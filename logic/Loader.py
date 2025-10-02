"""
Cargador (Loader) para el simulador de CPU
Carga programas binarios en memoria y maneja la reubicación de direcciones
"""

class Loader:
    def __init__(self, memory_system):
        """
        Inicializa el cargador con un sistema de memoria
        
        Args:
            memory_system: Sistema de memoria donde cargar los programas
        """
        self.memory = memory_system
        self.loaded_programs = {}  # Registro de programas cargados
        self.next_free_address = 0  # Próxima dirección libre
        
    def load_program(self, program_binary, start_address=None, program_name="default"):
        """
        Carga un programa binario en memoria
        
        Args:
            program_binary: Lista de instrucciones binarias
            start_address: Dirección donde cargar (None para automática)
            program_name: Nombre del programa para tracking
            
        Returns:
            dict: Información del programa cargado
        """
        # Calcular tamaño del programa
        program_size = len(program_binary) * 8  # 8 bytes por instrucción
        
        # Determinar dirección de carga
        if start_address is None:
            start_address = self.find_free_space(program_size)
        
        # Verificar que hay espacio suficiente
        if not self.check_memory_space(start_address, program_size):
            raise MemoryError(f"No hay espacio suficiente en memoria para cargar {program_name}")
        
        # Aplicar reubicación si es necesario
        if start_address != 0:
            program_binary = self.relocate_program(program_binary, 0, start_address)
        
        # Cargar programa en memoria
        self.write_program_to_memory(program_binary, start_address)
        
        # Registrar programa cargado
        program_info = {
            'name': program_name,
            'start_address': start_address,
            'end_address': start_address + program_size - 8,
            'size': program_size,
            'instructions_count': len(program_binary)
        }
        
        self.loaded_programs[program_name] = program_info
        
        # Actualizar próxima dirección libre
        self.next_free_address = max(self.next_free_address, start_address + program_size)
        
        return program_info
    
    def find_free_space(self, required_size):
        """
        Encuentra espacio libre en memoria para un programa
        
        Args:
            required_size: Tamaño requerido en bytes
            
        Returns:
            int: Dirección de inicio del espacio libre
        """
        # Estrategia simple: usar la próxima dirección libre
        # En un sistema real, esto sería más complejo (fragmentación, etc.)
        return self.next_free_address
    
    def check_memory_space(self, start_address, size):
        """
        Verifica si hay espacio suficiente en memoria
        
        Args:
            start_address: Dirección de inicio
            size: Tamaño requerido
            
        Returns:
            bool: True si hay espacio suficiente
        """
        end_address = start_address + size
        memory_size = len(self.memory.memory) if hasattr(self.memory, 'memory') else 4096 * 8
        
        return end_address <= memory_size
    
    def write_program_to_memory(self, program_binary, start_address):
        """
        Escribe el programa binario en memoria
        
        Args:
            program_binary: Lista de instrucciones binarias
            start_address: Dirección de inicio
        """
        for i, instruction in enumerate(program_binary):
            memory_address = start_address + (i * 8)
            
            # Convertir instrucción a bytes y escribir en memoria
            instruction_bytes = instruction.to_bytes(8, 'little')
            
            # Escribir en memoria del sistema
            if hasattr(self.memory, 'memory'):
                # CPU memory (lista de enteros)
                for j, byte_val in enumerate(instruction_bytes):
                    if memory_address + j < len(self.memory.memory):
                        self.memory.memory[memory_address + j] = byte_val
            else:
                # Otro tipo de memoria
                self.memory[memory_address:memory_address + 8] = instruction_bytes
    
    def relocate_program(self, program_binary, old_base, new_base):
        """
        Reubica un programa a una nueva dirección base
        
        Args:
            program_binary: Programa binario original
            old_base: Dirección base original
            new_base: Nueva dirección base
            
        Returns:
            list: Programa reubicado
        """
        relocated_program = []
        offset = new_base - old_base
        
        for instruction in program_binary:
            # Extraer opcode para determinar si necesita reubicación
            opcode = (instruction >> 48) & 0xFFFF
            
            # Instrucciones de salto que necesitan reubicación
            jump_opcodes = {0x0090, 0x0091, 0x0092, 0x0093, 0x0094, 
                          0x0095, 0x0096, 0x0097, 0x0098}
            
            if opcode in jump_opcodes:
                # Reajustar dirección de salto
                immediate = instruction & 0xFFFFFFFFFFF
                new_immediate = immediate + offset
                relocated_instruction = (instruction & ~0xFFFFFFFFFFF) | (new_immediate & 0xFFFFFFFFFFF)
                relocated_program.append(relocated_instruction)
            else:
                # Instrucción no necesita reubicación
                relocated_program.append(instruction)
        
        return relocated_program
    
    def unload_program(self, program_name):
        """
        Descarga un programa de memoria
        
        Args:
            program_name: Nombre del programa a descargar
            
        Returns:
            bool: True si se descargó exitosamente
        """
        if program_name not in self.loaded_programs:
            return False
        
        program_info = self.loaded_programs[program_name]
        start_addr = program_info['start_address']
        size = program_info['size']
        
        # Limpiar memoria
        self.clear_memory_region(start_addr, size)
        
        # Remover del registro
        del self.loaded_programs[program_name]
        
        return True
    
    def clear_memory_region(self, start_address, size):
        """
        Limpia una región de memoria
        
        Args:
            start_address: Dirección de inicio
            size: Tamaño a limpiar
        """
        end_address = start_address + size
        
        if hasattr(self.memory, 'memory'):
            for addr in range(start_address, min(end_address, len(self.memory.memory))):
                self.memory.memory[addr] = 0
    
    def get_program_info(self, program_name):
        """
        Obtiene información de un programa cargado
        
        Args:
            program_name: Nombre del programa
            
        Returns:
            dict: Información del programa o None
        """
        return self.loaded_programs.get(program_name)
    
    def list_loaded_programs(self):
        """
        Lista todos los programas cargados
        
        Returns:
            dict: Diccionario de programas cargados
        """
        return self.loaded_programs.copy()
    
    def get_memory_map(self):
        """
        Obtiene un mapa de uso de memoria
        
        Returns:
            dict: Mapa de memoria mostrando regiones ocupadas
        """
        memory_map = {
            'total_memory': len(self.memory.memory) if hasattr(self.memory, 'memory') else 4096 * 8,
            'used_memory': self.next_free_address,
            'free_memory': (len(self.memory.memory) if hasattr(self.memory, 'memory') else 4096 * 8) - self.next_free_address,
            'programs': {}
        }
        
        for name, info in self.loaded_programs.items():
            memory_map['programs'][name] = {
                'start': f"0x{info['start_address']:04x}",
                'end': f"0x{info['end_address']:04x}",
                'size': info['size']
            }
        
        return memory_map
    
    def dump_memory_state(self):
        """
        Muestra el estado actual de la memoria (para debugging)
        """
        print("=== ESTADO DEL CARGADOR ===")
        print(f"Próxima dirección libre: 0x{self.next_free_address:04x}")
        print(f"Programas cargados: {len(self.loaded_programs)}")
        
        for name, info in self.loaded_programs.items():
            print(f"  {name}: 0x{info['start_address']:04x} - 0x{info['end_address']:04x} ({info['size']} bytes)")
        
        memory_map = self.get_memory_map()
        print(f"Memoria total: {memory_map['total_memory']} bytes")
        print(f"Memoria usada: {memory_map['used_memory']} bytes")
        print(f"Memoria libre: {memory_map['free_memory']} bytes")


