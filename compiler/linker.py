"""
Enlazador-Cargador (Linker-Loader) usando PLY Lex
Maneja archivos objeto, resolución de símbolos, reubicación y carga en memoria
"""

import ply.lex as lex
import re
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path


class ObjectFileParser:
    """Parser de archivos objeto usando PLY Lex"""
    
    # Tokens para el formato de archivo objeto
    tokens = (
        'SECTION_HEADER',   # .text, .data, .bss, .symtab, .reltab
        'SYMBOL_DEF',       # SYMBOL nombre tipo direccion
        'RELOC_ENTRY',      # RELOC tipo direccion simbolo
        'DATA_BYTE',        # Dato en formato hexadecimal
        'LABEL',            # Etiqueta
        'NUMBER',           # Número decimal o hexadecimal
        'STRING',           # Cadena entre comillas
        'COMMA',            # Separador
        'COLON',            # :
        'EQUALS',           # =
        'IDENTIFIER',       # Identificador genérico
    )
    
    # Ignorar espacios y tabs
    t_ignore = ' \t'
    
    # Tokens simples
    t_COMMA = r','
    t_COLON = r':'
    t_EQUALS = r'='
    
    def t_SECTION_HEADER(self, t):
        r'\.(?:text|data|bss|symtab|reltab|strtab)'
        return t
    
    def t_SYMBOL_DEF(self, t):
        r'SYMBOL'
        return t
    
    def t_RELOC_ENTRY(self, t):
        r'RELOC'
        return t
    
    def t_NUMBER(self, t):
        r'0x[0-9A-Fa-f]+|[0-9]+'
        if t.value.startswith('0x'):
            t.value = int(t.value, 16)
        else:
            t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        r'"[^"]*"'
        t.value = t.value[1:-1]  # Remover comillas
        return t
    
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_COMMENT(self, t):
        r';.*'
        pass  # Ignorar comentarios
    
    def t_error(self, t):
        print(f"Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)
    
    def __init__(self):
        self.lexer = lex.lex(module=self)
    
    def tokenize(self, data):
        """Tokeniza el contenido de un archivo objeto"""
        self.lexer.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens


class Symbol:
    """Representa un símbolo en la tabla de símbolos"""
    
    def __init__(self, name: str, value: int, section: str, 
                 binding: str = 'LOCAL', symbol_type: str = 'NOTYPE'):
        self.name = name
        self.value = value  # Dirección o valor
        self.section = section  # .text, .data, .bss, ABS, UNDEF
        self.binding = binding  # LOCAL, GLOBAL, EXTERN
        self.symbol_type = symbol_type  # NOTYPE, FUNC, OBJECT
        self.size = 0
    
    def __repr__(self):
        return f"Symbol({self.name}, 0x{self.value:04x}, {self.section}, {self.binding})"


class RelocationEntry:
    """Entrada de reubicación"""
    
    def __init__(self, offset: int, reloc_type: str, symbol_name: str, addend: int = 0):
        self.offset = offset  # Offset en la sección
        self.reloc_type = reloc_type  # ABSOLUTE, RELATIVE, etc.
        self.symbol_name = symbol_name
        self.addend = addend  # Valor a sumar
    
    def __repr__(self):
        return f"Reloc({self.reloc_type}, 0x{self.offset:04x}, {self.symbol_name})"


class ObjectFile:
    """Representa un archivo objeto completo"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.sections = {
            '.text': bytearray(),
            '.data': bytearray(),
            '.bss': bytearray(),
        }
        self.symbols = {}  # nombre -> Symbol
        self.relocations = {
            '.text': [],
            '.data': [],
        }
        self.section_sizes = {
            '.text': 0,
            '.data': 0,
            '.bss': 0,
        }
    
    def add_symbol(self, symbol: Symbol):
        """Agrega un símbolo a la tabla"""
        self.symbols[symbol.name] = symbol
    
    def add_relocation(self, section: str, reloc: RelocationEntry):
        """Agrega una entrada de reubicación"""
        if section in self.relocations:
            self.relocations[section].append(reloc)
    
    def get_global_symbols(self) -> Dict[str, Symbol]:
        """Obtiene todos los símbolos globales"""
        return {name: sym for name, sym in self.symbols.items() 
                if sym.binding == 'GLOBAL'}
    
    def get_undefined_symbols(self) -> Set[str]:
        """Obtiene símbolos no definidos (externos)"""
        return {name for name, sym in self.symbols.items() 
                if sym.section == 'UNDEF'}


class Linker:
    """Enlazador que combina múltiples archivos objeto"""
    
    def __init__(self):
        self.object_files: List[ObjectFile] = []
        self.global_symbols: Dict[str, Symbol] = {}
        self.section_offsets: Dict[str, Dict[str, int]] = {}  # file -> section -> offset
        self.linked_sections = {
            '.text': bytearray(),
            '.data': bytearray(),
            '.bss': bytearray(),
        }
        self.entry_point = 0
    
    def add_object_file(self, obj_file: ObjectFile):
        """Agrega un archivo objeto para enlazar"""
        self.object_files.append(obj_file)
    
    def link(self, output_file: Optional[str] = None) -> 'LinkedProgram':
        """
        Enlaza todos los archivos objeto
        
        Returns:
            LinkedProgram: Programa enlazado listo para cargar
        """
        print("=== INICIANDO ENLACE ===")
        
        # Paso 1: Calcular offsets de secciones
        self._calculate_section_offsets()
        
        # Paso 2: Resolver símbolos globales
        self._resolve_global_symbols()
        
        # Paso 3: Combinar secciones
        self._combine_sections()
        
        # Paso 4: Aplicar reubicaciones
        self._apply_relocations()
        
        # Paso 5: Verificar símbolos indefinidos
        undefined = self._check_undefined_symbols()
        if undefined:
            raise LinkError(f"Símbolos indefinidos: {', '.join(undefined)}")
        
        print("=== ENLACE COMPLETADO ===")
        
        # Crear programa enlazado
        linked_program = LinkedProgram(
            text_section=bytes(self.linked_sections['.text']),
            data_section=bytes(self.linked_sections['.data']),
            bss_size=len(self.linked_sections['.bss']),
            entry_point=self.entry_point,
            symbols=self.global_symbols
        )
        
        # Guardar si se especifica archivo de salida
        if output_file:
            linked_program.save(output_file)
        
        return linked_program
    
    def _calculate_section_offsets(self):
        """Calcula los offsets de cada sección para cada archivo"""
        print("\n--- Calculando offsets de secciones ---")
        
        current_offsets = {'.text': 0, '.data': 0, '.bss': 0}
        
        for obj_file in self.object_files:
            self.section_offsets[obj_file.filename] = {}
            
            for section in ['.text', '.data', '.bss']:
                # Guardar offset actual para este archivo/sección
                self.section_offsets[obj_file.filename][section] = current_offsets[section]
                
                # Incrementar offset para próximo archivo
                section_size = obj_file.section_sizes[section]
                current_offsets[section] += section_size
                
                print(f"  {obj_file.filename}:{section} -> offset 0x{self.section_offsets[obj_file.filename][section]:04x}, size {section_size}")
    
    def _resolve_global_symbols(self):
        """Resuelve símbolos globales entre archivos"""
        print("\n--- Resolviendo símbolos globales ---")
        
        for obj_file in self.object_files:
            file_offset = self.section_offsets[obj_file.filename]
            
            for name, symbol in obj_file.symbols.items():
                if symbol.binding == 'GLOBAL':
                    # Ajustar valor del símbolo con el offset de su sección
                    if symbol.section in file_offset:
                        adjusted_value = symbol.value + file_offset[symbol.section]
                        
                        # Verificar redefiniciones
                        if name in self.global_symbols:
                            existing = self.global_symbols[name]
                            if existing.section != 'UNDEF':
                                raise LinkError(f"Símbolo '{name}' definido múltiples veces")
                        
                        # Crear símbolo global ajustado
                        global_sym = Symbol(
                            name=name,
                            value=adjusted_value,
                            section=symbol.section,
                            binding='GLOBAL',
                            symbol_type=symbol.symbol_type
                        )
                        self.global_symbols[name] = global_sym
                        print(f"  {name}: 0x{adjusted_value:04x} ({symbol.section})")
                    
                    # Detectar punto de entrada
                    if name == '_start' or name == 'main':
                        self.entry_point = self.global_symbols[name].value
    
    def _combine_sections(self):
        """Combina secciones de todos los archivos objeto"""
        print("\n--- Combinando secciones ---")
        
        for obj_file in self.object_files:
            for section in ['.text', '.data']:
                if section in obj_file.sections:
                    section_data = obj_file.sections[section]
                    self.linked_sections[section].extend(section_data)
                    print(f"  {obj_file.filename}:{section} -> {len(section_data)} bytes")
            
            # .bss solo necesita tamaño, no datos
            bss_size = obj_file.section_sizes.get('.bss', 0)
            self.linked_sections['.bss'].extend(bytearray(bss_size))
    
    def _apply_relocations(self):
        """Aplica todas las entradas de reubicación"""
        print("\n--- Aplicando reubicaciones ---")
        
        for obj_file in self.object_files:
            file_offset = self.section_offsets[obj_file.filename]
            
            for section, relocs in obj_file.relocations.items():
                for reloc in relocs:
                    # Obtener símbolo referenciado
                    if reloc.symbol_name not in self.global_symbols:
                        # Buscar en símbolos locales del archivo
                        if reloc.symbol_name in obj_file.symbols:
                            local_sym = obj_file.symbols[reloc.symbol_name]
                            if local_sym.section in file_offset:
                                symbol_value = local_sym.value + file_offset[local_sym.section]
                            else:
                                raise LinkError(f"Símbolo '{reloc.symbol_name}' en sección desconocida")
                        else:
                            raise LinkError(f"Símbolo '{reloc.symbol_name}' no encontrado")
                    else:
                        symbol_value = self.global_symbols[reloc.symbol_name].value
                    
                    # Calcular dirección a parchear
                    patch_address = file_offset[section] + reloc.offset
                    
                    # Aplicar reubicación según tipo
                    self._patch_relocation(
                        section, 
                        patch_address, 
                        symbol_value, 
                        reloc.reloc_type,
                        reloc.addend
                    )
                    
                    print(f"  {reloc.reloc_type} @ 0x{patch_address:04x} -> {reloc.symbol_name} (0x{symbol_value:04x})")
    
    def _patch_relocation(self, section: str, offset: int, value: int, 
                          reloc_type: str, addend: int):
        """Parchea una ubicación con valor reubicado"""
        section_data = self.linked_sections[section]
        
        if reloc_type == 'ABSOLUTE':
            # Dirección absoluta (reemplazar completamente)
            final_value = value + addend
            # Asumir 8 bytes para instrucciones
            for i in range(8):
                if offset + i < len(section_data):
                    section_data[offset + i] = (final_value >> (i * 8)) & 0xFF
        
        elif reloc_type == 'RELATIVE':
            # Dirección relativa (PC-relative)
            final_value = (value + addend) - (offset + 8)  # 8 = tamaño instrucción
            for i in range(8):
                if offset + i < len(section_data):
                    section_data[offset + i] = (final_value >> (i * 8)) & 0xFF
        
        elif reloc_type == 'IMMEDIATE':
            # Valor inmediato en instrucción (últimos 44 bits)
            if offset + 7 < len(section_data):
                # Leer instrucción actual
                instruction = 0
                for i in range(8):
                    instruction |= section_data[offset + i] << (i * 8)
                
                # Preservar opcode (bits 48-63), reemplazar inmediato (bits 0-43)
                opcode = instruction & 0xFFFF000000000000
                immediate = (value + addend) & 0xFFFFFFFFFFF
                new_instruction = opcode | immediate
                
                # Escribir instrucción modificada
                for i in range(8):
                    section_data[offset + i] = (new_instruction >> (i * 8)) & 0xFF
    
    def _check_undefined_symbols(self) -> Set[str]:
        """Verifica si quedan símbolos sin definir"""
        undefined = set()
        
        for obj_file in self.object_files:
            for name, symbol in obj_file.symbols.items():
                if symbol.section == 'UNDEF' and name not in self.global_symbols:
                    undefined.add(name)
        
        return undefined
    
    def print_symbol_table(self):
        """Imprime la tabla de símbolos global"""
        print("\n=== TABLA DE SÍMBOLOS GLOBAL ===")
        print(f"{'Nombre':<20} {'Valor':<12} {'Sección':<10} {'Tipo':<10}")
        print("-" * 60)
        
        for name, symbol in sorted(self.global_symbols.items()):
            print(f"{name:<20} 0x{symbol.value:08x}   {symbol.section:<10} {symbol.symbol_type:<10}")


class LinkedProgram:
    """Programa enlazado listo para cargar"""
    
    def __init__(self, text_section: bytes, data_section: bytes, 
                 bss_size: int, entry_point: int, symbols: Dict[str, Symbol]):
        self.text_section = text_section
        self.data_section = data_section
        self.bss_size = bss_size
        self.entry_point = entry_point
        self.symbols = symbols
    
    def save(self, filename: str):
        """Guarda el programa enlazado en formato binario"""
        with open(filename, 'wb') as f:
            # Header
            f.write(b'HEXACORE')  # Magic number
            f.write(self.entry_point.to_bytes(8, 'little'))
            f.write(len(self.text_section).to_bytes(4, 'little'))
            f.write(len(self.data_section).to_bytes(4, 'little'))
            f.write(self.bss_size.to_bytes(4, 'little'))
            
            # Secciones
            f.write(self.text_section)
            f.write(self.data_section)
        
        print(f"\nPrograma enlazado guardado en: {filename}")
    
    def load(self, filename: str):
        """Carga un programa enlazado desde archivo"""
        with open(filename, 'rb') as f:
            # Verificar magic number
            magic = f.read(8)
            if magic != b'HEXACORE':
                raise ValueError("Archivo no es un ejecutable HEXACORE válido")
            
            # Leer header
            self.entry_point = int.from_bytes(f.read(8), 'little')
            text_size = int.from_bytes(f.read(4), 'little')
            data_size = int.from_bytes(f.read(4), 'little')
            self.bss_size = int.from_bytes(f.read(4), 'little')
            
            # Leer secciones
            self.text_section = f.read(text_size)
            self.data_section = f.read(data_size)
        
        print(f"Programa cargado desde: {filename}")
        print(f"  Punto de entrada: 0x{self.entry_point:04x}")
        print(f"  Tamaño .text: {text_size} bytes")
        print(f"  Tamaño .data: {data_size} bytes")
        print(f"  Tamaño .bss: {self.bss_size} bytes")
    
    def get_instructions(self) -> List[int]:
        """Convierte la sección de texto en lista de instrucciones"""
        instructions = []
        for i in range(0, len(self.text_section), 8):
            if i + 8 <= len(self.text_section):
                instr_bytes = self.text_section[i:i+8]
                instruction = int.from_bytes(instr_bytes, 'little')
                instructions.append(instruction)
        return instructions


class Loader:
    """Cargador mejorado que usa programas enlazados"""
    
    def __init__(self, memory_system):
        self.memory = memory_system
        self.loaded_programs = {}
        self.next_free_address = 0
    
    def load_linked_program(self, linked_program: LinkedProgram, 
                           start_address: Optional[int] = None,
                           program_name: str = "default") -> Dict:
        """
        Carga un programa enlazado en memoria
        
        Args:
            linked_program: Programa enlazado
            start_address: Dirección de carga (None = automática)
            program_name: Nombre del programa
            
        Returns:
            dict: Información del programa cargado
        """
        print(f"\n=== CARGANDO PROGRAMA: {program_name} ===")
        
        # Calcular tamaño total
        total_size = len(linked_program.text_section) + \
                     len(linked_program.data_section) + \
                     linked_program.bss_size
        
        # Determinar dirección de carga
        if start_address is None:
            start_address = self.next_free_address
        
        # Verificar espacio
        if not self._check_memory_space(start_address, total_size):
            raise MemoryError(f"No hay espacio suficiente en memoria")
        
        # Calcular offsets de secciones
        text_offset = start_address
        data_offset = text_offset + len(linked_program.text_section)
        bss_offset = data_offset + len(linked_program.data_section)
        
        # Cargar .text
        self._write_to_memory(text_offset, linked_program.text_section)
        print(f"  .text cargado en 0x{text_offset:04x} ({len(linked_program.text_section)} bytes)")
        
        # Cargar .data
        self._write_to_memory(data_offset, linked_program.data_section)
        print(f"  .data cargado en 0x{data_offset:04x} ({len(linked_program.data_section)} bytes)")
        
        # Inicializar .bss (todo en ceros)
        self._clear_memory_region(bss_offset, linked_program.bss_size)
        print(f"  .bss inicializado en 0x{bss_offset:04x} ({linked_program.bss_size} bytes)")
        
        # Calcular punto de entrada ajustado
        entry_point = start_address + linked_program.entry_point
        
        # Registrar programa
        program_info = {
            'name': program_name,
            'start_address': start_address,
            'entry_point': entry_point,
            'text_section': {'offset': text_offset, 'size': len(linked_program.text_section)},
            'data_section': {'offset': data_offset, 'size': len(linked_program.data_section)},
            'bss_section': {'offset': bss_offset, 'size': linked_program.bss_size},
            'total_size': total_size
        }
        
        self.loaded_programs[program_name] = program_info
        self.next_free_address = start_address + total_size
        
        print(f"  Punto de entrada: 0x{entry_point:04x}")
        print(f"  Tamaño total: {total_size} bytes")
        
        return program_info
    
    def _write_to_memory(self, address: int, data: bytes):
        """Escribe datos en memoria"""
        if hasattr(self.memory, 'memory'):
            for i, byte_val in enumerate(data):
                if address + i < len(self.memory.memory):
                    self.memory.memory[address + i] = byte_val
    
    def _clear_memory_region(self, address: int, size: int):
        """Limpia una región de memoria"""
        if hasattr(self.memory, 'memory'):
            for i in range(size):
                if address + i < len(self.memory.memory):
                    self.memory.memory[address + i] = 0
    
    def _check_memory_space(self, start_address: int, size: int) -> bool:
        """Verifica si hay espacio disponible"""
        end_address = start_address + size
        memory_size = len(self.memory.memory) if hasattr(self.memory, 'memory') else 4096 * 8
        return end_address <= memory_size
    
    def unload_program(self, program_name: str) -> bool:
        """Descarga un programa de memoria"""
        if program_name not in self.loaded_programs:
            return False
        
        program_info = self.loaded_programs[program_name]
        self._clear_memory_region(
            program_info['start_address'], 
            program_info['total_size']
        )
        
        del self.loaded_programs[program_name]
        print(f"Programa '{program_name}' descargado")
        return True
    
    def get_program_info(self, program_name: str) -> Optional[Dict]:
        """Obtiene información de un programa cargado"""
        return self.loaded_programs.get(program_name)
    
    def print_memory_map(self):
        """Imprime el mapa de memoria"""
        print("\n=== MAPA DE MEMORIA ===")
        memory_size = len(self.memory.memory) if hasattr(self.memory, 'memory') else 4096 * 8
        
        print(f"Memoria total: {memory_size} bytes")
        print(f"Memoria usada: {self.next_free_address} bytes")
        print(f"Memoria libre: {memory_size - self.next_free_address} bytes")
        print(f"\nProgramas cargados: {len(self.loaded_programs)}")
        
        for name, info in self.loaded_programs.items():
            print(f"\n{name}:")
            print(f"  Rango: 0x{info['start_address']:04x} - 0x{info['start_address'] + info['total_size']:04x}")
            print(f"  Punto de entrada: 0x{info['entry_point']:04x}")
            print(f"  .text: 0x{info['text_section']['offset']:04x} ({info['text_section']['size']} bytes)")
            print(f"  .data: 0x{info['data_section']['offset']:04x} ({info['data_section']['size']} bytes)")
            print(f"  .bss:  0x{info['bss_section']['offset']:04x} ({info['bss_section']['size']} bytes)")


class LinkError(Exception):
    """Excepción para errores de enlace"""
    pass


# Ejemplo de uso
if __name__ == "__main__":
    print("=== DEMOSTRACIÓN DEL ENLAZADOR-CARGADOR ===\n")
    
    # Crear archivos objeto de ejemplo
    obj1 = ObjectFile("module1.o")
    obj1.section_sizes['.text'] = 24
    obj1.sections['.text'] = bytearray(b'\x00' * 24)
    obj1.add_symbol(Symbol("_start", 0, '.text', 'GLOBAL', 'FUNC'))
    obj1.add_symbol(Symbol("func1", 8, '.text', 'GLOBAL', 'FUNC'))
    
    obj2 = ObjectFile("module2.o")
    obj2.section_sizes['.text'] = 16
    obj2.sections['.text'] = bytearray(b'\x00' * 16)
    obj2.add_symbol(Symbol("func2", 0, '.text', 'GLOBAL', 'FUNC'))
    obj2.add_symbol(Symbol("func1", 0, 'UNDEF', 'GLOBAL'))  # Referencia externa
    
    # Crear enlazador
    linker = Linker()
    linker.add_object_file(obj1)
    linker.add_object_file(obj2)
    
    try:
        # Enlazar
        linked = linker.link()
        
        # Mostrar tabla de símbolos
        linker.print_symbol_table()
        
        # Guardar ejecutable
        linked.save("program.exe")
        
        # Simular carga en memoria
        class SimpleMemory:
            def __init__(self):
                self.memory = [0] * 4096
        
        memory = SimpleMemory()
        loader = Loader(memory)
        
        info = loader.load_linked_program(linked, program_name="test_program")
        loader.print_memory_map()
        
    except LinkError as e:
        print(f"ERROR DE ENLACE: {e}")
