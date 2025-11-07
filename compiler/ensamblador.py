"""
Ensamblador con análisis léxico usando PLY
Traduce código assembly a instrucciones binarias
Integra preprocesador y generación de bytecode
Puede generar archivos objeto para enlace posterior
"""

import ply.lex as lex
import os
from compiler.preprocessor import Preprocessor
from compiler.object_file_generator import ObjectFileGenerator

# =============================================
# ANALIZADOR LÉXICO (PLY Lex)
# =============================================

tokens = (
    'LABEL',
    'INSTRUCTION',
    'NUMBER',
    'REGISTER',
    'COMMA',
    'NEWLINE'
)

# Tokens ignorados
t_ignore = ' \t'
t_ignore_COMMENT = r';[^\n]*'

# Reglas de tokens
def t_LABEL(t):
    r'[A-Za-z_][A-Za-z0-9_]*:'
    t.value = t.value[:-1]  # Remover el ':'
    return t

def t_REGISTER(t):
    r'R[0-9]+'
    return t

def t_NUMBER(t):
    r'0x[0-9A-Fa-f]+|0b[01]+|\d+'
    return t

def t_INSTRUCTION(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    return t

def t_COMMA(t):
    r','
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

# =============================================
# ENSAMBLADOR PRINCIPAL
# =============================================

class Ensamblador:
    """Ensamblador completo con PLY y generación de bytecode"""
    
    def __init__(self, use_preprocessor=True):
        self.lexer = lex.lex()
        self.use_preprocessor = use_preprocessor
        self.preprocessor = Preprocessor() if use_preprocessor else None
        
        # Tabla de símbolos (etiquetas y direcciones)
        self.labels = {}
        self.current_address = 0
        
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
            'SHL': 'RR', 'SHR': 'RR', 'SAL': 'RR', 'SAR': 'RR',
            
            # Memoria básica
            'LOAD': 'RI', 'LOADV': 'RI', 'STORE': 'RI', 'STOREV': 'RI', 'CLEAR': 'R',
            
            # Comparación
            'CMP': 'RR', 'CMPV': 'RI',
            
            # Flags
            'CLRZ': 'OP', 'CLRN': 'OP', 'CLRC': 'OP', 'CLRV': 'OP',
            'SETZ': 'OP', 'SETN': 'OP', 'SETC': 'OP', 'SETV': 'OP',
            
            # Saltos
            'JMP': 'I', 'JEQ': 'I', 'JNE': 'I', 'JLT': 'I', 'JGE': 'I',
            'JCS': 'I', 'JCC': 'I', 'JMI': 'I', 'JPL': 'I',
            
            # I/O
            'SVIO': 'RI', 'LOADIO': 'RI', 'SHOWIO': 'I', 'CLRIO': 'I', 'RESETIO': 'OP',
            
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
    
    def tokenize_line(self, line):
        """Tokeniza una línea usando PLY"""
        self.lexer.input(line)
        tokens_list = []
        for tok in self.lexer:
            if tok.type != 'NEWLINE':
                tokens_list.append(tok)
        return tokens_list
    
    def parse_register(self, reg_token):
        """Convierte token de registro a número"""
        reg_str = reg_token.value if hasattr(reg_token, 'value') else reg_token
        if not reg_str.startswith('R'):
            raise ValueError(f"Registro inválido: {reg_str}")
        return int(reg_str[1:])
    
    def parse_immediate(self, imm_token):
        """Convierte token de número a valor inmediato"""
        imm_str = imm_token.value if hasattr(imm_token, 'value') else imm_token
        imm_str_lower = imm_str.lower()
        
        if imm_str_lower.startswith('0x'):
            return int(imm_str, 16)
        elif imm_str_lower.startswith('0b'):
            return int(imm_str, 2)
        elif imm_str.upper() in self.labels:
            return self.labels[imm_str.upper()]
        else:
            try:
                return int(imm_str)
            except ValueError:
                # Debe ser una etiqueta
                imm_upper = imm_str.upper()
                if imm_upper not in self.labels:
                    raise ValueError(f"Etiqueta no definida: {imm_str}")
                return self.labels[imm_upper]
    
    def assemble_tokens(self, tokens):
        """Ensambla una lista de tokens a bytecode"""
        if not tokens:
            return None
        
        instruction = tokens[0].value.upper()
        
        if instruction not in self.opcodes:
            raise ValueError(f"Instrucción desconocida: {instruction}")
        
        opcode = self.opcodes[instruction]
        fmt = self.formats[instruction]
        
        # Construir la instrucción según el formato
        if fmt == 'OP':
            return (opcode << 48)
        
        elif fmt == 'R':
            if len(tokens) < 2:
                raise ValueError(f"Formato R requiere 1 registro: {instruction}")
            rd = self.parse_register(tokens[1])
            return (opcode << 48) | (rd << 44)
        
        elif fmt == 'RR':
            if len(tokens) < 3:
                raise ValueError(f"Formato RR requiere 2 registros: {instruction}")
            # Saltar comas
            reg_tokens = [t for t in tokens[1:] if t.type != 'COMMA']
            if len(reg_tokens) < 2:
                raise ValueError(f"Formato RR requiere 2 registros: {instruction}")
            rd = self.parse_register(reg_tokens[0])
            rs = self.parse_register(reg_tokens[1])
            return (opcode << 48) | (rd << 4) | rs
        
        elif fmt == 'RI':
            if len(tokens) < 3:
                raise ValueError(f"Formato RI requiere registro e inmediato: {instruction}")
            # Saltar comas
            operands = [t for t in tokens[1:] if t.type != 'COMMA']
            if len(operands) < 2:
                raise ValueError(f"Formato RI requiere registro e inmediato: {instruction}")
            rd = self.parse_register(operands[0])
            imm = self.parse_immediate(operands[1])
            return (opcode << 48) | (rd << 44) | (imm & 0xFFFFFFFFFFF)
        
        elif fmt == 'I':
            if len(tokens) < 2:
                raise ValueError(f"Formato I requiere inmediato: {instruction}")
            imm = self.parse_immediate(tokens[1])
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
            if source_file:
                base_path = os.path.dirname(os.path.abspath(source_file))
            else:
                base_path = os.getcwd()
            code = self.preprocessor.preprocess(code, base_path)
        
        lines = code.split('\n')
        self.labels = {}
        self.current_address = 0
        
        # Primera pasada: recopilar etiquetas
        temp_address = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            tokens = self.tokenize_line(line)
            if not tokens:
                continue
            
            # Si hay etiqueta, guardarla
            if tokens[0].type == 'LABEL':
                label_name = tokens[0].value.upper()
                self.labels[label_name] = temp_address * 8  # Direcciones en bytes
                tokens = tokens[1:]  # Remover la etiqueta
            
            # Si hay instrucción después de la etiqueta
            if tokens and tokens[0].type == 'INSTRUCTION':
                temp_address += 1
        
        # Segunda pasada: generar código
        program = []
        self.current_address = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            tokens = self.tokenize_line(line)
            if not tokens:
                continue
            
            # Saltar etiquetas
            if tokens[0].type == 'LABEL':
                tokens = tokens[1:]
            
            if tokens and tokens[0].type == 'INSTRUCTION':
                instruction = self.assemble_tokens(tokens)
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
    
    def assemble_to_object(self, source, module_name="module", global_symbols=None):
        """
        Ensambla código a archivo objeto para enlace posterior
        
        Args:
            source: Código assembly
            module_name: Nombre del módulo
            global_symbols: Lista de símbolos a exportar como globales
            
        Returns:
            ObjectFileGenerator: Generador con archivo objeto completo
        """
        if global_symbols is None:
            global_symbols = []
        
        # Preprocesar
        if self.use_preprocessor:
            source = self.preprocessor.preprocess(source)
        
        # Crear generador de archivo objeto
        gen = ObjectFileGenerator(module_name)
        
        # Resetear estado
        self.labels = {}
        self.current_address = 0
        
        # Primera pasada: recolectar etiquetas y detectar directivas
        current_section = '.text'
        gen.set_section(current_section)
        
        lines = source.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Detectar directivas de sección
            if line.startswith('.'):
                section = line.split()[0]
                if section in ['.text', '.data', '.bss']:
                    current_section = section
                    gen.set_section(current_section)
                continue
            
            # Detectar directivas de símbolos globales/externos
            if line.upper().startswith('GLOBAL'):
                parts = line.split()
                if len(parts) >= 2:
                    symbol = parts[1]
                    if symbol not in global_symbols:
                        global_symbols.append(symbol)
                continue
            
            if line.upper().startswith('EXTERN'):
                parts = line.split()
                if len(parts) >= 2:
                    symbol = parts[1]
                    gen.add_external_reference(symbol)
                continue
            
            # Detectar etiquetas
            if ':' in line:
                label_name = line.split(':')[0].strip()
                is_global = label_name in global_symbols
                gen.add_label(label_name, is_global)
                self.labels[label_name] = self.current_address
                
                # Si hay instrucción después de la etiqueta
                rest = ':'.join(line.split(':')[1:]).strip()
                if rest:
                    line = rest
                else:
                    continue
            
            # Procesar instrucción
            if current_section == '.text':
                tokens = self.tokenize_line(line)
                if tokens:
                    instruction = self.build_instruction(tokens)
                    gen.add_instruction(instruction)
                    self.current_address += 8
            elif current_section == '.data':
                # Procesar datos (simplificado por ahora)
                pass
            elif current_section == '.bss':
                # Procesar reserva de espacio
                pass
        
        return gen


# =============================================
# EJEMPLO DE USO
# =============================================

if __name__ == "__main__":
    source = """
LOADV R1, 1071
LOADV R2, 462

MIENTRAS:
CMP R1, R2
JEQ FIN_MIENTRAS
CMP R1, R2
JLT CASO_B_MAYOR
SUB R1, R2
JMP MIENTRAS

CASO_B_MAYOR:
SUB R2, R1
JMP MIENTRAS

FIN_MIENTRAS:
SVIO R1, 0x100
SHOWIO 0x100
PARAR
"""

    assembler = Ensamblador()
    program = assembler.assemble(source)

    print("=" * 60)
    print("Tabla de simbolos (etiquetas):")
    print("=" * 60)
    for k, v in assembler.labels.items():
        print(f"  {k:20s} -> 0x{v:04X}")

    print("\n" + "=" * 60)
    print("Codigo ensamblado (bytecode):")
    print("=" * 60)
    for i, instr in enumerate(program):
        addr = i * 8
        disasm = assembler.disassemble_instruction(instr)
        print(f"{addr:04X}: {instr:016X}  {disasm}")






