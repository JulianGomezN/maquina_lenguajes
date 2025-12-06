#!/usr/bin/env python3
"""
Test para verificar el límite de 10 elif
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import SemanticAnalyzer

def test_limite_elif():
    """Test que verifica que se rechace más de 10 elif"""
    
    # Generar código con 11 elif (debe fallar)
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 100) {
            x = 1;
        }"""
    
    # Agregar 11 elif
    for i in range(11):
        code += f""" si_no_si (x > {100 - (i+1)*9}) {{
            x = {i+2};
        }}"""
    
    code += """
        si_no {
            x = 99;
        }
    }
    """
    
    print("Test: Verificar límite de 10 elif")
    print(f"Generando código con 11 elif (debe fallar)...\n")
    
    # Parse del código
    ast = parse(code)
    if ast is None:
        print("❌ Error: No se pudo parsear el código")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    print(f"✓ Parsing exitoso: {len(if_stmt.elif_clauses)} elif detectados")
    
    # Análisis semántico (debe detectar el error)
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        print("❌ Error: El análisis semántico NO detectó el exceso de elif")
        return False
    
    # Verificar que el error sea el correcto
    if len(analyzer.errors) == 0:
        print("❌ Error: No se generó mensaje de error")
        return False
    
    error_msg = analyzer.errors[0]
    if "10 cláusulas 'si_no_si'" in error_msg:
        print(f"✓ Error detectado correctamente: {error_msg}")
        return True
    else:
        print(f"❌ Error incorrecto: {error_msg}")
        return False

def test_limite_correcto():
    """Test que verifica que 10 elif exactos sí funcione"""
    
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 100) {
            x = 1;
        }"""
    
    # Agregar exactamente 10 elif
    for i in range(10):
        code += f""" si_no_si (x > {100 - (i+1)*9}) {{
            x = {i+2};
        }}"""
    
    code += """
        si_no {
            x = 99;
        }
    }
    """
    
    print("\nTest: Verificar que 10 elif funcione correctamente")
    print(f"Generando código con 10 elif (debe funcionar)...\n")
    
    # Parse del código
    ast = parse(code)
    if ast is None:
        print("❌ Error: No se pudo parsear el código")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    print(f"✓ Parsing exitoso: {len(if_stmt.elif_clauses)} elif detectados")
    
    # Análisis semántico (debe pasar sin errores)
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if not success:
        print(f"❌ Error: El análisis semántico falló: {analyzer.errors}")
        return False
    
    print("✓ Análisis semántico exitoso: 10 elif permitidos")
    return True

def main():
    print("=== Test de Límite de elif ===\n")
    
    test1 = test_limite_elif()
    test2 = test_limite_correcto()
    
    print("\n=== Resultados ===")
    if test1 and test2:
        print("✓ Todos los tests pasaron")
        print("✓ El límite de 10 elif funciona correctamente")
        return 0
    else:
        print("❌ Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
