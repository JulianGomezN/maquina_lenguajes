import ply.lex as lex
import os
import re

path_lib = "lib"

# --- Tokens ---
tokens = [
    'DIRECTIVE',
    'TEXT',
    'NEWLINE',
    'HASH'
]

# --- Lista de directivas reconocidas ---
directives = [
    'define',
    'include',
    'ifdef',
    'ifndef',
    'endif',
]

# --- Reglas de tokens ---
t_HASH = r'\#'
t_ignore = ' \t'

# Comentarios ignoramos todo
def t_COMMENT_LINE(t):
    r'//[^\n]*'
    pass

def t_COMMENT_BLOCK(t):
    r'/\*([^*]|\*+[^*/])*\*+/'
    pass

# Saltos de línea
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# Token para directivas (después del #)
def t_DIRECTIVE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value.lower() in directives:
        t.value = t.value.upper()
        return t
    # Si no es una directiva reconocida, se convierte en TEXT
    t.type = 'TEXT'
    return t

# Token de texto genérico (cualquier cosa que no sea espacio, salto, comentario, etc.)
def t_TEXT(t):
    r'[^\s#]+'
    return t

# Manejo de errores: simplemente ignorar cualquier cosa
def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

############################
# LOGICA DEL PREPROCESADOR #
############################

macros = {}
conditional_stack = []

def preprocess(code: str, base_path="."):
    ### Create a new lexer to preprocess so its posible to preprocess included files with no conflict
    lexer = lex.lex()
    lexer.input(code)
    result = []
    current_line = []

    for tok in lexer:
        
        if tok.type == 'NEWLINE':
            process_line(current_line, result, base_path)
            current_line = []
        else:
            current_line.append(tok)

    # Última línea si no terminó con \n
    if current_line:
        process_line(current_line, result, base_path)
    return ''.join(result)

def process_line(tokens, result, base_path):
    if not tokens:
        return

    # Ignorar bloques inactivos por #ifdef
    if conditional_stack and not conditional_stack[-1]:
        if tokens[0].type == 'HASH' and tokens[1].type in ('ENDIF', 'IFDEF', 'IFNDEF'):
            handle_directive(tokens, result, base_path)
        return

    if tokens[0].type == 'HASH':
        handle_directive(tokens, result, base_path)
    else:
        # Sustituir macros en código normal
        line = ' '.join(tok.value for tok in tokens)
        for name, value in macros.items():
            pattern = rf'\b{name}\b'       # solo cuando está delimitado
            line = re.sub(pattern, value, line)

        result.append(line + '\n')

def handle_directive(tokens, result, base_path):
    directive = tokens[1].value

    if directive == 'DEFINE':
        name = tokens[2].value
        value = ' '.join(tok.value for tok in tokens[3:] if tok.type != 'NEWLINE')
        macros[name] = value

    elif directive == 'INCLUDE':
        if tokens[2].value.startswith('<'):
            ##remove < >
            file = tokens[2].value.strip('<>')
            filename = os.path.join(path_lib,file)
        else:
            filename = tokens[2].value.strip('"')
        file_path = os.path.join(base_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                included_code = preprocess(f.read(), os.path.dirname(file_path))
                result.append(included_code)
            
            return
        except FileNotFoundError:
            print(f"[WARN] Archivo no encontrado: {filename}")

    elif directive == 'IFDEF':
        name = tokens[2].value
        conditional_stack.append(name in macros)

    elif directive == 'IFNDEF':
        name = tokens[2].value
        conditional_stack.append(name not in macros)

    elif directive == 'ENDIF':
        if conditional_stack:
            conditional_stack.pop()
        else:
            print("[WARN] #endif sin #ifdef/#ifndef")

    else:
        print(f"[WARN] Directiva desconocida: {directive}")


if __name__ == "__main__":
    import sys
    code = sys.stdin.read()
    lexer.input(code)

    result = preprocess(code)
    print(result)
