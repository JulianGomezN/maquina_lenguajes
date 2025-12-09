#!/usr/bin/env python3
"""
Test básico para verificar el funcionamiento del condicional si-no-si (elif)
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from compiler.Lex_analizer import lexer
from compiler.syntax_analizer import parse
from compiler.ast_nodes import IfStmt, ElifClause

def test_elif_simple():
    """Test con un elif simple"""
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 20) {
            x = 1;
        } si_no_si (x > 10) {
            x = 2;
        } si_no {
            x = 3;
        }
    }
    """
    
    print("Test 1: elif simple")
    ast = parse(code)
    if ast is None:
        print("❌ Error: AST es None")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    if not isinstance(if_stmt, IfStmt):
        print(f"❌ Error: Esperado IfStmt, obtenido {type(if_stmt)}")
        return False
    
    if len(if_stmt.elif_clauses) != 1:
        print(f"❌ Error: Esperado 1 elif, obtenido {len(if_stmt.elif_clauses)}")
        return False
    
    if not isinstance(if_stmt.elif_clauses[0], ElifClause):
        print(f"❌ Error: elif_clause no es ElifClause")
        return False
    
    if if_stmt.else_block is None:
        print(f"❌ Error: else_block es None")
        return False
    
    print("✓ Test 1 pasado")
    return True

def test_elif_multiple():
    """Test con múltiples elif"""
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 30) {
            x = 1;
        } si_no_si (x > 20) {
            x = 2;
        } si_no_si (x > 10) {
            x = 3;
        } si_no_si (x > 5) {
            x = 4;
        } si_no {
            x = 5;
        }
    }
    """
    
    print("Test 2: múltiples elif")
    ast = parse(code)
    if ast is None:
        print("❌ Error: AST es None")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    if len(if_stmt.elif_clauses) != 3:
        print(f"❌ Error: Esperado 3 elif, obtenido {len(if_stmt.elif_clauses)}")
        return False
    
    print("✓ Test 2 pasado")
    return True

def test_elif_sin_else():
    """Test con elif pero sin else final"""
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 20) {
            x = 1;
        } si_no_si (x > 10) {
            x = 2;
        }
    }
    """
    
    print("Test 3: elif sin else")
    ast = parse(code)
    if ast is None:
        print("❌ Error: AST es None")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    if len(if_stmt.elif_clauses) != 1:
        print(f"❌ Error: Esperado 1 elif, obtenido {len(if_stmt.elif_clauses)}")
        return False
    
    if if_stmt.else_block is not None:
        print(f"❌ Error: else_block debería ser None")
        return False
    
    print("✓ Test 3 pasado")
    return True

def test_if_tradicional():
    """Test que el if-else tradicional sigue funcionando"""
    code = """
    funcion vacio test() {
        entero4 x = 10;
        si (x > 10) {
            x = 1;
        } si_no {
            x = 2;
        }
    }
    """
    
    print("Test 4: if-else tradicional")
    ast = parse(code)
    if ast is None:
        print("❌ Error: AST es None")
        return False
    
    func = ast.declarations[0]
    if_stmt = func.body.statements[1]
    
    if len(if_stmt.elif_clauses) != 0:
        print(f"❌ Error: Esperado 0 elif, obtenido {len(if_stmt.elif_clauses)}")
        return False
    
    if if_stmt.else_block is None:
        print(f"❌ Error: else_block no debería ser None")
        return False
    
    print("✓ Test 4 pasado")
    return True

def main():
    print("=== Tests de si-no-si (elif) ===\n")
    
    tests = [
        test_elif_simple,
        test_elif_multiple,
        test_elif_sin_else,
        test_if_tradicional
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Error en test: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print(f"=== Resultados ===")
    print(f"✓ Pasados: {passed}")
    print(f"❌ Fallidos: {failed}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
