"""
Ensamblador simple para el simulador de CPU
Traduce código assembly a instrucciones binarias
"""

class Assembler:
    def __init__(self):
        # Mapa de instrucciones a opcodes
        self.opcodes = {
            'PARAR': 0x0000, 'NOP': 0x0001,
            'ADD': 0x0010, 'SUB': 0x0011, 'MULS': 0x0012, 'MUL': 0x0013, 'DIV': 0x0014,
            'ADDV': 0x0020, 'SUBV': 0x0021,
            'INC': 0x0030, 'DEC': 0x0031,
            'NOT': 0x0040, 'AND': 0x0041, 'ANDV': 0x0042, 'OR': 0x0043,
            'ORV': 0x0044, 'XOR': 0x0045, 'XORV': 0x0046,
            'SHL': 0x0050, 'SHR': 0x0051, 'SAL': 0x0052, 'SAR': 0x0053,
            'LOAD': 0x0060, 'LOADV': 0x0061, 'STORE': 0x0062, 'STOREV': 0x0063, 'CLEAR': 0x0064,
            'CMP': 0x0070, 'CMPV': 0x0071,
            'CLRZ': 0x0080, 'CLRN': 0x0081, 'CLRC': 0x0082, 'CLRV': 0x0083,
            'SETZ': 0x0084, 'SETN': 0x0085, 'SETC': 0x0086, 'SETV': 0x0087,
            'JMP': 0x0090, 'JEQ': 0x0091, 'JNE': 0x0092, 'JLT': 0x0093, 'JGE': 0x0094,
            'JCS': 0x0095, 'JCC': 0x0096, 'JMI': 0x0097, 'JPL': 0x0098,
            'SVIO': 0x00A0, 'LOADIO': 0x00A1, 'SHOWIO': 0x00A2, 'CLRIO': 0x00A3, 'RESETIO': 0x00A4
        }
        
        # Formatos de instrucción
        self.formats = {
            'PARAR': 'OP', 'NOP': 'OP',
            'ADD': 'RR', 'SUB': 'RR', 'MULS': 'RR', 'MUL': 'RR', 'DIV': 'RR',
            'ADDV': 'RI', 'SUBV': 'RI',
            'INC': 'R', 'DEC': 'R',
            'NOT': 'R', 'AND': 'RR', 'ANDV': 'RI', 'OR': 'RR',
            'ORV': 'RI', 'XOR': 'RR', 'XORV': 'RI',
            'SHL': 'R', 'SHR': 'R', 'SAL': 'R', 'SAR': 'R',
            'LOAD': 'RI', 'LOADV': 'RI', 'STORE': 'RR', 'STOREV': 'RI', 'CLEAR': 'R',
            'CMP': 'RR', 'CMPV': 'RI',
            'CLRZ': 'OP', 'CLRN': 'OP', 'CLRC': 'OP', 'CLRV': 'OP',
            'SETZ': 'OP', 'SETN': 'OP', 'SETC': 'OP', 'SETV': 'OP',
            'JMP': 'I', 'JEQ': 'I', 'JNE': 'I', 'JLT': 'I', 'JGE': 'I',
            'JCS': 'I', 'JCC': 'I', 'JMI': 'I', 'JPL': 'I',
            'SVIO': 'RI', 'LOADIO': 'RI',             'SHOWIO': 'I', 'CLRIO': 'OP', 'RESETIO': 'OP'
        }
        
        self.labels = {}
        self.current_address = 0

    def parse_register(self, reg_str):
        """Convierte 'R1' o 'R01' a número entero"""
        if not reg_str.startswith('R'):
            raise ValueError(f"Registro inválido: {reg_str}")
        return int(reg_str[1:])

    def parse_immediate(self, imm_str):
        """Convierte string a valor inmediato"""
        imm_str = imm_str.lower()  # Convertir a minúsculas para 0x
        if imm_str.startswith('0x'):
            return int(imm_str, 16)
        elif imm_str.startswith('0b'):
            return int(imm_str, 2)
        elif imm_str.upper() in self.labels:
            return self.labels[imm_str.upper()]
        else:
            try:
                return int(imm_str)
            except ValueError:
                # Si no es un número, debe ser una etiqueta
                imm_upper = imm_str.upper()
                if imm_upper not in self.labels:
                    raise ValueError(f"Etiqueta no definida: {imm_str}")
                return self.labels[imm_upper]

    def assemble_line(self, line):
        """Ensambla una línea de código"""
        line = line.strip().upper()
        if not line or line.startswith(';'):  # Comentario o línea vacía
            return None
        
        # Remover comentarios al final de la línea
        if ';' in line:
            line = line.split(';')[0].strip()
            if not line:
                return None
        
        # Manejar etiquetas
        if ':' in line and not line.startswith((' ', '\t')):
            label = line.split(':')[0].strip()
            self.labels[label] = self.current_address
            line = line.split(':', 1)[1].strip()
            if not line:
                return None

        parts = line.replace(',', ' ').split()
        if not parts:
            return None
            
        instruction = parts[0]
        if instruction not in self.opcodes:
            raise ValueError(f"Instrucción desconocida: {instruction}")
        
        opcode = self.opcodes[instruction]
        fmt = self.formats[instruction]
        
        # Construir la instrucción según el formato
        if fmt == 'OP':
            return (opcode << 48)
        
        elif fmt == 'R':
            if len(parts) != 2:
                raise ValueError(f"Formato R requiere 1 registro: {line}")
            rd = self.parse_register(parts[1])
            return (opcode << 48) | (rd << 44)
        
        elif fmt == 'RR':
            if len(parts) != 3:
                raise ValueError(f"Formato RR requiere 2 registros: {line}")
            rd = self.parse_register(parts[1])
            rs = self.parse_register(parts[2])
            return (opcode << 48) | (rd << 4) | rs
        
        elif fmt == 'RI':
            if len(parts) != 3:
                raise ValueError(f"Formato RI requiere registro e inmediato: {line}")
            rd = self.parse_register(parts[1])
            imm = self.parse_immediate(parts[2])
            return (opcode << 48) | (rd << 44) | (imm & 0xFFFFFFFFFFF)
        
        elif fmt == 'I':  # Solo inmediato (para SHOWIO)
            if len(parts) != 2:
                raise ValueError(f"Formato I requiere solo inmediato: {line}")
            imm = self.parse_immediate(parts[1])
            return (opcode << 48) | (imm & 0xFFFFFFFFFFF)
        
        else:
            raise ValueError(f"Formato desconocido: {fmt}")

    def assemble(self, code):
        """Ensambla código completo"""
        lines = code.split('\n')
        program = []
        self.labels = {}
        self.current_address = 0
        
        # Primera pasada: recopilar etiquetas
        temp_address = 0
        for line in lines:
            line = line.strip().upper()
            if not line or line.startswith(';'):
                continue
            
            # Remover comentarios
            if ';' in line:
                line = line.split(';')[0].strip()
                if not line:
                    continue
            
            if ':' in line and not line.startswith((' ', '\t')):
                label = line.split(':')[0].strip()
                self.labels[label] = temp_address * 8  # Direcciones en bytes
                line = line.split(':', 1)[1].strip()
            if line:
                temp_address += 1
        
        # Segunda pasada: generar código
        self.current_address = 0
        for line in lines:
            instruction = self.assemble_line(line)
            if instruction is not None:
                program.append(instruction)
                self.current_address += 8
        
        return program

    def disassemble_instruction(self, instr):
        """Desarma una instrucción a texto legible"""
        opcode = (instr >> 48) & 0xFFFF
        
        # Buscar el nombre de la instrucción
        instr_name = None
        for name, op in self.opcodes.items():
            if op == opcode:
                instr_name = name
                break
        
        if not instr_name:
            return f"UNKNOWN {opcode:#06x}"
        
        fmt = self.formats[instr_name]
        
        if fmt == 'OP':
            return instr_name
        elif fmt == 'R':
            rd = (instr >> 44) & 0xF
            return f"{instr_name} R{rd:02d}"
        elif fmt == 'RR':
            rd = (instr >> 4) & 0xF
            rs = instr & 0xF
            return f"{instr_name} R{rd:02d}, R{rs:02d}"
        elif fmt == 'RI':
            rd = (instr >> 44) & 0xF
            imm = instr & 0xFFFFFFFFFFF
            return f"{instr_name} R{rd:02d}, {imm}"
        elif fmt == 'I':
            imm = instr & 0xFFFFFFFFFFF
            return f"{instr_name} {imm}"
        
        return f"UNKNOWN FORMAT for {instr_name}"

# Ejemplo de uso
if __name__ == "__main__":
    assembler = Assembler()
    
    sample_code = """
    ; Programa de ejemplo - suma de los primeros n enteros
    LOADV R1, 5      ; n = 5
    CLEAR R2         ; acumulador = 0
    
    LOOP:
    ADD R2, R1       ; acumulador += n
    DEC R1           ; n--
    CMPV R1, 0       ; comparar n con 0
    JNE LOOP         ; si n != 0, saltar al loop
    
    ; Mostrar resultado
    SVIO R2, 0x30    ; guardar resultado en IO[0x30]
    SHOWIO 0x30      ; mostrar resultado
    PARAR            ; terminar programa
    """
    
    try:
        program = assembler.assemble(sample_code)
        print("Programa ensamblado:")
        for i, instr in enumerate(program):
            print(f"{i*8:04x}: {instr:016x} ; {assembler.disassemble_instruction(instr)}")
    except Exception as e:
        print(f"Error de ensamblado: {e}")