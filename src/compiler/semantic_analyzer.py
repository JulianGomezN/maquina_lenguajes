# semantic_analyzer.py
# Analizador Semántico - Valida tipos, scopes, y reglas semánticas

from compiler.symbol_table import SymbolTable, Symbol
from compiler.ast_nodes import *

class SemanticError(Exception):
    """Excepción para errores semánticos"""
    def __init__(self, message, lineno=None):
        self.message = message
        self.lineno = lineno
        super().__init__(f"Error semántico en línea {lineno}: {message}" if lineno else f"Error semántico: {message}")


class SemanticAnalyzer:
    """Analizador semántico que valida el AST"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.structs = {}  # name -> StructDecl
        self.functions = {}  # name -> FunctionDecl
    
    def error(self, message, lineno=None):
        """Registra un error semántico"""
        err_msg = f"Error semántico en línea {lineno}: {message}" if lineno else f"Error semántico: {message}"
        self.errors.append(err_msg)
        print(err_msg)
    
    def analyze(self, ast):
        """
        Analiza el AST completo
        
        Returns:
            bool: True si no hay errores, False si hay errores
        """
        if not isinstance(ast, Program):
            self.error("El AST raíz debe ser un Program", None)
            return False
        
        # Primera pasada: declarar structs y funciones
        for decl in ast.declarations:
            if isinstance(decl, StructDecl):
                self._declare_struct(decl)
            elif isinstance(decl, FunctionDecl):
                self._declare_function(decl)
        
        # Segunda pasada: analizar declaraciones
        for decl in ast.declarations:
            if isinstance(decl, StructDecl):
                self._analyze_struct(decl)
            elif isinstance(decl, FunctionDecl):
                self._analyze_function(decl)
            elif isinstance(decl, VarDecl):
                self._analyze_global_var(decl)
        
        return len(self.errors) == 0
    
    # ============================================
    # DECLARACIÓN DE ESTRUCTURAS
    # ============================================
    
    def _declare_struct(self, struct_decl):
        """Primera pasada: declarar estructura"""
        if struct_decl.name in self.structs:
            self.error(f"Estructura '{struct_decl.name}' ya está declarada", struct_decl.lineno)
            return
        
        self.structs[struct_decl.name] = struct_decl
        
        # Crear tipo para la estructura
        struct_type = Type(struct_decl.name, is_pointer=False, lineno=struct_decl.lineno)
        symbol = Symbol(struct_decl.name, struct_type, struct_decl, kind='struct')
        # Agregar referencia a los miembros en el símbolo para acceso fácil
        symbol.members = struct_decl.members
        self.symbol_table.define(symbol)
    
    def _analyze_struct(self, struct_decl):
        """Segunda pasada: analizar miembros de estructura"""
        # Calcular offsets para cada miembro
        current_offset = 0
        for member in struct_decl.members:
            self._validate_type(member.var_type, member.lineno)
            
            # Asignar offset al miembro
            member.offset = current_offset
            
            # Calcular tamaño del miembro para el siguiente offset
            type_name = member.var_type.name if hasattr(member.var_type, 'name') else 'entero4'
            
            # Determinar tamaño según el tipo
            if type_name == 'caracter' or type_name == 'booleano':
                size = 1
            elif type_name == 'entero2':
                size = 2
            elif type_name == 'entero4' or type_name == 'flotante':
                size = 4
            elif type_name == 'entero8' or type_name == 'doble' or type_name == 'cadena':
                size = 8  # cadena es un puntero (8 bytes)
            elif member.var_type.is_pointer:
                size = 8  # Todos los punteros son 8 bytes
            else:
                size = 8  # Por defecto
            
            current_offset += size
        
        # Guardar tamaño total de la estructura
        struct_decl.total_size = current_offset
    
    # ============================================
    # DECLARACIÓN DE FUNCIONES
    # ============================================
    
    def _declare_function(self, func_decl):
        """Primera pasada: declarar función"""
        if func_decl.name in self.functions:
            # Verificar si es sobrecarga (mismo nombre, diferentes parámetros)
            existing = self.functions[func_decl.name]
            if not self._same_signature(existing, func_decl):
                self.error(f"Función '{func_decl.name}' ya está declarada con diferente firma", func_decl.lineno)
        else:
            self.functions[func_decl.name] = func_decl
        
        # Definir en tabla de símbolos
        symbol = Symbol(func_decl.name, func_decl.return_type, func_decl, kind='function')
        self.symbol_table.define(symbol)
    
    def _same_signature(self, func1, func2):
        """Verifica si dos funciones tienen la misma firma"""
        if len(func1.params) != len(func2.params):
            return False
        for p1, p2 in zip(func1.params, func2.params):
            if not self._types_equal(p1.var_type, p2.var_type):
                return False
        return True
    
    def _analyze_function(self, func_decl):
        """Segunda pasada: analizar cuerpo de función"""
        if func_decl.is_extern:
            return  # Funciones externas no tienen cuerpo
        
        # Validar tipo de retorno
        self._validate_type(func_decl.return_type, func_decl.lineno)
        
        # Entrar a scope de función
        self.symbol_table.enter_scope(
            name=f"function_{func_decl.name}",
            is_function=True,
            return_type=func_decl.return_type
        )
        
        # Declarar parámetros
        for param in func_decl.params:
            self._validate_type(param.var_type, param.lineno)
            param_symbol = Symbol(param.name, param.var_type, param, kind='parameter')
            if not self.symbol_table.define(param_symbol):
                self.error(f"Parámetro '{param.name}' duplicado", param.lineno)
        
        # Analizar cuerpo
        if func_decl.body:
            self._analyze_block(func_decl.body)
        
        # Salir de scope de función
        self.symbol_table.exit_scope()
    
    def _analyze_global_var(self, var_decl):
        """Analiza variable global"""
        self._validate_type(var_decl.var_type, var_decl.lineno)
        
        if var_decl.init_value:
            init_type = self._analyze_expression(var_decl.init_value)
            if init_type and not self._types_compatible(var_decl.var_type, init_type):
                self.error(
                    f"Tipo incompatible en inicialización: esperado {var_decl.var_type}, encontrado {init_type}",
                    var_decl.lineno
                )
        
        var_symbol = Symbol(var_decl.name, var_decl.var_type, var_decl, kind='variable')
        if not self.symbol_table.define(var_symbol):
            self.error(f"Variable '{var_decl.name}' ya está declarada", var_decl.lineno)
    
    # ============================================
    # ANÁLISIS DE SENTENCIAS
    # ============================================
    
    def _analyze_statement(self, stmt):
        """Analiza una sentencia"""
        if isinstance(stmt, Block):
            self._analyze_block(stmt)
        elif isinstance(stmt, VarDecl):
            self._analyze_var_decl(stmt)
        elif isinstance(stmt, IfStmt):
            self._analyze_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self._analyze_while(stmt)
        elif isinstance(stmt, ForStmt):
            self._analyze_for(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._analyze_return(stmt)
        elif isinstance(stmt, BreakStmt):
            self._analyze_break(stmt)
        elif isinstance(stmt, ContinueStmt):
            self._analyze_continue(stmt)
        elif isinstance(stmt, PrintStmt):
            self._analyze_print(stmt)
        elif isinstance(stmt, ExprStmt):
            if stmt.expression:
                self._analyze_expression(stmt.expression)
        # Ignorar otros tipos de sentencias
    
    def _analyze_block(self, block):
        """Analiza un bloque de código"""
        self.symbol_table.enter_scope(name="block")
        
        for stmt in block.statements:
            self._analyze_statement(stmt)
        
        self.symbol_table.exit_scope()
    
    def _analyze_var_decl(self, var_decl):
        """Analiza declaración de variable local"""
        self._validate_type(var_decl.var_type, var_decl.lineno)
        
        if var_decl.init_value:
            init_type = self._analyze_expression(var_decl.init_value)
            if init_type and not self._types_compatible(var_decl.var_type, init_type):
                self.error(
                    f"Tipo incompatible en inicialización: esperado {var_decl.var_type}, encontrado {init_type}",
                    var_decl.lineno
                )
        
        var_symbol = Symbol(var_decl.name, var_decl.var_type, var_decl, kind='variable')
        if not self.symbol_table.define(var_symbol):
            self.error(f"Variable '{var_decl.name}' ya está declarada en este scope", var_decl.lineno)
    
    def _analyze_if(self, if_stmt):
        """Analiza sentencia if con soporte para elif"""
        # Validar límite de elif clauses (máximo 10)
        MAX_ELIF_CLAUSES = 10
        if len(if_stmt.elif_clauses) > MAX_ELIF_CLAUSES:
            self.error(
                f"Máximo {MAX_ELIF_CLAUSES} cláusulas 'si_no_si' permitidas, se encontraron {len(if_stmt.elif_clauses)}",
                if_stmt.lineno
            )
        
        # Validar condición principal
        cond_type = self._analyze_expression(if_stmt.condition)
        if cond_type and not self._is_boolean_type(cond_type):
            self.error("Condición de 'si' debe ser de tipo booleano", if_stmt.lineno)
        
        # Analizar bloque then
        self._analyze_statement(if_stmt.then_block)
        
        # Analizar cláusulas elif
        for elif_clause in if_stmt.elif_clauses:
            elif_cond_type = self._analyze_expression(elif_clause.condition)
            if elif_cond_type and not self._is_boolean_type(elif_cond_type):
                self.error("Condición de 'si_no_si' debe ser de tipo booleano", elif_clause.lineno)
            self._analyze_statement(elif_clause.block)
        
        # Analizar bloque else
        if if_stmt.else_block:
            self._analyze_statement(if_stmt.else_block)
    
    def _analyze_while(self, while_stmt):
        """Analiza sentencia while"""
        cond_type = self._analyze_expression(while_stmt.condition)
        if cond_type and not self._is_boolean_type(cond_type):
            self.error("Condición de 'mientras' debe ser de tipo booleano", while_stmt.lineno)
        
        self.symbol_table.enter_scope(name="while_loop", is_loop=True)
        self._analyze_statement(while_stmt.body)
        self.symbol_table.exit_scope()
    
    def _analyze_for(self, for_stmt):
        """Analiza sentencia for"""
        # Scope para el for
        self.symbol_table.enter_scope(name="for_loop", is_loop=True)
        
        # Analizar inicialización
        if for_stmt.init:
            if isinstance(for_stmt.init, VarDecl):
                self._analyze_var_decl(for_stmt.init)
            else:
                self._analyze_expression(for_stmt.init)
        
        # Analizar condición
        if for_stmt.condition:
            cond_type = self._analyze_expression(for_stmt.condition)
            if cond_type and not self._is_boolean_type(cond_type):
                self.error("Condición de 'para' debe ser de tipo booleano", for_stmt.lineno)
        
        # Analizar incremento
        if for_stmt.increment:
            self._analyze_expression(for_stmt.increment)
        
        # Analizar cuerpo
        self._analyze_statement(for_stmt.body)
        
        self.symbol_table.exit_scope()
    
    def _analyze_return(self, return_stmt):
        """Analiza sentencia return"""
        expected_type = self.symbol_table.get_current_function_return_type()
        
        if return_stmt.value:
            actual_type = self._analyze_expression(return_stmt.value)
            if expected_type and actual_type:
                if not self._types_equal(expected_type, actual_type):
                    self.error(
                        f"Tipo de retorno incompatible: esperado {expected_type}, encontrado {actual_type}",
                        return_stmt.lineno
                    )
        else:
            # return sin valor
            if expected_type and expected_type.name != 'vacio':
                self.error(f"Función debe retornar un valor de tipo {expected_type}", return_stmt.lineno)
    
    def _analyze_break(self, break_stmt):
        """Analiza sentencia break"""
        if not self.symbol_table.is_in_loop():
            self.error("'romper' solo puede usarse dentro de un ciclo", break_stmt.lineno)
    
    def _analyze_continue(self, continue_stmt):
        """Analiza sentencia continue"""
        if not self.symbol_table.is_in_loop():
            self.error("'continuar' solo puede usarse dentro de un ciclo", continue_stmt.lineno)
    
    def _analyze_print(self, print_stmt):
        """Analiza sentencia imprimir"""
        # Validar cada expresión en la lista de argumentos
        for expr in print_stmt.expressions:
            expr_type = self._analyze_expression(expr)
            # No hay restricciones de tipo: se puede imprimir cualquier tipo
            # (enteros, flotantes, caracteres, cadenas, punteros, etc.)
            # Si la expresión tiene error, _analyze_expression ya lo reportó
    
    # ============================================
    # ANÁLISIS DE EXPRESIONES
    # ============================================
    
    def _analyze_expression(self, expr):
        """Analiza una expresión y retorna su tipo"""
        if isinstance(expr, Identifier):
            return self._analyze_identifier(expr)
        elif isinstance(expr, IntLiteral):
            return Type('entero4', lineno=expr.lineno)
        elif isinstance(expr, FloatLiteral):
            return Type('flotante', lineno=expr.lineno)
        elif isinstance(expr, StringLiteral):
            return Type('cadena', lineno=expr.lineno)
        elif isinstance(expr, CharLiteral):
            return Type('caracter', lineno=expr.lineno)
        elif isinstance(expr, BoolLiteral):
            return Type('booleano', lineno=expr.lineno)
        elif isinstance(expr, BinaryOp):
            return self._analyze_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            return self._analyze_unary_op(expr)
        elif isinstance(expr, Assignment):
            return self._analyze_assignment(expr)
        elif isinstance(expr, FunctionCall):
            return self._analyze_function_call(expr)
        elif isinstance(expr, MemberAccess):
            return self._analyze_member_access(expr)
        elif isinstance(expr, ArrayAccess):
            return self._analyze_array_access(expr)
        elif isinstance(expr, NewExpr):
            return self._analyze_new(expr)
        elif isinstance(expr, DeleteExpr):
            return self._analyze_delete(expr)
        else:
            return None
    
    def _analyze_identifier(self, ident):
        """Analiza un identificador"""
        symbol = self.symbol_table.lookup(ident.name)
        if not symbol:
            self.error(f"Variable '{ident.name}' no está declarada", ident.lineno)
            return None
        return symbol.type
    
    def _analyze_binary_op(self, bin_op):
        """Analiza operación binaria"""
        left_type = self._analyze_expression(bin_op.left)
        right_type = self._analyze_expression(bin_op.right)
        
        if not left_type or not right_type:
            return None
        
        op = bin_op.operator
        
        # Operadores aritméticos
        if op in ('+', '-', '*', '/', '%'):
            if self._is_numeric_type(left_type) and self._is_numeric_type(right_type):
                # Promoción de tipos: si hay flotante, resultado es flotante
                if self._is_float_type(left_type) or self._is_float_type(right_type):
                    return Type('flotante', lineno=bin_op.lineno)
                return Type('entero4', lineno=bin_op.lineno)
            else:
                self.error(f"Operador '{op}' requiere operandos numéricos", bin_op.lineno)
                return None
        
        # Operadores de comparación
        elif op in ('==', '!=', '<', '<=', '>', '>='):
            if self._types_compatible(left_type, right_type):
                return Type('booleano', lineno=bin_op.lineno)
            else:
                self.error(f"Operador '{op}' requiere tipos compatibles", bin_op.lineno)
                return None
        
        # Operadores lógicos
        elif op in ('&&', '||'):
            if self._is_boolean_type(left_type) and self._is_boolean_type(right_type):
                return Type('booleano', lineno=bin_op.lineno)
            else:
                self.error(f"Operador '{op}' requiere operandos booleanos", bin_op.lineno)
                return None
        
        # Operadores bitwise
        elif op in ('&', '|', '^'):
            if self._is_integer_type(left_type) and self._is_integer_type(right_type):
                return left_type  # Mismo tipo que el izquierdo
            else:
                self.error(f"Operador '{op}' requiere operandos enteros", bin_op.lineno)
                return None
        
        return None
    
    def _analyze_unary_op(self, unary_op):
        """Analiza operación unaria"""
        operand_type = self._analyze_expression(unary_op.operand)
        if not operand_type:
            return None
        
        op = unary_op.operator
        
        if op == '!':
            if self._is_boolean_type(operand_type):
                return Type('booleano', lineno=unary_op.lineno)
            else:
                self.error("Operador '!' requiere operando booleano", unary_op.lineno)
                return None
        
        elif op == '-':
            if self._is_numeric_type(operand_type):
                return operand_type
            else:
                self.error("Operador '-' requiere operando numérico", unary_op.lineno)
                return None
        
        elif op in ('++', '--'):
            if self._is_numeric_type(operand_type):
                return operand_type
            else:
                self.error(f"Operador '{op}' requiere operando numérico", unary_op.lineno)
                return None
        
        elif op == '*':
            # Desreferencia de puntero
            if operand_type.is_pointer:
                return Type(operand_type.name, is_pointer=False, lineno=unary_op.lineno)
            else:
                self.error("Operador '*' requiere puntero", unary_op.lineno)
                return None
        
        elif op == '&':
            # Dirección de variable
            return Type(operand_type.name, is_pointer=True, lineno=unary_op.lineno)
        
        return None
    
    def _analyze_assignment(self, assign):
        """Analiza asignación"""
        lvalue_type = self._analyze_lvalue(assign.lvalue)
        rvalue_type = self._analyze_expression(assign.rvalue)
        
        if not lvalue_type or not rvalue_type:
            return None
        
        # Verificar que lvalue no sea constante
        if isinstance(assign.lvalue, Identifier):
            symbol = self.symbol_table.lookup(assign.lvalue.name)
            if symbol and symbol.is_const:
                self.error(f"No se puede asignar a constante '{assign.lvalue.name}'", assign.lineno)
        
        if not self._types_compatible(lvalue_type, rvalue_type):
            self.error(
                f"Tipo incompatible en asignación: esperado {lvalue_type}, encontrado {rvalue_type}",
                assign.lineno
            )
        
        return lvalue_type
    
    def _analyze_lvalue(self, expr):
        """Analiza un lvalue (expresión que puede ser asignada)"""
        if isinstance(expr, Identifier):
            return self._analyze_identifier(expr)
        elif isinstance(expr, MemberAccess):
            return self._analyze_member_access(expr)
        elif isinstance(expr, ArrayAccess):
            return self._analyze_array_access(expr)
        elif isinstance(expr, UnaryOp) and expr.operator == '*':
            # *ptr es un lvalue
            return self._analyze_expression(expr)
        else:
            self.error("Expresión no es un lvalue válido", expr.lineno if hasattr(expr, 'lineno') else None)
            return None
    
    def _analyze_function_call(self, call):
        """Analiza llamada a función"""
        # Evaluar la expresión de la función (puede ser un identificador o expresión)
        func_type = self._analyze_expression(call.function)
        
        if not isinstance(call.function, Identifier):
            # Si no es un identificador simple, asumimos que es una expresión válida
            # (por ejemplo, resultado de expansión de macro)
            # Evaluar argumentos y retornar tipo desconocido
            for arg in call.arguments:
                self._analyze_expression(arg)
            return None
        
        func_name = call.function.name
        func_symbol = self.symbol_table.lookup(func_name)
        
        if not func_symbol or func_symbol.kind != 'function':
            self.error(f"Función '{func_name}' no está declarada", call.lineno)
            return None
        
        func_decl = func_symbol.node
        
        # Verificar número de argumentos
        if len(call.arguments) != len(func_decl.params):
            self.error(
                f"Función '{func_name}' espera {len(func_decl.params)} argumentos, se proporcionaron {len(call.arguments)}",
                call.lineno
            )
            return func_decl.return_type
        
        # Verificar tipos de argumentos
        for i, (arg, param) in enumerate(zip(call.arguments, func_decl.params)):
            arg_type = self._analyze_expression(arg)
            if arg_type and not self._types_compatible(param.var_type, arg_type):
                self.error(
                    f"Argumento {i+1} de '{func_name}': esperado {param.var_type}, encontrado {arg_type}",
                    call.lineno
                )
        
        return func_decl.return_type
    
    def _analyze_member_access(self, member_access):
        """Analiza acceso a miembro"""
        obj_type = self._analyze_expression(member_access.object)
        if not obj_type:
            return None
        
        # Si es puntero, obtener tipo base
        if member_access.is_pointer:
            if not obj_type.is_pointer:
                self.error("Operador '->' requiere puntero", member_access.lineno)
                return None
            base_type = Type(obj_type.name, is_pointer=False)
        else:
            base_type = obj_type
        
        # Buscar estructura
        if base_type.name not in self.structs:
            self.error(f"Tipo '{base_type.name}' no es una estructura", member_access.lineno)
            return None
        
        struct_decl = self.structs[base_type.name]
        
        # Buscar miembro
        for member in struct_decl.members:
            if member.name == member_access.member:
                return member.var_type
        
        self.error(f"Miembro '{member_access.member}' no existe en estructura '{base_type.name}'", member_access.lineno)
        return None
    
    def _analyze_array_access(self, array_access):
        """Analiza acceso a array"""
        array_type = self._analyze_expression(array_access.array)
        index_type = self._analyze_expression(array_access.index)
        
        if not array_type or not index_type:
            return None
        
        if not self._is_integer_type(index_type):
            self.error("Índice de array debe ser entero", array_access.lineno)
        
        # Los arrays y punteros permiten acceso con []
        if array_type.is_pointer or array_type.is_array:
            # Para arrays multidimensionales, retornar tipo con una dimensión menos
            if hasattr(array_type, 'dimensions') and array_type.dimensions and len(array_type.dimensions) > 1:
                # Reducir una dimensión: [2][3] -> [3]
                new_dims = array_type.dimensions[1:]
                return Type(array_type.name, dimensions=new_dims, lineno=array_access.lineno)
            else:
                # Última dimensión: retornar tipo del elemento (sin array)
                return Type(array_type.name, is_pointer=False, is_array=False, lineno=array_access.lineno)
        else:
            self.error("Acceso a array requiere puntero o array", array_access.lineno)
            return None
    
    def _analyze_new(self, new_expr):
        """Analiza expresión nuevo"""
        self._validate_type(new_expr.type, new_expr.lineno)
        return Type(new_expr.type.name, is_pointer=True, lineno=new_expr.lineno)
    
    def _analyze_delete(self, delete_expr):
        """Analiza expresión eliminar"""
        expr_type = self._analyze_expression(delete_expr.expression)
        if expr_type and not expr_type.is_pointer:
            self.error("'eliminar' requiere puntero", delete_expr.lineno)
        return Type('vacio', lineno=delete_expr.lineno)
    
    # ============================================
    # VALIDACIÓN DE TIPOS
    # ============================================
    
    def _validate_type(self, type_obj, lineno):
        """Valida que un tipo sea válido"""
        if not isinstance(type_obj, Type):
            self.error(f"Tipo inválido: {type_obj}", lineno)
            return False
        
        type_name = type_obj.name
        
        # Tipos primitivos válidos
        valid_types = {
            'vacio', 'entero2', 'entero4', 'entero8',
            'caracter', 'cadena', 'flotante', 'doble', 'booleano',
            'con_signo', 'sin_signo'
        }
        
        if type_name not in valid_types and type_name not in self.structs:
            self.error(f"Tipo desconocido: '{type_name}'", lineno)
            return False
        
        return True
    
    def _types_equal(self, type1, type2):
        """Verifica si dos tipos son iguales"""
        if not type1 or not type2:
            return False
        return (type1.name == type2.name and 
                type1.is_pointer == type2.is_pointer)
    
    def _types_compatible(self, type1, type2):
        """Verifica si dos tipos son compatibles (permite conversiones implícitas)"""
        if not type1 or not type2:
            return False
        
        # Mismos tipos
        if self._types_equal(type1, type2):
            return True
        
        # Conversiones numéricas implícitas
        if self._is_numeric_type(type1) and self._is_numeric_type(type2):
            return True
        
        # Punteros compatibles (mismo tipo base)
        if type1.is_pointer and type2.is_pointer:
            return type1.name == type2.name
        
        return False
    
    def _is_numeric_type(self, type_obj):
        """Verifica si un tipo es numérico"""
        if not type_obj:
            return False
        numeric = {'entero2', 'entero4', 'entero8', 'flotante', 'doble'}
        return type_obj.name in numeric
    
    def _is_integer_type(self, type_obj):
        """Verifica si un tipo es entero"""
        if not type_obj:
            return False
        integer = {'entero2', 'entero4', 'entero8'}
        return type_obj.name in integer
    
    def _is_float_type(self, type_obj):
        """Verifica si un tipo es flotante"""
        if not type_obj:
            return False
        return type_obj.name in {'flotante', 'doble'}
    
    def _is_boolean_type(self, type_obj):
        """Verifica si un tipo es booleano"""
        if not type_obj:
            return False
        return type_obj.name == 'booleano'


# ============================================
# FUNCIÓN DE AYUDA
# ============================================

def analyze(ast):
    """
    Analiza semánticamente un AST
    
    Args:
        ast: Nodo Program del AST
    
    Returns:
        bool: True si no hay errores, False si hay errores
        list: Lista de errores
        SymbolTable: Tabla de símbolos generada
    """
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    # Asignar la tabla de símbolos al AST para uso posterior
    ast.symbol_table = analyzer.symbol_table
    
    return success, analyzer.errors