# Ejemplo de uso
if __name__ == "__main__":
    # Simulación de sistema de memoria simple
    class SimpleMemory:
        def __init__(self, size=4096):
            self.memory = [0] * size
    
    # Crear sistema de memoria y cargador
    memory_system = SimpleMemory()
    loader = Loader(memory_system)
    
    # Programa de ejemplo (instrucciones binarias)
    sample_program = [
        0x006100000000000005,  # LOADV R1, 5
        0x006400000000000000,  # CLEAR R2
        0x001000000000000021,  # ADD R2, R1
        0x003100000000000000,  # DEC R1
        0x007100000000000000,  # CMPV R1, 0
        0x009200000000000010,  # JNE LOOP
        0x00A0200000000030,    # SVIO R2, 0x30
        0x00A2000000000030,    # SHOWIO 0x30
        0x000000000000000000   # PARAR
    ]
    
    try:
        # Cargar programa
        program_info = loader.load_program(sample_program, program_name="suma_numeros")
        print("Programa cargado exitosamente:")
        print(f"  Dirección de inicio: 0x{program_info['start_address']:04x}")
        print(f"  Tamaño: {program_info['size']} bytes")
        print(f"  Instrucciones: {program_info['instructions_count']}")
        
        # Mostrar estado de memoria
        loader.dump_memory_state()
        
    except Exception as e:
        print(f"Error al cargar programa: {e}")