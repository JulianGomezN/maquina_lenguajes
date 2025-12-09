from machine.Memory.Memory import Memory
import logging
import struct

logger = logging.getLogger("compiler.loader")


class Loader :

    def __init__(self, memory: Memory, *, debug: bool = False, init_data_on_load: bool = True):
        self.memory = memory
        self.debug = debug
        self.init_data_on_load = init_data_on_load
        # one-time header printed for loader table output
        self._loader_header_printed = False

    def _get_absolute_code(self, code: str, start_address: int):
        """
            Retorna el codigo absoluto para cargarlo en memoria
            
            Args:
                code: Código fuente a cargar
            
            Returns:
                codigo en absoluto numerico
            """

        lines = code.split('\n')
        out = []
        data_entries = []
        for line in lines:
            if not line:
                continue
            # Collect assembler-emitted .DATA directives (extended format):
            # .DATA <address_hex> <size_dec> <bytes_hex> [; NAME=<symbol>] [; RELOCS=off:size:sym,...]
            if line.upper().startswith('.DATA'):
                # split by whitespace first 4 tokens, then optional semicolon fields
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    addr = int(parts[1], 16)
                    size = int(parts[2])
                    # bytes field may be followed by comment/fields after whitespace
                    rest = parts[3].strip()
                    # if there is a semicolon, the first token is bytes, rest are metadata
                    if ';' in rest:
                        bytes_hex, meta = rest.split(';', 1)
                        bytes_hex = bytes_hex.strip()
                        meta = meta.strip()
                    else:
                        bytes_hex = rest.split()[0]
                        meta = ''

                    name = None
                    relocs = []
                    if meta:
                        # meta fields separated by ';'
                        for field in meta.split(';'):
                            field = field.strip()
                            if not field:
                                continue
                            if field.upper().startswith('NAME='):
                                name = field.split('=',1)[1]
                            elif field.upper().startswith('RELOCS='):
                                reloc_list = field.split('=',1)[1]
                                if reloc_list:
                                    for r in reloc_list.split(','):
                                        r = r.strip()
                                        if not r:
                                            continue
                                        # expected format off:size:sym
                                        try:
                                            off_s, size_s, sym = r.split(':',2)
                                            relocs.append({'offset':int(off_s),'size':int(size_s),'symbol':sym})
                                        except Exception:
                                            logger.warning("loader: malformed reloc entry '%s'", r)

                    data_entries.append({'addr':addr, 'size':size, 'bytes_hex':bytes_hex, 'name':name, 'relocs':relocs, 'local': False})
                continue
            # Collect .LOCAL_REL metadata (BP-relative offsets) emitted by code generator
            if line.upper().startswith('.LOCAL_REL'):
                parts = line.split(None, 4)
                # Format: .LOCAL_REL <offset> <size_dec> <name> ; FUNC=...
                if len(parts) >= 4:
                    try:
                        # allow decimal or hex offset (base 0)
                        rel = int(parts[1], 0)
                        size = int(parts[2])
                        name = parts[3]
                        func = None
                        # If there is trailing metadata after a semicolon, parse FUNC=
                        if ';' in line:
                            tail = line.split(';',1)[1]
                            for field in tail.split(';'):
                                field = field.strip()
                                if not field:
                                    continue
                                if field.upper().startswith('FUNC='):
                                    func = field.split('=',1)[1].strip()
                        # strip trailing metadata from name if present
                        if ';' in name:
                            name = name.split(';',1)[0].strip()
                        data_entries.append({'rel':rel, 'size':size, 'name':name, 'local': True, 'func': func})
                    except Exception:
                        logger.warning("loader: malformed .LOCAL_REL line '%s'", line)
                continue

            # Collect .LOCAL metadata emitted by code generator for locals/params (legacy absolute addresses)
            if line.upper().startswith('.LOCAL'):
                parts = line.split(None, 4)
                # Format: .LOCAL <addr_hex> <size_dec> <name> ; FUNC=...
                if len(parts) >= 4:
                    try:
                        addr = int(parts[1], 16)
                        size = int(parts[2])
                        name = parts[3]
                        # strip trailing metadata after semicolon if present
                        if ';' in name:
                            name = name.split(';',1)[0].strip()
                        data_entries.append({'addr':addr, 'size':size, 'name':name, 'local': True})
                    except Exception:
                        logger.warning("loader: malformed .LOCAL line '%s'", line)
                continue

            if line.startswith('['):
                temp = line.strip('[]')
                address = int(temp,16)
                address += start_address
                out.append(address)
            else:
                ins = int(line,16)
                out.append(ins)

        return out, data_entries

    
    def load_in_memory(self, rel_src : str, start_address : int):
        """
        Carga el código en memoria y retorna información de carga.
        
        Args:
            rel_src: Código fuente relocatable
            start_address: Dirección inicial donde cargar
            
        Returns:
            tuple: (codigo_absoluto_str, end_address)
                - codigo_absoluto_str: Código en formato absoluto
                - end_address: Dirección final (start_address + tamaño)
        """
        program, data_entries = self._get_absolute_code(rel_src,start_address)

        address = start_address
        absoluto = ""

        for ins in program:
            self.memory.write(address, ins, 8)
            absoluto += f"{ins:016X}\n"
            address += 8

        # Apply .DATA entries (deterministic initialization at load-time)
        if self.init_data_on_load and data_entries:
            for entry in data_entries:
                addr = entry.get('addr', None)
                try:
                    # If this is a local/parameter metadata entry, register symbol only
                    if entry.get('local'):
                        # If loader received a BP-relative local ('rel' present), register as relative
                        if entry.get('name') and hasattr(self.memory, 'register_symbol'):
                            try:
                                if 'rel' in entry:
                                    rel = entry.get('rel')
                                    # compute an assumed absolute address using the same
                                    # initial BP that the code generator used (0x1C000 + 16)
                                    assumed_bp = 0x1C000 + 16
                                    assumed_addr = assumed_bp + rel
                                    meta = {'local_rel': rel, 'assumed_addr': assumed_addr}
                                    if entry.get('func'):
                                        meta['func'] = entry.get('func')
                                    registered = self.memory.register_symbol(entry.get('name'), None, entry.get('size'), meta=meta)
                                    if registered:
                                        if not self._loader_header_printed:
                                            logger.info("LOADER  %-15s %-12s %-20s %-6s %-34s %-12s", 'Event', 'Name', 'Addr', 'Size', 'Hex', 'Init')
                                            self._loader_header_printed = True
                                        # show both the BP-relative and the assumed absolute address
                                        logger.info("LOADER  %-15s %-12s %-20s %-6d %-34s %-12s", 'REGISTER_LOCAL', entry.get('name'), f"(BP{rel:+d})={assumed_addr:#010x}", entry.get('size'), '-', '-')
                                else:
                                    # legacy absolute local entry
                                    registered = self.memory.register_symbol(entry.get('name'), addr, entry.get('size'), meta=None)
                                    if registered:
                                        if not self._loader_header_printed:
                                            logger.info("LOADER  %-15s %-12s %-12s %-6s %-34s %-12s", 'Event', 'Name', 'Addr', 'Size', 'Hex', 'Init')
                                            self._loader_header_printed = True
                                        logger.info("LOADER  %-15s %-12s %-12s %-6d %-34s %-12s", 'REGISTER_LOCAL', entry.get('name'), f"{addr:#010x}", entry.get('size'), '-', '-')
                            except Exception:
                                logger.exception("failed to register local symbol %s @0x%08X", entry.get('name'), addr)
                        continue

                    # Otherwise treat as .DATA bytes to load
                    data = bytes.fromhex(entry.get('bytes_hex',''))
                    # write raw bytes to memory at addr
                    self.memory.load_bytes(addr, data)
                    # produce an interpreted initializer representation for the loader
                    init_repr = None
                    try:
                        if len(data) in (4, 8):
                            # try float/double
                            if len(data) == 4:
                                f = struct.unpack('<f', data)[0]
                                init_repr = f"{f}"
                            else:
                                d = struct.unpack('<d', data)[0]
                                init_repr = f"{d}"
                    except Exception:
                        init_repr = None

                    # print header once before first INIT_DATA row (if not already printed by REGISTER_LOCAL)
                    if not self._loader_header_printed:
                        logger.info("LOADER  %-15s %-12s %-12s %-6s %-34s %-12s", 'Event', 'Name', 'Addr', 'Size', 'Hex', 'Init')
                        self._loader_header_printed = True

                    # Log only when moving variables/data to memory (info level), formatted as table
                    payload = data.hex()
                    # truncate payload display to keep column widths reasonable
                    payload_disp = payload if len(payload) <= 32 else payload[:32] + '...'
                    init_field = init_repr if init_repr is not None else '-'
                    if entry.get('name'):
                        logger.info("LOADER  %-15s %-12s %-12s %-6d %-34s %-12s", 'INIT_DATA', entry.get('name'), f"{addr:#010x}", len(data), payload_disp, init_field)
                    else:
                        logger.info("LOADER  %-15s %-12s %-12s %-6d %-34s %-12s", 'INIT_DATA', '', f"{addr:#010x}", len(data), payload_disp, init_field)
                    # TODO: handle relocation entries when linking multiple modules
                    if entry.get('relocs'):
                        logger.info(f"event=INIT_DATA_RELOCS addr={addr:#010x} relocs={entry.get('relocs')}")
                    # register symbol name in memory symbol table for runtime lookup
                    if entry.get('name') and hasattr(self.memory, 'register_symbol'):
                        try:
                            # build metadata including init bytes and interpreted initializer
                            meta = {'init_bytes': data.hex()}
                            if init_repr is not None:
                                meta['init_repr'] = init_repr
                            registered = self.memory.register_symbol(entry.get('name'), addr, len(data), meta=meta)
                            if registered:
                                # already logged INIT_DATA row above; nothing else to print here
                                pass
                        except Exception:
                            logger.exception("failed to register symbol %s @0x%08X", entry.get('name'), addr)
                except Exception:
                    if addr is not None:
                        logger.exception("failed to write .DATA @0x%08X", addr)
                    else:
                        logger.exception("failed to process data entry %s", entry)

            # leave a blank info line between loader output and later CPU/store logs
            if data_entries:
                logger.info("")

        return absoluto, address

    # Heuristic-based init removed. Loader uses explicit .DATA directives.
        
# -----------------------------
# Prueba (Powershell)
# cat {codigo relativo path} | python -m compiler.ensamblador | python -m compiler.loader
# -----------------------------
if __name__ == '__main__':
    import sys
    relativo = sys.stdin.read()

    loader = Loader(None)

    absoluto = loader._get_absolute_code(relativo,0)

    for i in absoluto:
        print(f"{i:016X}")