"""
Generador de Archivos Objeto
Convierte código ensamblado en archivos objeto (.o) con símbolos y reubicaciones
"""

from typing import List, Dict, Tuple, Optional, Set
from compiler.linker import ObjectFile, Symbol, RelocationEntry
import struct


class ObjectFileGenerator:
    """Genera archivos objeto desde código ensamblado"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.obj_file = ObjectFile(module_name)
        self.current_section = '.text'
        self.section_positions = {
            '.text': 0,
            '.data': 0,
            '.bss': 0,
        }
        self.labels = {}  # label -> (section, offset)
        self.external_refs = set()  # Símbolos externos referenciados
        self.global_symbols = set()  # Símbolos declarados como globales
        
    def set_section(self, section: str):
        """Cambia la sección actual"""
        if section not in ['.text', '.data', '.bss']:
            raise ValueError(f"Sección inválida: {section}")
        self.current_section = section
    
    def add_label(self, label: str, is_global: bool = False):
        """
        Agrega una etiqueta en la posición actual
        
        Args:
            label: Nombre de la etiqueta
            is_global: Si es un símbolo global
        """
        offset = self.section_positions[self.current_section]
        self.labels[label] = (self.current_section, offset)
        
        if is_global:
            self.global_symbols.add(label)
    
    def add_instruction(self, instruction: int):
        """
        Agrega una instrucción a la sección actual
        
        Args:
            instruction: Instrucción en formato de 64 bits
        """
        if self.current_section == '.bss':
            raise ValueError("No se pueden agregar instrucciones a .bss")
        
        # Convertir instrucción a bytes (little endian)
        instr_bytes = instruction.to_bytes(8, 'little')
        
        # Agregar a la sección
        self.obj_file.sections[self.current_section].extend(instr_bytes)
        
        # Actualizar posición
        self.section_positions[self.current_section] += 8
    
    def add_data(self, data: bytes):
        """
        Agrega datos a la sección .data
        
        Args:
            data: Bytes a agregar
        """
        if self.current_section != '.data':
            raise ValueError("Solo se pueden agregar datos a .data")
        
        self.obj_file.sections['.data'].extend(data)
        self.section_positions['.data'] += len(data)
    
    def reserve_bss(self, size: int):
        """
        Reserva espacio en .bss
        
        Args:
            size: Tamaño a reservar en bytes
        """
        if self.current_section != '.bss':
            raise ValueError("Solo se puede reservar espacio en .bss")
        
        self.section_positions['.bss'] += size
    
    def add_external_reference(self, symbol_name: str):
        """
        Marca un símbolo como referencia externa
        
        Args:
            symbol_name: Nombre del símbolo externo
        """
        self.external_refs.add(symbol_name)
    
    def add_relocation(self, reloc_type: str, symbol_name: str, addend: int = 0):
        """
        Agrega una entrada de reubicación en la posición actual
        
        Args:
            reloc_type: Tipo de reubicación (ABSOLUTE, RELATIVE, IMMEDIATE)
            symbol_name: Símbolo a reubicar
            addend: Valor a sumar
        """
        # La reubicación se aplica a la última instrucción agregada
        offset = self.section_positions[self.current_section] - 8
        
        reloc = RelocationEntry(
            offset=offset,
            reloc_type=reloc_type,
            symbol_name=symbol_name,
            addend=addend
        )
        
        self.obj_file.add_relocation(self.current_section, reloc)
    
    def finalize(self) -> ObjectFile:
        """
        Finaliza la generación del archivo objeto
        
        Returns:
            ObjectFile: Archivo objeto completado
        """
        # Actualizar tamaños de secciones
        self.obj_file.section_sizes['.text'] = len(self.obj_file.sections['.text'])
        self.obj_file.section_sizes['.data'] = len(self.obj_file.sections['.data'])
        self.obj_file.section_sizes['.bss'] = self.section_positions['.bss']
        
        # Agregar símbolos de etiquetas
        for label, (section, offset) in self.labels.items():
            binding = 'GLOBAL' if label in self.global_symbols else 'LOCAL'
            symbol = Symbol(
                name=label,
                value=offset,
                section=section,
                binding=binding,
                symbol_type='FUNC' if section == '.text' else 'OBJECT'
            )
            self.obj_file.add_symbol(symbol)
        
        # Agregar símbolos externos (indefinidos)
        for ext_symbol in self.external_refs:
            if ext_symbol not in self.labels:  # Solo si no está definido localmente
                symbol = Symbol(
                    name=ext_symbol,
                    value=0,
                    section='UNDEF',
                    binding='GLOBAL',
                    symbol_type='NOTYPE'
                )
                self.obj_file.add_symbol(symbol)
        
        return self.obj_file
    
    def save_to_file(self, filename: str):
        """
        Guarda el archivo objeto en formato texto
        
        Args:
            filename: Nombre del archivo de salida
        """
        obj_file = self.finalize()
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"; Archivo objeto: {self.module_name}\n")
            f.write(f"; Generado por Object File Generator\n\n")
            
            # Sección .text
            f.write(".text\n")
            f.write(f"; Tamaño: {obj_file.section_sizes['.text']} bytes\n")
            text_data = obj_file.sections['.text']
            for i in range(0, len(text_data), 8):
                if i + 8 <= len(text_data):
                    instr = int.from_bytes(text_data[i:i+8], 'little')
                    f.write(f"  0x{i:04x}: 0x{instr:016x}\n")
            f.write("\n")
            
            # Sección .data
            f.write(".data\n")
            f.write(f"; Tamaño: {obj_file.section_sizes['.data']} bytes\n")
            data_section = obj_file.sections['.data']
            for i in range(0, len(data_section), 16):
                chunk = data_section[i:min(i+16, len(data_section))]
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                f.write(f"  0x{i:04x}: {hex_str}\n")
            f.write("\n")
            
            # Sección .bss
            f.write(".bss\n")
            f.write(f"; Tamaño: {obj_file.section_sizes['.bss']} bytes\n\n")
            
            # Tabla de símbolos
            f.write(".symtab\n")
            f.write(f"; {'Nombre':<20} {'Valor':<12} {'Sección':<10} {'Binding':<10} {'Tipo':<10}\n")
            for name, symbol in sorted(obj_file.symbols.items()):
                f.write(f"SYMBOL {name:<20} 0x{symbol.value:08x} {symbol.section:<10} {symbol.binding:<10} {symbol.symbol_type:<10}\n")
            f.write("\n")
            
            # Tabla de reubicaciones
            f.write(".reltab\n")
            for section, relocs in obj_file.relocations.items():
                if relocs:
                    f.write(f"; Reubicaciones para {section}\n")
                    for reloc in relocs:
                        f.write(f"RELOC {reloc.reloc_type:<12} 0x{reloc.offset:04x} {reloc.symbol_name:<20} {reloc.addend}\n")
            
        print(f"Archivo objeto guardado: {filename}")
    
    def save_binary(self, filename: str):
        """
        Guarda el archivo objeto en formato binario
        
        Args:
            filename: Nombre del archivo de salida (.o)
        """
        obj_file = self.finalize()
        
        with open(filename, 'wb') as f:
            # Magic number
            f.write(b'HEXAOBJ\x00')  # 8 bytes
            
            # Tamaños de secciones
            f.write(struct.pack('<I', obj_file.section_sizes['.text']))
            f.write(struct.pack('<I', obj_file.section_sizes['.data']))
            f.write(struct.pack('<I', obj_file.section_sizes['.bss']))
            
            # Número de símbolos y reubicaciones
            f.write(struct.pack('<I', len(obj_file.symbols)))
            reloc_count = sum(len(relocs) for relocs in obj_file.relocations.values())
            f.write(struct.pack('<I', reloc_count))
            
            # Secciones
            f.write(bytes(obj_file.sections['.text']))
            f.write(bytes(obj_file.sections['.data']))
            
            # Tabla de símbolos
            for name, symbol in obj_file.symbols.items():
                # Nombre (null-terminated, max 64 bytes)
                name_bytes = name.encode('utf-8')[:63] + b'\x00'
                name_bytes = name_bytes.ljust(64, b'\x00')
                f.write(name_bytes)
                
                # Valor
                f.write(struct.pack('<Q', symbol.value))
                
                # Sección (como índice: .text=0, .data=1, .bss=2, UNDEF=3)
                section_map = {'.text': 0, '.data': 1, '.bss': 2, 'UNDEF': 3}
                section_idx = section_map.get(symbol.section, 3)
                f.write(struct.pack('<B', section_idx))
                
                # Binding (LOCAL=0, GLOBAL=1)
                binding_idx = 1 if symbol.binding == 'GLOBAL' else 0
                f.write(struct.pack('<B', binding_idx))
                
                # Tipo (NOTYPE=0, FUNC=1, OBJECT=2)
                type_map = {'NOTYPE': 0, 'FUNC': 1, 'OBJECT': 2}
                type_idx = type_map.get(symbol.symbol_type, 0)
                f.write(struct.pack('<B', type_idx))
                
                # Padding
                f.write(b'\x00' * 5)
            
            # Tabla de reubicaciones
            for section, relocs in obj_file.relocations.items():
                section_idx = {'..text': 0, '.data': 1}.get(section, 0)
                
                for reloc in relocs:
                    # Sección
                    f.write(struct.pack('<B', section_idx))
                    
                    # Tipo (ABSOLUTE=0, RELATIVE=1, IMMEDIATE=2)
                    type_map = {'ABSOLUTE': 0, 'RELATIVE': 1, 'IMMEDIATE': 2}
                    type_idx = type_map.get(reloc.reloc_type, 0)
                    f.write(struct.pack('<B', type_idx))
                    
                    # Padding
                    f.write(b'\x00' * 6)
                    
                    # Offset
                    f.write(struct.pack('<Q', reloc.offset))
                    
                    # Nombre del símbolo
                    symbol_name = reloc.symbol_name.encode('utf-8')[:63] + b'\x00'
                    symbol_name = symbol_name.ljust(64, b'\x00')
                    f.write(symbol_name)
                    
                    # Addend
                    f.write(struct.pack('<q', reloc.addend))  # signed
        
        print(f"Archivo objeto binario guardado: {filename}")


class ObjectFileReader:
    """Lee archivos objeto en formato binario"""
    
    @staticmethod
    def read_binary(filename: str) -> ObjectFile:
        """
        Lee un archivo objeto binario
        
        Args:
            filename: Archivo a leer
            
        Returns:
            ObjectFile: Archivo objeto cargado
        """
        with open(filename, 'rb') as f:
            # Verificar magic number
            magic = f.read(8)
            if magic != b'HEXAOBJ\x00':
                raise ValueError(f"Archivo {filename} no es un archivo objeto válido")
            
            # Leer tamaños
            text_size = struct.unpack('<I', f.read(4))[0]
            data_size = struct.unpack('<I', f.read(4))[0]
            bss_size = struct.unpack('<I', f.read(4))[0]
            symbol_count = struct.unpack('<I', f.read(4))[0]
            reloc_count = struct.unpack('<I', f.read(4))[0]
            
            # Crear archivo objeto
            obj_file = ObjectFile(filename)
            obj_file.section_sizes['.text'] = text_size
            obj_file.section_sizes['.data'] = data_size
            obj_file.section_sizes['.bss'] = bss_size
            
            # Leer secciones
            obj_file.sections['.text'] = bytearray(f.read(text_size))
            obj_file.sections['.data'] = bytearray(f.read(data_size))
            obj_file.sections['.bss'] = bytearray(bss_size)  # Vacío, solo tamaño
            
            # Leer símbolos
            section_names = ['.text', '.data', '.bss', 'UNDEF']
            binding_names = ['LOCAL', 'GLOBAL']
            type_names = ['NOTYPE', 'FUNC', 'OBJECT']
            
            for _ in range(symbol_count):
                # Nombre
                name_bytes = f.read(64)
                name = name_bytes.rstrip(b'\x00').decode('utf-8')
                
                # Valor
                value = struct.unpack('<Q', f.read(8))[0]
                
                # Atributos
                section_idx = struct.unpack('<B', f.read(1))[0]
                binding_idx = struct.unpack('<B', f.read(1))[0]
                type_idx = struct.unpack('<B', f.read(1))[0]
                
                # Padding
                f.read(5)
                
                # Crear símbolo
                symbol = Symbol(
                    name=name,
                    value=value,
                    section=section_names[section_idx] if section_idx < len(section_names) else 'UNDEF',
                    binding=binding_names[binding_idx] if binding_idx < len(binding_names) else 'LOCAL',
                    symbol_type=type_names[type_idx] if type_idx < len(type_names) else 'NOTYPE'
                )
                obj_file.add_symbol(symbol)
            
            # Leer reubicaciones
            type_names_reloc = ['ABSOLUTE', 'RELATIVE', 'IMMEDIATE']
            
            for _ in range(reloc_count):
                # Sección
                section_idx = struct.unpack('<B', f.read(1))[0]
                section = '.text' if section_idx == 0 else '.data'
                
                # Tipo
                type_idx = struct.unpack('<B', f.read(1))[0]
                reloc_type = type_names_reloc[type_idx] if type_idx < len(type_names_reloc) else 'ABSOLUTE'
                
                # Padding
                f.read(6)
                
                # Offset
                offset = struct.unpack('<Q', f.read(8))[0]
                
                # Nombre del símbolo
                symbol_name = f.read(64).rstrip(b'\x00').decode('utf-8')
                
                # Addend
                addend = struct.unpack('<q', f.read(8))[0]
                
                # Crear reubicación
                reloc = RelocationEntry(
                    offset=offset,
                    reloc_type=reloc_type,
                    symbol_name=symbol_name,
                    addend=addend
                )
                obj_file.add_relocation(section, reloc)
        
        print(f"Archivo objeto leído: {filename}")
        print(f"  .text: {text_size} bytes, .data: {data_size} bytes, .bss: {bss_size} bytes")
        print(f"  Símbolos: {symbol_count}, Reubicaciones: {reloc_count}")
        
        return obj_file


# Ejemplo de uso
if __name__ == "__main__":
    print("=== GENERADOR DE ARCHIVOS OBJETO ===\n")
    
    # Crear generador
    gen = ObjectFileGenerator("ejemplo.asm")
    
    # Sección .text
    gen.set_section('.text')
    gen.add_label("_start", is_global=True)
    gen.add_instruction(0x006100000000000005)  # LOADV R1, 5
    gen.add_label("loop")
    gen.add_instruction(0x001000000000000021)  # ADD R2, R1
    gen.add_instruction(0x003100000000000000)  # DEC R1
    
    # Referencia externa (llamada a función en otro módulo)
    gen.add_external_reference("print_number")
    gen.add_instruction(0x008E00000000000000)  # CALL print_number (placeholder)
    gen.add_relocation('IMMEDIATE', 'print_number')
    
    gen.add_instruction(0x000000000000000000)  # PARAR
    
    # Sección .data
    gen.set_section('.data')
    gen.add_label("mensaje", is_global=False)
    gen.add_data(b"Hola mundo\x00")
    
    # Sección .bss
    gen.set_section('.bss')
    gen.add_label("buffer")
    gen.reserve_bss(256)  # Buffer de 256 bytes
    
    # Guardar archivo objeto
    gen.save_to_file("ejemplo.txt")
    gen.save_binary("ejemplo.o")
    
    # Leer archivo objeto
    print("\n--- Leyendo archivo objeto ---")
    obj_file = ObjectFileReader.read_binary("ejemplo.o")
    
    print("\nSímbolos:")
    for name, sym in obj_file.symbols.items():
        print(f"  {sym}")
    
    print("\nReubicaciones:")
    for section, relocs in obj_file.relocations.items():
        for reloc in relocs:
            print(f"  {section}: {reloc}")
