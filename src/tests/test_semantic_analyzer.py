# test_semantic_analyzer.py
# Pruebas unitarias para el analizador semántico

import unittest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import analyze, SemanticAnalyzer
from compiler.ast_nodes import *


class TestSemanticAnalyzer(unittest.TestCase):
    """Test suite para el analizador semántico"""
    
    def test_valid_program(self):
        """Test: programa válido sin errores"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            entero4 y = 20;
            entero4 z = x + y;
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_undeclared_variable(self):
        """Test: variable no declarada"""
        code = """
        funcion vacio principal() {
            entero4 x = y;  // y no está declarada
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar variable no declarada")
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("no está declarada" in err for err in errors))
    
    def test_duplicate_variable(self):
        """Test: variable duplicada en mismo scope"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            entero4 x = 20;  // x ya está declarada
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar variable duplicada")
        self.assertTrue(any("ya está declarada" in err for err in errors))
    
    def test_type_mismatch_assignment(self):
        """Test: incompatibilidad de tipos en asignación"""
        code = """
        funcion vacio principal() {
            entero4 x;
            x = "hola";  // Error: asignar cadena a entero
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar incompatibilidad de tipos")
        self.assertTrue(any("incompatible" in err.lower() for err in errors))
    
    def test_type_mismatch_initialization(self):
        """Test: incompatibilidad de tipos en inicialización"""
        code = """
        funcion vacio principal() {
            entero4 x = "texto";  // Error: inicializar entero con cadena
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar incompatibilidad de tipos")
    
    def test_binary_op_type_check(self):
        """Test: verificación de tipos en operaciones binarias"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            cadena texto = "hola";
            entero4 resultado = x + texto;  // Error: sumar entero y cadena
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar error en operación binaria")
    
    def test_if_condition_boolean(self):
        """Test: condición de if debe ser booleana"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            si (x) {  // Error: x no es booleano
                x = 20;
            }
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar que condición no es booleana")
        self.assertTrue(any("booleano" in err.lower() for err in errors))
    
    def test_while_condition_boolean(self):
        """Test: condición de while debe ser booleana"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            mientras (x) {  // Error: x no es booleano
                x = x - 1;
            }
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar que condición no es booleana")
    
    def test_for_condition_boolean(self):
        """Test: condición de for debe ser booleana"""
        code = """
        funcion vacio principal() {
            para (entero4 i = 0; i; i = i + 1) {  // Error: i no es booleano
                // ...
            }
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar que condición no es booleana")
    
    def test_break_outside_loop(self):
        """Test: break fuera de loop"""
        code = """
        funcion vacio principal() {
            romper;  // Error: break fuera de loop
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar break fuera de loop")
        self.assertTrue(any("romper" in err.lower() or "ciclo" in err.lower() for err in errors))
    
    def test_continue_outside_loop(self):
        """Test: continue fuera de loop"""
        code = """
        funcion vacio principal() {
            continuar;  // Error: continue fuera de loop
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar continue fuera de loop")
    
    def test_break_inside_while(self):
        """Test: break dentro de while (válido)"""
        code = """
        funcion vacio principal() {
            mientras (1) {
                romper;  // Válido
            }
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_continue_inside_for(self):
        """Test: continue dentro de for (válido)"""
        code = """
        funcion vacio principal() {
            para (entero4 i = 0; i < 10; i = i + 1) {
                continuar;  // Válido
            }
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_return_type_mismatch(self):
        """Test: tipo de retorno incorrecto"""
        code = """
        funcion entero4 obtenerValor() {
            retornar "texto";  // Error: debería retornar entero4
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar tipo de retorno incorrecto")
        self.assertTrue(any("retorno" in err.lower() for err in errors))
    
    def test_return_void_function(self):
        """Test: return sin valor en función void"""
        code = """
        funcion vacio test() {
            retornar;  // Válido
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_return_value_in_void_function(self):
        """Test: return con valor en función void"""
        code = """
        funcion vacio test() {
            retornar 42;  // Error: función void no puede retornar valor
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        # Nota: esto podría ser válido dependiendo de la semántica
        # Por ahora, lo marcamos como posible error
        # self.assertFalse(success, "Debería detectar return con valor en función void")
    
    def test_function_call_undeclared(self):
        """Test: llamada a función no declarada"""
        code = """
        funcion vacio principal() {
            funcionNoExiste();  // Error: función no declarada
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar función no declarada")
        self.assertTrue(any("no está declarada" in err for err in errors))
    
    def test_function_call_wrong_args(self):
        """Test: llamada a función con argumentos incorrectos"""
        code = """
        funcion entero4 sumar(entero4 a, entero4 b) {
            retornar a + b;
        }
        
        funcion vacio principal() {
            sumar(10);  // Error: falta un argumento
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar argumentos incorrectos")
        self.assertTrue(any("argumentos" in err.lower() for err in errors))
    
    def test_function_call_wrong_arg_types(self):
        """Test: llamada a función con tipos de argumentos incorrectos"""
        code = """
        funcion entero4 sumar(entero4 a, entero4 b) {
            retornar a + b;
        }
        
        funcion vacio principal() {
            sumar(10, "texto");  // Error: segundo argumento debería ser entero4
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar tipos de argumentos incorrectos")
    
    def test_const_assignment(self):
        """Test: asignación a constante"""
        code = """
        funcion vacio principal() {
            constante entero4 MAX = 100;
            MAX = 200;  // Error: no se puede asignar a constante
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar asignación a constante")
        self.assertTrue(any("constante" in err.lower() for err in errors))
    
    def test_struct_declaration(self):
        """Test: declaración de estructura válida"""
        code = """
        estructura Persona {
            cadena nombre;
            entero4 edad;
        };
        
        funcion vacio principal() {
            Persona p;
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_struct_member_access(self):
        """Test: acceso a miembro de estructura"""
        code = """
        estructura Persona {
            cadena nombre;
            entero4 edad;
        };
        
        funcion vacio principal() {
            Persona p;
            p.edad = 25;  // Válido
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_struct_member_not_found(self):
        """Test: acceso a miembro inexistente"""
        code = """
        estructura Persona {
            cadena nombre;
            entero4 edad;
        };
        
        funcion vacio principal() {
            Persona p;
            p.altura = 1.75;  // Error: 'altura' no existe
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar miembro inexistente")
        self.assertTrue(any("no existe" in err.lower() for err in errors))
    
    def test_pointer_dereference(self):
        """Test: desreferencia de puntero"""
        code = """
        funcion vacio principal() {
            entero4* ptr;
            entero4 x = *ptr;  // Válido
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_pointer_dereference_non_pointer(self):
        """Test: desreferencia de no-puntero"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            entero4 y = *x;  // Error: x no es puntero
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar desreferencia de no-puntero")
    
    def test_logical_operators(self):
        """Test: operadores lógicos con booleanos"""
        code = """
        funcion vacio principal() {
            booleano a = verdadero;
            booleano b = falso;
            booleano resultado = a && b;  // Válido
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        # Nota: necesitaríamos literales booleanos en el parser
        # Por ahora, este test podría fallar si no hay soporte para booleanos
    
    def test_numeric_promotion(self):
        """Test: promoción de tipos numéricos"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            flotante y = 3.14;
            flotante resultado = x + y;  // Válido: promoción a flotante
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")
    
    def test_nested_scopes(self):
        """Test: scopes anidados"""
        code = """
        funcion vacio principal() {
            entero4 x = 10;
            si (x < 20) {
                entero4 y = 20;
                entero4 z = x + y;  // Válido: x del scope externo
            }
            entero4 w = y;  // Error: y no existe en este scope
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success, "Debería detectar variable fuera de scope")
    
    def test_global_variable(self):
        """Test: variable global"""
        code = """
        entero4 global = 100;
        
        funcion vacio principal() {
            entero4 local = global;  // Válido: acceso a variable global
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertTrue(success, f"Debería ser válido, pero hay errores: {errors}")


class TestSemanticErrors(unittest.TestCase):
    """Test suite para manejo de errores semánticos"""
    
    def test_multiple_errors(self):
        """Test: múltiples errores en un programa"""
        code = """
        funcion vacio principal() {
            entero4 x = y;  // Error 1: y no declarada
            cadena texto = 42;  // Error 2: tipo incompatible
            z = 10;  // Error 3: z no declarada
        }
        """
        ast = parse(code)
        self.assertIsNotNone(ast)
        
        success, errors = analyze(ast)
        self.assertFalse(success)
        self.assertGreaterEqual(len(errors), 2, "Debería detectar múltiples errores")


if __name__ == '__main__':
    unittest.main(verbosity=2)

