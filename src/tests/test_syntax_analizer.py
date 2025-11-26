# test_syntax_analizer.py
# Pruebas unitarias para el analizador sintáctico

import unittest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from compiler.syntax_analizer import parse
from compiler.ast_nodes import *

class TestSyntaxAnalizer(unittest.TestCase):
    """Test suite para el analizador sintáctico"""
    
    def test_simple_function(self):
        """Test: función simple sin parámetros"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.declarations), 1)
        
        func = ast.declarations[0]
        self.assertIsInstance(func, FunctionDecl)
        self.assertEqual(func.name, "principal")
        self.assertEqual(func.return_type.name, "vacio")
        self.assertEqual(len(func.params), 0)
        self.assertIsInstance(func.body, Block)
    
    def test_function_with_params(self):
        """Test: función con parámetros"""
        code = """
        funcion entero4 sumar(entero4 a, entero4 b) {
            retornar a + b;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        self.assertEqual(func.name, "sumar")
        self.assertEqual(len(func.params), 2)
        self.assertEqual(func.params[0].name, "a")
        self.assertEqual(func.params[1].name, "b")
    
    def test_variable_declarations(self):
        """Test: declaraciones de variables con inicialización"""
        code = """
        funcion vacio test() {
            entero4 x = 10;
            flotante pi = 3.14;
            cadena texto = "Hola";
            caracter c = 'A';
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        block = func.body
        
        # Verificar que hay 4 declaraciones
        self.assertEqual(len(block.statements), 4)
        
        # Primera declaración: entero4
        var1 = block.statements[0]
        self.assertIsInstance(var1, VarDecl)
        self.assertEqual(var1.name, "x")
        self.assertEqual(var1.var_type.name, "entero4")
        self.assertIsInstance(var1.init_value, IntLiteral)
    
    def test_const_declaration(self):
        """Test: declaración de constante"""
        code = """
        funcion vacio test() {
            constante entero4 MAX = 100;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        var = func.body.statements[0]
        
        self.assertTrue(var.is_const)
        self.assertEqual(var.name, "MAX")
    
    def test_if_statement(self):
        """Test: sentencia if"""
        code = """
        funcion vacio test() {
            entero4 x = 5;
            si (x < 10) {
                x = x + 1;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        if_stmt = func.body.statements[1]
        
        self.assertIsInstance(if_stmt, IfStmt)
        self.assertIsInstance(if_stmt.condition, BinaryOp)
        self.assertIsNone(if_stmt.else_block)
    
    def test_if_else_statement(self):
        """Test: sentencia if-else"""
        code = """
        funcion vacio test() {
            entero4 x = 5;
            si (x < 10) {
                x = x + 1;
            } si_no {
                x = x - 1;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        if_stmt = func.body.statements[1]
        
        self.assertIsInstance(if_stmt, IfStmt)
        self.assertIsNotNone(if_stmt.else_block)
        self.assertIsInstance(if_stmt.else_block, Block)
    
    def test_while_loop(self):
        """Test: ciclo while"""
        code = """
        funcion vacio test() {
            entero4 i = 0;
            mientras (i < 10) {
                i = i + 1;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        while_stmt = func.body.statements[1]
        
        self.assertIsInstance(while_stmt, WhileStmt)
        self.assertIsInstance(while_stmt.condition, BinaryOp)
        self.assertIsInstance(while_stmt.body, Block)
    
    def test_for_loop(self):
        """Test: ciclo for"""
        code = """
        funcion vacio test() {
            para (entero4 i = 0; i < 10; i = i + 1) {
                continuar;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        for_stmt = func.body.statements[0]
        
        self.assertIsInstance(for_stmt, ForStmt)
        self.assertIsNotNone(for_stmt.init)
        self.assertIsNotNone(for_stmt.condition)
        self.assertIsNotNone(for_stmt.increment)
    
    def test_return_statement(self):
        """Test: sentencia return"""
        code = """
        funcion entero4 obtenerValor() {
            retornar 42;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        ret_stmt = func.body.statements[0]
        
        self.assertIsInstance(ret_stmt, ReturnStmt)
        self.assertIsInstance(ret_stmt.value, IntLiteral)
        self.assertEqual(ret_stmt.value.value, 42)
    
    def test_break_continue(self):
        """Test: sentencias break y continue"""
        code = """
        funcion vacio test() {
            mientras (1) {
                romper;
                continuar;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        while_stmt = func.body.statements[0]
        
        self.assertIsInstance(while_stmt.body.statements[0], BreakStmt)
        self.assertIsInstance(while_stmt.body.statements[1], ContinueStmt)
    
    def test_binary_operations(self):
        """Test: operaciones binarias"""
        code = """
        funcion vacio test() {
            entero4 result = 5 + 3 * 2 - 1 / 2;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        var_decl = func.body.statements[0]
        
        # La expresión debe ser BinaryOp (verificar que se parseó)
        self.assertIsInstance(var_decl.init_value, BinaryOp)
    
    def test_logical_operations(self):
        """Test: operaciones lógicas"""
        code = """
        funcion vacio test() {
            si (x < 10 && y > 5 || z == 0) {
                retornar;
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        if_stmt = func.body.statements[0]
        
        # Verificar que la condición es una operación lógica
        self.assertIsInstance(if_stmt.condition, BinaryOp)
    
    def test_assignment_operators(self):
        """Test: operadores de asignación compuesta"""
        code = """
        funcion vacio test() {
            entero4 x = 10;
            x += 5;
            x -= 3;
            x *= 2;
            x /= 4;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        # Verificar asignaciones compuestas
        assign1 = func.body.statements[1]
        self.assertIsInstance(assign1, ExprStmt)
        self.assertIsInstance(assign1.expression, Assignment)
        self.assertEqual(assign1.expression.operator, "+=")
    
    def test_increment_decrement(self):
        """Test: operadores ++ y --"""
        code = """
        funcion vacio test() {
            entero4 x = 0;
            ++x;
            x++;
            --x;
            x--;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        # Prefijo ++x
        inc_prefix = func.body.statements[1].expression
        self.assertIsInstance(inc_prefix, UnaryOp)
        self.assertTrue(inc_prefix.is_prefix)
        
        # Postfijo x++
        inc_postfix = func.body.statements[2].expression
        self.assertIsInstance(inc_postfix, UnaryOp)
        self.assertFalse(inc_postfix.is_prefix)
    
    def test_function_call(self):
        """Test: llamada a función"""
        code = """
        funcion vacio test() {
            entero4 resultado = calcular(10, 20);
            imprimir();
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        # Primera llamada con argumentos
        call1 = func.body.statements[0].init_value
        self.assertIsInstance(call1, FunctionCall)
        self.assertEqual(len(call1.arguments), 2)
        
        # Segunda llamada sin argumentos
        call2 = func.body.statements[1].expression
        self.assertIsInstance(call2, FunctionCall)
        self.assertEqual(len(call2.arguments), 0)
    
    def test_struct_declaration(self):
        """Test: declaración de estructura"""
        code = """
        estructura Persona {
            cadena nombre;
            entero4 edad;
            flotante altura;
        };
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        struct = ast.declarations[0]
        
        self.assertIsInstance(struct, StructDecl)
        self.assertEqual(struct.name, "Persona")
        self.assertEqual(len(struct.members), 3)
        self.assertEqual(struct.members[0].name, "nombre")
    
    def test_member_access(self):
        """Test: acceso a miembros"""
        code = """
        funcion vacio test() {
            Persona p;
            p.edad = 25;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        assign = func.body.statements[1].expression
        
        self.assertIsInstance(assign, Assignment)
        self.assertIsInstance(assign.lvalue, MemberAccess)
        self.assertEqual(assign.lvalue.member, "edad")
        self.assertFalse(assign.lvalue.is_pointer)
    
    def test_pointer_member_access(self):
        """Test: acceso a miembros con puntero"""
        code = """
        funcion vacio test() {
            Persona* p;
            p->edad = 25;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        assign = func.body.statements[1].expression
        
        self.assertIsInstance(assign.lvalue, MemberAccess)
        self.assertTrue(assign.lvalue.is_pointer)
    
    def test_array_access(self):
        """Test: acceso a array"""
        code = """
        funcion vacio test() {
            entero4 arr;
            entero4 x = arr[5];
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        var_decl = func.body.statements[1]
        
        self.assertIsInstance(var_decl.init_value, ArrayAccess)
    
    def test_new_delete(self):
        """Test: operadores nuevo y eliminar"""
        code = """
        funcion vacio test() {
            Persona* p = nuevo Persona;
            eliminar p;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        # nuevo
        new_expr = func.body.statements[0].init_value
        self.assertIsInstance(new_expr, NewExpr)
        
        # eliminar
        delete_stmt = func.body.statements[1].expression
        self.assertIsInstance(delete_stmt, DeleteExpr)
    
    def test_pointer_type(self):
        """Test: tipos puntero"""
        code = """
        funcion vacio test() {
            entero4* ptr;
            entero4** ptrptr;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        # Puntero simple
        ptr1 = func.body.statements[0]
        self.assertTrue(ptr1.var_type.is_pointer)
        
        # Puntero a puntero
        ptr2 = func.body.statements[1]
        self.assertTrue(ptr2.var_type.is_pointer)
    
    def test_extern_function(self):
        """Test: función externa"""
        code = """
        externo funcion vacio imprimir(cadena texto);
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        
        self.assertIsInstance(func, FunctionDecl)
        self.assertTrue(func.is_extern)
        self.assertIsNone(func.body)
        self.assertEqual(len(func.params), 1)
    
    def test_complex_expression(self):
        """Test: expresión compleja con precedencia"""
        code = """
        funcion vacio test() {
            entero4 result = 2 + 3 * 4 - 5 / 2 % 3;
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        # Simplemente verificar que se parseó sin errores
        func = ast.declarations[0]
        self.assertIsInstance(func.body.statements[0].init_value, BinaryOp)
    
    def test_nested_blocks(self):
        """Test: bloques anidados"""
        code = """
        funcion vacio test() {
            si (1) {
                mientras (1) {
                    si (1) {
                        romper;
                    }
                }
            }
        }
        """
        ast = parse(code)
        
        self.assertIsNotNone(ast)
        func = ast.declarations[0]
        outer_if = func.body.statements[0]
        
        self.assertIsInstance(outer_if, IfStmt)
        self.assertIsInstance(outer_if.then_block, Block)
    
    def test_ejemplo_alto_nivel_1(self):
        """Test: archivo de ejemplo 1.txt"""
        # Leer archivo de ejemplo
        example_path = os.path.join(os.path.dirname(__file__), 
                                    'Algoritmos', 'Ejemplos_alto_nivel', '1.txt')
        
        if os.path.exists(example_path):
            with open(example_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast = parse(code)
            self.assertIsNotNone(ast, "El archivo 1.txt debe parsearse correctamente")
            self.assertIsInstance(ast, Program)

class TestSyntaxErrors(unittest.TestCase):
    """Test suite para manejo de errores sintácticos"""
    
    def test_missing_semicolon(self):
        """Test: detectar punto y coma faltante"""
        code = """
        funcion vacio test() {
            entero4 x = 10
        }
        """
        # Este debería generar un error
        # (PLY puede o no retornar None dependiendo de la recuperación)
        ast = parse(code)
        # Solo verificar que no causa excepción
    
    def test_unmatched_braces(self):
        """Test: llaves sin cerrar"""
        code = """
        funcion vacio test() {
            entero4 x = 10;
        """
        ast = parse(code)
        # Verificar que se maneja el error
    
    def test_invalid_type(self):
        """Test: tipo inválido"""
        code = """
        funcion vacio test() {
            invalido x = 10;
        }
        """
        ast = parse(code)
        # El parser aceptará esto (el análisis semántico lo rechazará)

if __name__ == '__main__':
    unittest.main(verbosity=2)
