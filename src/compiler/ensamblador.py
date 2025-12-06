"""
Ensamblador con análisis léxico usando PLY
Traduce código assembly a instrucciones binarias
Integra preprocesador y generación de bytecode
Puede generar archivos objeto para enlace posterior
"""

import ply.lex as lex
from compiler.instructions import INSTRUCTION_SET as IS, IS_INV

# =============================================
# ANALIZADOR LÉXICO (PLY Lex)
# =============================================

tokens = (
    'LABEL',
    'INSTRUCTION',
    'NUMBER',
    'FLOAT',
    'CHAR',
    'STRING',
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
    r'R[0-9]+|SP'
    return t

def t_NUMBER(t):
    r'[+-]?(0x[0-9A-Fa-f]+|0b[01]+|\d+)'
    return t

def t_FLOAT(t):
    r'[fd][+-]?(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?'
    return t

def t_CHAR(t):
    r'\'[\x20-\x7E]\''
    return t

def t_STRING(t):
    r'\"[^\x00-\x1F\x7F"]*\"'
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
# Para castear flotantes
# =============================================

import struct
import re

float_re = re.compile(
    r'(?P<type>[fd])'
    r'(?P<sign>[+-]?)'
    r'(?P<mant>(\d+\.\d*|\.\d+|\d+))'
    r'([eE](?P<exp_sign>[+-]?)(?P<exp>\d+))?'
)

def literal_to_ieee_int(literal: str) -> int:
    m = float_re.fullmatch(literal)
    if not m:
        raise ValueError(f"Literal flotante inválido: {literal}")

    tipo = m.group('type')
    sign = m.group('sign') or ''
    mant = m.group('mant')
    exp  = ''

    if m.group('exp') is not None:
        exp_sign = m.group('exp_sign') or '+'
        exp = 'e' + exp_sign + m.group('exp')

    number = float(sign + mant + exp)

    if tipo == 'f':
        return struct.unpack('>I', struct.pack('>f', number))[0]
    else:  # tipo == 'd'
        return struct.unpack('>Q', struct.pack('>d', number))[0]

# =============================================
# ENSAMBLADOR PRINCIPAL
# =============================================

class Ensamblador:
    """Ensamblador completo con PLY y generación de bytecode"""
    
    def __init__(self):
        self.lexer = lex.lex()
        # Tabla de símbolos (etiquetas y direcciones)
        self.labels = {}
        self.current_address = 0
    
    
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
        if reg_str == "SP":
            return 15 ## SP in CPU
        if not reg_str.startswith('R'):
            raise ValueError(f"Registro inválido: {reg_str}")
        return int(reg_str[1:])
    

    ### 
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
        
        ### FLOATANTE
        elif imm_str_lower.startswith(('d','f')):
            cast = literal_to_ieee_int(imm_str_lower)
            return cast
        
        ### CHARS
        elif imm_str_lower.startswith('\''):
            char = imm_str_lower.strip('\'')
            return ord(char)
        
        else:
            ## Entero
            try:   
                # Si negativo parsear a equivalente entero
                if(imm_str_lower.startswith('-')):
                    max64 = 1 << 64
                    return(max64 + int(imm_str))
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
        
        if instruction not in IS.keys():
            raise ValueError(f"Instrucción desconocida: {instruction}")
        
        opcode = IS[instruction]["opcode"]
        fmt = IS[instruction]["format"]
        address = IS[instruction]["requiresAddress"]
        # Construir la instrucción según el formato
        if fmt == 'OP':
            return f"{opcode:04X}{0:012X}\n"
        
        elif fmt == 'R':
            if len(tokens) < 2:
                raise ValueError(f"Formato R requiere 1 registro: {instruction}")
            rd = self.parse_register(tokens[1])
            return f"{opcode:04X}{rd:01X}{0:011X}\n"
        
        elif fmt == 'RR':
            if len(tokens) < 3:
                raise ValueError(f"Formato RR requiere 2 registros: {instruction}")
            # Saltar comas
            reg_tokens = [t for t in tokens[1:] if t.type != 'COMMA']
            if len(reg_tokens) < 2:
                raise ValueError(f"Formato RR requiere 2 registros: {instruction}")
            rd = self.parse_register(reg_tokens[0])
            rs = self.parse_register(reg_tokens[1])
            return f"{opcode:04X}{0:010X}{rd:01X}{rs:01X}\n"
        
        elif fmt == 'RI':
            if len(tokens) < 3:
                raise ValueError(f"Formato RI requiere registro e inmediato: {instruction}")
            # Saltar comas
            operands = [t for t in tokens[1:] if t.type != 'COMMA']
            if len(operands) < 2:
                raise ValueError(f"Formato RI requiere registro e inmediato: {instruction}")
            rd = self.parse_register(operands[0])
            imm = self.parse_immediate(operands[1])
            if address:
                return f"{opcode:04X}{rd:01X}{0:011X}\n[{imm:016X}]\n"
            return f"{opcode:04X}{rd:01X}{0:011X}\n{imm:016X}\n"
        
        
        elif fmt == 'I':
            if len(tokens) < 2:
                raise ValueError(f"Formato I requiere inmediato: {instruction}")
            imm = self.parse_immediate(tokens[1])

            if address:
                return f"{opcode:04X}{0:012X}\n[{imm:016X}]\n"
            return f"{opcode:04X}{0:012X}\n{imm:016X}\n"
        
        else:
            raise ValueError(f"Formato desconocido: {fmt}")
    
    def assemble(self, code):
        """
        Ensambla código completo
        
        Args:
            code: Código fuente a ensamblar
        
        Returns:
            cadena de instrucciones en formato hexadecimal, {} referencias externas (Trabajo linker) [] direcciones relativas (Trabajo de cargador)
        """
        
        lines = code.split('\n')
        self.labels = {}
        self.current_address = 0
        
        # Primera pasada: recopilar etiquetas
        temp_address = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            # Passthrough .DATA and .LOCAL directives for loader; do not count them as instructions
            if line.upper().startswith('.DATA') or line.upper().startswith('.LOCAL'):
                # .DATA lines do not occupy instruction slots
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
                if IS[tokens[0].value]["format"] in ["RI", "I"]: ## Esto pq esos formatos usan dos bytes
                    temp_address += 1
                temp_address += 1
        
        # Segunda pasada: generar código
        program = []
        self.current_address = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            # Passthrough .DATA and .LOCAL directives to output unchanged
            if line.upper().startswith('.DATA') or line.upper().startswith('.LOCAL'):
                program.append(line + "\n")
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
        
        return "".join(program)
    

    ### TODO: RI y I formatos ahora sons instrucciones de 128 bits
    def disassemble_instruction(self, instr):
        """Desarma una instrucción a texto legible"""
        opcode = (instr >> 48) & 0xFFFF
        
        # Buscar el nombre de la instrucción
        instr_name = IS_INV.get(opcode)
        
        if not instr_name:
            return f"UNKNOWN {opcode:#06x}"
        
        fmt = instr_name.get("format")
        
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
        
        return f"UNKNOWN FORMAT for {instr_name}, fmt = {fmt}"


# =============================================
# EJEMPLO DE USO
# =============================================

def example():
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
    
    for i in program:
        print(i)


# -----------------------------
# Prueba (Powershell)
# run cat .\compiler\ejemplos\analizador_lex\1.txt | python .\compiler\preproccessor.py   | python .\compiler\lex_analizer.py 
# We must preproccess it firt
# -----------------------------
if __name__ == '__main__':
    import sys
    source = sys.stdin.read()

    assembler = Ensamblador()
    program = assembler.assemble(source)

    print(program)