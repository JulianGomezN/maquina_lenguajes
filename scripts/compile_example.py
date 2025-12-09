import sys, os
# Ensure src is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import generate_code

example_path = os.path.join(ROOT, 'Algoritmos', 'Ejemplos_alto_nivel', 'ejemplo_elif_simple.txt')
with open(example_path, 'r', encoding='utf-8') as f:
    code = f.read()

print('--- Parsing ---')
ast = parse(code)
if not ast:
    print('Parsing failed')
    sys.exit(1)

print('--- Semantic Analysis ---')
analyzer = SemanticAnalyzer()
success = analyzer.analyze(ast)
if analyzer.errors:
    print('Semantic errors:')
    for e in analyzer.errors:
        print(e)

print('--- Generating Assembly ---')
asm = generate_code(ast, analyzer.symbol_table)
print(asm)

# Save assembly for inspection
outpath = os.path.join(ROOT, 'debug_example_output.asm')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(asm)
print(f'Assembly written to {outpath}')
