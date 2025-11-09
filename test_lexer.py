from compiler.lex_analizer import lexer  
from compiler.preprocessor import preprocess
# Lee un archivo de prueba

## 1 to 3
file = "Algoritmos/Ejemplos_alto_nivel/1.txt"

with open(file, "r", encoding="utf-8") as f:
    data = f.read()

# Preprocesar primero
data = preprocess(data)
# Enviar el contenido al lexer
lexer.input(data)

# Imprimir encabezado
print(f"|{'TOKEN':^15}|{'VALOR / LEXEMA':^20}|{'LÍNEA':^10}|{'POSICIÓN':^10}|")
print("-" * 60)

# Leer e imprimir tokens
while True:
    tok = lexer.token()
    if not tok:
        break
    print(f"|{tok.type:^15}|{str(tok.value):^20}|{tok.lineno:^10}|{tok.lexpos:^10}|")
    print("-" * 60)