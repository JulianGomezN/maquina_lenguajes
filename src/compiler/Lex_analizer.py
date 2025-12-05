# lexer.py
import ply.lex as lex

# -----------------------------
# Palabras reservadas (keywords) con sus tokens
# -----------------------------
reserved = {
    'si': 'SI',
    'si_no': 'SI_NO',
    'si_no_si': 'SI_NO_SI',
    'mientras': 'MIENTRAS',
    'para': 'PARA',
    'romper': 'ROMPER',
    'continuar': 'CONTINUAR',
    'vacio': 'VACIO',
    'constante': 'CONSTANTE',
    'entero2': 'ENTERO2',
    'entero4': 'ENTERO4',
    'entero8': 'ENTERO8',
    'caracter': 'TIPO_CARACTER',
    'cadena': 'TIPO_CADENA',
    'con_signo': 'CON_SIGNO',
    'sin_signo': 'SIN_SIGNO',
    'flotante': 'FLOTANTE',
    'doble': 'DOBLE',
    'booleano': 'BOOLEANO',
    'funcion': 'FUNCION',
    'retornar': 'RETORNAR',
    'estructura': 'ESTRUCTURA',
    'externo': 'EXTERNO',
    'nuevo': 'NUEVO',
    'eliminar': 'ELIMINAR',
    'imprimir': 'IMPRIMIR',
}

# -----------------------------
# Lista de tokens
# -----------------------------
tokens = [
    # Identificadores y literales
    'ID',
    'ENTERO',
    'FLOT',
    'CARACTER',
    'CADENA',

    # Operadores compuestos (deben ir antes que operadores simples)
    'PLUSEQ', 'MINUSEQ', 'MULTEQ', 'DIVEQ', 'MODEQ',

    # Incremento/decremento
    'PLUSPLUS', 'MINUSMINUS',

    # Operadores aritméticos y bitwise
    'MAS', 'MENOS', 'MULT', 'DIV', 'MOD',
    'AND', 'OR', 'XOR', 'NOT',

    # Comparación
    'IGUAL', 'DISTINTO',
    'MENOR', 'MENORIGUAL', 'MAYOR', 'MAYORIGUAL',

    # Asignación simple
    'ASIGNAR',

    # Lógicos
    'ANDLOG', 'ORLOG',

    # Delimitadores
    'LLAVEIZQ', 'LLAVEDER',
    'PARIZQ', 'PARDER',
    'CORCHIZQ', 'CORCHDER',
    'PUNTOCOMA', 'COMA',

    # Acceso de miembros
    'PUNTO',
    'FLECHA'
] + list(reserved.values())  # Agregar tokens de palabras reservadas

# -----------------------------
# Reglas (tokens simples por regex)
# -----------------------------
# Operadores compuestos y tokens multicaracter (orden importa)
t_PLUSEQ      = r'\+\='
t_MINUSEQ     = r'\-\='
t_MULTEQ      = r'\*\='
t_DIVEQ       = r'\/\='
t_MODEQ       = r'\%\='

t_PLUSPLUS    = r'\+\+'
t_MINUSMINUS  = r'\-\-'

t_IGUAL       = r'=='
t_DISTINTO    = r'!='
t_MENORIGUAL  = r'<='
t_MAYORIGUAL  = r'>='

t_ANDLOG      = r'&&'
t_ORLOG       = r'\|\|'
t_FLECHA      = r'->'

# Operadores simples (debe venir después de los multicaracter)
t_ASIGNAR     = r'='
t_MAS         = r'\+'
t_MENOS       = r'-'
t_MULT        = r'\*'
t_DIV         = r'/'
t_MOD         = r'%'
t_AND         = r'&'
t_OR          = r'\|'
t_XOR         = r'\^'
t_NOT         = r'!'

t_MENOR       = r'<'
t_MAYOR       = r'>'

# Delimitadores
t_LLAVEIZQ    = r'\{'
t_LLAVEDER    = r'\}'
t_PARIZQ      = r'\('
t_PARDER      = r'\)'
t_CORCHIZQ    = r'\['
t_CORCHDER    = r'\]'
t_PUNTOCOMA   = r';'
t_COMA        = r','

t_PUNTO       = r'.'

# -----------------------------
# Reglas con función (más complejas)
# -----------------------------
# IMPORTANTE: El orden de las funciones determina la prioridad en PLY
# Los literales flotantes deben ir ANTES de ID para capturar f3.14 correctamente

# Punto flotante: f3.14, d2.5, 123.456, 1.23e+10, 1.23E-10
def t_FLOT(t):
    r'[fd]\d+\.\d*([eE][\-+]?\d+)?|[fd]\d*\.\d+([eE][\-+]?\d+)?|\d+\.\d*([eE][\-+]?\d+)?|\d*\.\d+([eE][\-+]?\d+)?'
    try:
        # Remover prefijo f o d si existe
        val = t.value
        if val and val[0] in ('f', 'd'):
            val = val[1:]
        t.value = float(val)
    except ValueError:
        print(f"Float value error {t.value}")
        t.value = 0.0
    return t

# Identificadores (y palabras reservadas)
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Verificar si es palabra reservada
    t.type = reserved.get(t.value, 'ID')
    return t

# Enteros: decimal u hexadecimal (sin signo en token)
def t_ENTERO(t):
    r'0[xX][0-9A-Fa-f]+|\d+'
    s = t.value
    if s[:2].lower() == '0x':
        t.value = int(s, 16)
    else:
        t.value = int(s, 10)
    return t

# Carácter: 'A' o '\n' (maneja escapes simples)
def t_CARACTER(t):
    r'\'(\\.|[^\\\'])\''
    # quitar las comillas y procesar escapes básicos
    raw = t.value[1:-1]
    # eval con cuidado: convertir secuencias escapadas a su char
    t.value = bytes(raw, "utf-8").decode("unicode_escape")
    return t

# Cadena: "texto" con escapes
def t_CADENA(t):
    r'\"(\\.|[^\\"])*\"'
    raw = t.value[1:-1]
    t.value = bytes(raw, "utf-8").decode("unicode_escape")
    return t

# Comentarios: multilínea /* ... */ y línea // ...

def t_COMMENT(t):
    r'(/\*(.|\n)*?\*/)|(//.*)'
    # Ignorar comentario: actualizar número de línea si contiene saltos
    t.lexer.lineno += t.value.count('\n')
    pass

# Saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Espacios y tabs a ignorar
t_ignore  = ' \t\r'

# Manejo de errores
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en la linea {t.lineno}")
    if t.value[0] == '#':
        print("Missing preprocesor ??")
    exit(1)
    t.lexer.skip(1)

# -----------------------------
# Construir el lexer
# -----------------------------
lexer = lex.lex()

# -----------------------------
# Prueba (Powershell)
# run cat .\compiler\ejemplos\analizador_lex\1.txt | python .\compiler\preprocessor.py | python .\compiler\lex_analizer.py
# We must preprocess it first 
# -----------------------------
if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    lexer.input(data)

    print(f"|{'TOKEN':^15}|{'VALOR / LEXEMA':^20}|{'LÍNEA':^10}|{'POSICIÓN':^10}|")
    print("-" * 60)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(f"|{tok.type:^15}|{str(tok.value):^20}|{tok.lineno:^10}|{tok.lexpos:^10}|")
        print("-" * 60)
