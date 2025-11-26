#!/usr/bin/env python
# test_simple.py
# Script simple para probar el analizador semántico

import sys
import os

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Directorio actual: {current_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    from compiler.syntax_analizer import parse
    print("[OK] Import de syntax_analizer exitoso")
except Exception as e:
    print(f"[ERROR] No se pudo importar syntax_analizer: {e}")
    sys.exit(1)

try:
    from compiler.semantic_analyzer import analyze
    print("[OK] Import de semantic_analyzer exitoso")
except Exception as e:
    print(f"[ERROR] No se pudo importar semantic_analyzer: {e}")
    sys.exit(1)

try:
    from compiler.compiler import compile_code
    print("[OK] Import de compiler exitoso")
except Exception as e:
    print(f"[ERROR] No se pudo importar compiler: {e}")
    sys.exit(1)

# Prueba simple
code = """
funcion vacio principal() {
    entero4 x = 10;
}
"""

print("\n=== Probando compilación ===")
ast, success, errors = compile_code(code)

if success:
    print("[OK] Compilación exitosa")
else:
    print(f"[ERROR] Errores: {errors}")

