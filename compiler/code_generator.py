"""
Ensamblador simple para el simulador de CPU
Traduce código assembly a instrucciones binarias
"""

import os
from .preprocessor import Preprocessor

class Assembler:
    def __init__(self, use_preprocessor=True):
        self.use_preprocessor = use_preprocessor
        self.preprocessor = Preprocessor() if use_preprocessor else None
        # Mapa de instrucciones a opcodes
        self.opcodes = {
            # Control básico
            'PARAR': 0x0000, 'NOP': 0x0001,
            
            # Aritmética básica (8 bytes)
            'ADD': 0x0010, 'SUB': 0x0011, 'MULS': 0x0012, 'MUL': 0x0013, 'DIV': 0x0014,
            'ADDV': 0x0020, 'SUBV': 0x0021,
            'INC': 0x0030, 'DEC': 0x0031,
            
            # Lógicas
            'NOT': 0x0040, 'AND': 0x0041, 'ANDV': 0x0042, 'OR': 0x0043,
            'ORV': 0x0044, 'XOR': 0x0045, 'XORV': 0x0046,
            
            # Shifts
            'SHL': 0x0050, 'SHR': 0x0051, 'SAL': 0x0052, 'SAR': 0x0053,
            
            # Memoria básica
            'LOAD': 0x0060, 'LOADV': 0x0061, 'STORE': 0x0062, 'STOREV': 0x0063, 'CLEAR': 0x0064,
            
            # Comparación
            'CMP': 0x0070, 'CMPV': 0x0071,
            
            # Flags
            'CLRZ': 0x0080, 'CLRN': 0x0081, 'CLRC': 0x0082, 'CLRV': 0x0083,
            'SETZ': 0x0084, 'SETN': 0x0085, 'SETC': 0x0086, 'SETV': 0x0087,
            
            # Saltos
            'JMP': 0x0090, 'JEQ': 0x0091, 'JNE': 0x0092, 'JLT': 0x0093, 'JGE': 0x0094,
            'JCS': 0x0095, 'JCC': 0x0096, 'JMI': 0x0097, 'JPL': 0x0098,
            
            # I/O
            'SVIO': 0x00A0, 'LOADIO': 0x00A1, 'SHOWIO': 0x00A2, 'CLRIO': 0x00A3, 'RESETIO': 0x00A4,
            
            # Aritmética con tamaños específicos (1 byte)
            'ADD1': 0x0100, 'SUB1': 0x0101, 'MUL1': 0x0102, 'MULS1': 0x0103, 'DIV1': 0x0104,
            'ADDV1': 0x0110, 'SUBV1': 0x0111,
            
            # Aritmética con tamaños específicos (2 bytes)
            'ADD2': 0x0200, 'SUB2': 0x0201, 'MUL2': 0x0202, 'MULS2': 0x0203, 'DIV2': 0x0204,
            'ADDV2': 0x0210, 'SUBV2': 0x0211,
            
            # Aritmética con tamaños específicos (4 bytes)
            'ADD4': 0x0300, 'SUB4': 0x0301, 'MUL4': 0x0302, 'MULS4': 0x0303, 'DIV4': 0x0304,
            'ADDV4': 0x0310, 'SUBV4': 0x0311,

            # Aritmética con tamaños específicos (8 bytes)
            'ADD8': 0x0312, 'SUB8': 0x0313, 'MUL8': 0x0314, 'MULS8': 0x0315, 'DIV8': 0x0316,
            'ADDV8': 0x0317, 'SUBV8': 0x0318,
            
            # MOV instructions
            'MOV1': 0x0400, 'MOV2': 0x0401, 'MOV4': 0x0402, 'MOV8': 0x0403,
            'MOVV1': 0x0410, 'MOVV2': 0x0411, 'MOVV4': 0x0412, 'MOVV8': 0x0413,
            
            # LOAD instructions
            'LOAD1': 0x0500, 'LOAD2': 0x0501, 'LOAD4': 0x0502, 'LOAD8': 0x0503,
            'LOADR1': 0x0510, 'LOADR2': 0x0511, 'LOADR4': 0x0512, 'LOADR8': 0x0513,
            
            # STORE instructions
            'STORE1': 0x0600, 'STORE2': 0x0601, 'STORE4': 0x0602, 'STORE8': 0x0603,
            'STORER1': 0x0610, 'STORER2': 0x0611, 'STORER4': 0x0612, 'STORER8': 0x0613,
            
            # FPU instructions (4 bytes)
            'FADD4': 0x0700, 'FSUB4': 0x0701, 'FMUL4': 0x0702, 'FDIV4': 0x0703,
            'FSQRT4': 0x0720, 'FSIN4': 0x0722, 'FCOS4': 0x0723,
            
            # FPU instructions (8 bytes)
            'FADD8': 0x0710, 'FSUB8': 0x0711, 'FMUL8': 0x0712, 'FDIV8': 0x0713,
            'FSQRT8': 0x0721, 'FSIN8': 0x0724, 'FCOS8': 0x0725,
         
            # Stack instructions
            'RET': 0x0800,'CALL': 0x0099,
            'POP1': 0x0810, 'POP2': 0x0811, 'POP4': 0x0812, 'POP8': 0x0813,
            'PUSH1': 0x0820, 'PUSH2': 0x0821, 'PUSH4': 0x0822, 'PUSH8': 0x0823,
            
            # Size-specific CMP instructions
            'CMP1': 0x0830, 'CMP2': 0x0831, 'CMP4': 0x0832, 'CMP8': 0x0833,
            'CMPV1': 0x0840, 'CMPV2': 0x0841, 'CMPV4': 0x0842, 'CMPV8': 0x0843,
        }
        
        # Formatos de instrucción
        self.formats = {
            # Control básico
            'PARAR': 'OP', 'NOP': 'OP',
            
            # Aritmética básica (8 bytes)
            'ADD': 'RR', 'SUB': 'RR', 'MULS': 'RR', 'MUL': 'RR', 'DIV': 'RR',
            'ADDV': 'RI', 'SUBV': 'RI',
            'INC': 'R', 'DEC': 'R',
            
            # Lógicas
            'NOT': 'R', 'AND': 'RR', 'ANDV': 'RI', 'OR': 'RR',
            'ORV': 'RI', 'XOR': 'RR', 'XORV': 'RI',
            
            # Shifts
            'SHL': 'R', 'SHR': 'R', 'SAL': 'R', 'SAR': 'R',
            
            # Memoria básica
            'LOAD': 'RI', 'LOADV': 'RI', 'STORE': 'RR', 'STOREV': 'RI', 'CLEAR': 'R',
            
            # Comparación
            'CMP': 'RR', 'CMPV': 'RI',
            
            # Flags
            'CLRZ': 'OP', 'CLRN': 'OP', 'CLRC': 'OP', 'CLRV': 'OP',
            'SETZ': 'OP', 'SETN': 'OP', 'SETC': 'OP', 'SETV': 'OP',
            
            # Saltos
            'JMP': 'I', 'JEQ': 'I', 'JNE': 'I', 'JLT': 'I', 'JGE': 'I',
            'JCS': 'I', 'JCC': 'I', 'JMI': 'I', 'JPL': 'I',
            
            # I/O
            'SVIO': 'RI', 'LOADIO': 'RI', 'SHOWIO': 'I', 'CLRIO': 'OP', 'RESETIO': 'OP',
            
            # Aritmética con tamaños específicos (1 byte)
            'ADD1': 'RR', 'SUB1': 'RR', 'MUL1': 'RR', 'MULS1': 'RR', 'DIV1': 'RR',
            'ADDV1': 'RI', 'SUBV1': 'RI',
            
            # Aritmética con tamaños específicos (2 bytes)
            'ADD2': 'RR', 'SUB2': 'RR', 'MUL2': 'RR', 'MULS2': 'RR', 'DIV2': 'RR',
            'ADDV2': 'RI', 'SUBV2': 'RI',
            
            # Aritmética con tamaños específicos (4 bytes)
            'ADD4': 'RR', 'SUB4': 'RR', 'MUL4': 'RR', 'MULS4': 'RR', 'DIV4': 'RR',
            'ADDV4': 'RI', 'SUBV4': 'RI',

            # Aritmética con tamaños específicos (8 bytes)
            'ADD8': 'RR', 'SUB8': 'RR', 'MUL8': 'RR', 'MULS8': 'RR', 'DIV8': 'RR',
            'ADDV8': 'RI', 'SUBV8': 'RI',
            
            # MOV instructions
            'MOV1': 'RR', 'MOV2': 'RR', 'MOV4': 'RR', 'MOV8': 'RR',
            'MOVV1': 'RI', 'MOVV2': 'RI', 'MOVV4': 'RI', 'MOVV8': 'RI',
            
            # LOAD instructions
            'LOAD1': 'RI', 'LOAD2': 'RI', 'LOAD4': 'RI', 'LOAD8': 'RI',
            'LOADR1': 'RR', 'LOADR2': 'RR', 'LOADR4': 'RR', 'LOADR8': 'RR',
            
            # STORE instructions
            'STORE1': 'RI', 'STORE2': 'RI', 'STORE4': 'RI', 'STORE8': 'RI',
            'STORER1': 'RR', 'STORER2': 'RR', 'STORER4': 'RR', 'STORER8': 'RR',
            
            # FPU instructions (4 bytes)
            'FADD4': 'RR', 'FSUB4': 'RR', 'FMUL4': 'RR', 'FDIV4': 'RR',
            'FSQRT4': 'R', 'FSIN4': 'R', 'FCOS4': 'R',
            
            # FPU instructions (8 bytes)
            'FADD8': 'RR', 'FSUB8': 'RR', 'FMUL8': 'RR', 'FDIV8': 'RR',
            'FSQRT8': 'R', 'FSIN8': 'R', 'FCOS8': 'R',
            
            # Stack instructions
            'RET': 'OP', 'CALL': 'I',
            'POP1': 'R', 'POP2': 'R', 'POP4': 'R', 'POP8': 'R',
            'PUSH1': 'R', 'PUSH2': 'R', 'PUSH4': 'R', 'PUSH8': 'R',
            
            # Size-specific CMP instructions
            'CMP1': 'RR', 'CMP2': 'RR', 'CMP4': 'RR', 'CMP8': 'RR',
            'CMPV1': 'RI', 'CMPV2': 'RI', 'CMPV4': 'RI', 'CMPV8': 'RI',
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

    def assemble(self, code, source_file=None):
        """
        Ensambla código completo
        
        Args:
            code: Código fuente a ensamblar
            source_file: Ruta del archivo fuente (opcional, para includes)
        
        Returns:
            Lista de instrucciones en formato binario
        """
        # Preprocesar el código si está habilitado
        if self.use_preprocessor and self.preprocessor:
            # Determinar el directorio base para includes
            if source_file:
                base_path = os.path.dirname(os.path.abspath(source_file))
            else:
                base_path = os.getcwd()
            
            # Preprocesar
            code = self.preprocessor.preprocess(code, base_path)
        
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
    ; Programa de ejemplo - demostración de nuevas instrucciones
    ; Usando operaciones de diferentes tamaños y stack
    
    ; Test de operaciones de diferentes tamaños
    MOVV1 R1, 0xFF   ; R1 = 0xFF (1 byte)
    MOVV2 R2, 0x1234 ; R2 = 0x1234 (2 bytes)
    MOVV4 R3, 0x12345678 ; R3 = 0x12345678 (4 bytes)
    MOVV8 R4, 0x123456789ABCDEF0 ; R4 = 0x123456789ABCDEF0 (8 bytes)
    
    ; Test de operaciones aritméticas por tamaño
    ADD1 R1, R1      ; R1 = R1 + R1 (1 byte)
    ADD2 R2, R2      ; R2 = R2 + R2 (2 bytes)
    ADD4 R3, R3      ; R3 = R3 + R3 (4 bytes)
    ADD R4, R4       ; R4 = R4 + R4 (8 bytes)
    
    ; Test de operaciones de pila
    PUSH8 R4         ; Push R4 (8 bytes) a la pila
    PUSH4 R3         ; Push R3 (4 bytes) a la pila
    PUSH2 R2         ; Push R2 (2 bytes) a la pila
    PUSH1 R1         ; Push R1 (1 byte) a la pila
    
    ; Pop en orden inverso
    POP1 R5          ; Pop 1 byte a R5
    POP2 R6          ; Pop 2 bytes a R6
    POP4 R7          ; Pop 4 bytes a R7
    POP8 R8          ; Pop 8 bytes a R8
    
    ; Mostrar resultados
    SVIO R1, 0x100   ; Mostrar R1
    SHOWIO 0x100
    SVIO R2, 0x101   ; Mostrar R2
    SHOWIO 0x101
    SVIO R3, 0x102   ; Mostrar R3
    SHOWIO 0x102
    SVIO R4, 0x103   ; Mostrar R4
    SHOWIO 0x103
    
    SVIO R5, 0x200   ; Mostrar POP1 resultado
    SHOWIO 0x200
    SVIO R6, 0x201   ; Mostrar POP2 resultado
    SHOWIO 0x201
    SVIO R7, 0x202   ; Mostrar POP4 resultado
    SHOWIO 0x202
    SVIO R8, 0x203   ; Mostrar POP8 resultado
    SHOWIO 0x203
    
    PARAR            ; terminar programa
    """
    
    try:
        program = assembler.assemble(sample_code)
        print("Programa ensamblado:")
        for i, instr in enumerate(program):
            print(f"{i*8:04x}: {instr:016x} ; {assembler.disassemble_instruction(instr)}")
    except Exception as e:
        print(f"Error de ensamblado: {e}")