import ply.lex as lex

tokens = (
    'LABEL',
    'JUMP',
    'INSTRUCTION',
    'NUMBER',
    'REGISTER',
    'COMMA',
    'ID'
)

jump_instructions = {
    'JMP', 'JEQ', 'JNE', 'JLT', 'JGE', 'JCS', 'JCC', 'JMI', 'JPL'
}

t_COMMA = r','

def t_LABEL(t):
    r'[A-Za-z_][A-Za-z0-9_]*:'
    t.value = t.value[:-1]
    return t

def t_REGISTER(t):
    r'R[0-9]+'
    return t

def t_NUMBER(t):
    r'(0x[0-9A-Fa-f]+|\d+)'
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value.upper() in jump_instructions:
        t.type = 'JUMP'
    else:
        t.type = 'INSTRUCTION'
    return t

t_ignore_COMMENT = r';[^\n]*'
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal: {t.value[0]}")
    t.lexer.skip(1)


class ensamblador:
    def __init__(self, code):
        self.code = code.splitlines()
        self.lexer = lex.lex()
        self.symbols = {}    # Lista de etiquetas y sus direcciones
        self.program = []    
        self.pc = 0          # Program counter

    # Primera pasada: guarda las etiquetas y el valor de su direción
    def first_pass(self):
        for line in self.code:
            self.lexer.input(line)
            tokens_line = list(self.lexer)
            if not tokens_line:
                continue

            if tokens_line[0].type == 'LABEL':
                label_name = tokens_line[0].value
                self.symbols[label_name] = self.pc
                tokens_line = tokens_line[1:]

            if not tokens_line:
                continue

            first_token = tokens_line[0]
            if first_token.type in ('INSTRUCTION', 'JUMP'):
                self.pc += 1  # aumentar una unidad de instrución

            self.program.append(tokens_line)

    # second_pass: reemplazar etiquetas en saltos
    def second_pass(self):
        output = []
        for tokens_line in self.program:
            if not tokens_line:
                continue

            first = tokens_line[0]
            if first.type == 'JUMP':
                instr = first.value
                dest_label = tokens_line[1].value
                if dest_label in self.symbols:
                    addr = self.symbols[dest_label]
                    output.append(f"{instr} {{{addr}}}")
                else:
                    output.append(f"{instr} {{ {dest_label} }}; [Etiqueta no encontrada]")
            elif first.type == 'INSTRUCTION':
                # imprime las otras instrucciones
                text = " ".join(tok.value for tok in tokens_line)
                output.append(text)
        return output

    def assemble(self):
        self.first_pass()
        result = self.second_pass()
        return result

# -----------------------------
# =========Ejemplo ============
# -----------------------------

if __name__ == "__main__":

    source = '''

        ; Cargar operandos a₀ y b₀
        LOADV R1, 1071      ; a₀ = 1071
        STOREV R1, 375      ; Guardar en posición 375

        LOADV R2, 462       ; b₀ = 462
        STOREV R2, 1535     ; Guardar en posición 1535

        ; Inicializar variables: a := a₀; b := b₀
        LOAD R1, 375        ; R1 = a = a₀
        LOAD R2, 1535       ; R2 = b = b₀

        ; mientras a ≠ b hacer
        MIENTRAS:
        CMP R1, R2          ; Comparar a con b
        JEQ FIN_MIENTRAS    ; Si a = b, salir del bucle

        ; caso a > b → a := a - b
        CMP R1, R2          ; Comparar a con b
        JLT CASO_B_MAYOR    ; Si a < b, ir a caso b > a
        SUB R1, R2          ; a := a - b (caso a > b)
        JMP MIENTRAS        ; Volver al inicio del bucle

        ; [] a < b → b := b - a  
        CASO_B_MAYOR:
        SUB R2, R1          ; b := b - a
        JMP MIENTRAS        ; Volver al inicio del bucle

        ; fmientras
        FIN_MIENTRAS:
        ; dev a (el resultado está en R1)
        STOREV R1, 7478     ; Guardar resultado en posición 7478

        ; Mostrar resultado por dispositivo de salida
        LOAD R15, 7478
        SVIO R15, 7478
        SHOWIO 7478

        PARAR
    '''

    assembler = ensamblador(source)
    output = assembler.assemble()

    print("Tabla de símbolos:")
    for k, v in assembler.symbols.items():
        print(f"  {k:20s} → {v}")

    print("\nCódigo ensamblado:")
    for line in output:
        print(line)
