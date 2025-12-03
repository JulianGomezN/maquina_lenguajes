# ast_nodes.py
# Definición de nodos del Árbol de Sintaxis Abstracta (AST)

class ASTNode:
    """Clase base para todos los nodos del AST"""
    def __init__(self, lineno=None, lexpos=None):
        self.lineno = lineno
        self.lexpos = lexpos
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


# ============================================
# NODOS DE TIPO
# ============================================

class Type(ASTNode):
    """Representa un tipo de dato"""
    def __init__(self, name, is_pointer=False, is_array=False, array_size=None, dimensions=None, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.name = name  # 'entero4', 'flotante', 'vacio', etc.
        self.is_pointer = is_pointer
        
        # Soportar arrays multidimensionales
        if dimensions is not None:
            self.is_array = True
            self.dimensions = dimensions  # Lista de dimensiones, ej: [2, 3] para [2][3]
            self.array_size = dimensions[0] if dimensions else None  # Compatibilidad
        else:
            self.is_array = is_array
            self.array_size = array_size
            self.dimensions = [array_size] if is_array and array_size else None
    
    def __repr__(self):
        ptr = "*" if self.is_pointer else ""
        if self.dimensions:
            arr = "".join(f"[{d}]" for d in self.dimensions)
        else:
            arr = ""
        return f"Type({self.name}{ptr}{arr})"


# ============================================
# NODOS DE DECLARACIÓN
# ============================================

class Program(ASTNode):
    """Nodo raíz del programa - contiene todas las declaraciones"""
    def __init__(self, declarations, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.declarations = declarations  # Lista de declaraciones
    
    def __repr__(self):
        return f"Program(declarations={len(self.declarations)})"


class FunctionDecl(ASTNode):
    """Declaración de función"""
    def __init__(self, return_type, name, params, body, is_extern=False, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.return_type = return_type  # Type
        self.name = name  # string
        self.params = params  # Lista de VarDecl
        self.body = body  # Block o None (si es extern)
        self.is_extern = is_extern
    
    def __repr__(self):
        return f"FunctionDecl(name={self.name}, params={len(self.params)}, extern={self.is_extern})"


class StructDecl(ASTNode):
    """Declaración de estructura"""
    def __init__(self, name, members, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.name = name  # string
        self.members = members  # Lista de VarDecl
    
    def __repr__(self):
        return f"StructDecl(name={self.name}, members={len(self.members)})"


class VarDecl(ASTNode):
    """Declaración de variable"""
    def __init__(self, var_type, name, init_value=None, is_const=False, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.var_type = var_type  # Type
        self.name = name  # string
        self.init_value = init_value  # Expression o None
        self.is_const = is_const
    
    def __repr__(self):
        const_str = "const " if self.is_const else ""
        init_str = f", init={self.init_value}" if self.init_value else ""
        return f"VarDecl({const_str}{self.var_type} {self.name}{init_str})"


# ============================================
# NODOS DE SENTENCIA (STATEMENT)
# ============================================

class Block(ASTNode):
    """Bloque de código { ... }"""
    def __init__(self, statements, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.statements = statements  # Lista de Statement
    
    def __repr__(self):
        return f"Block(statements={len(self.statements)})"


class IfStmt(ASTNode):
    """Sentencia if / if-else"""
    def __init__(self, condition, then_block, else_block=None, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.condition = condition  # Expression
        self.then_block = then_block  # Statement
        self.else_block = else_block  # Statement o None
    
    def __repr__(self):
        has_else = " with else" if self.else_block else ""
        return f"IfStmt({has_else})"


class WhileStmt(ASTNode):
    """Sentencia while"""
    def __init__(self, condition, body, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.condition = condition  # Expression
        self.body = body  # Statement
    
    def __repr__(self):
        return f"WhileStmt()"


class ForStmt(ASTNode):
    """Sentencia for"""
    def __init__(self, init, condition, increment, body, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.init = init  # Expression o None
        self.condition = condition  # Expression o None
        self.increment = increment  # Expression o None
        self.body = body  # Statement
    
    def __repr__(self):
        return f"ForStmt()"


class ReturnStmt(ASTNode):
    """Sentencia return"""
    def __init__(self, value=None, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # Expression o None
    
    def __repr__(self):
        return f"ReturnStmt(value={self.value})"


class BreakStmt(ASTNode):
    """Sentencia break"""
    def __repr__(self):
        return "BreakStmt()"


class ContinueStmt(ASTNode):
    """Sentencia continue"""
    def __repr__(self):
        return "ContinueStmt()"


class PrintStmt(ASTNode):
    """Sentencia imprimir"""
    def __init__(self, expressions=None, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.expressions = expressions if expressions is not None else []
    
    def __repr__(self):
        return f"PrintStmt(expressions={self.expressions})"


class ExprStmt(ASTNode):
    """Sentencia de expresión (expresión seguida de ;)"""
    def __init__(self, expression, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.expression = expression  # Expression
    
    def __repr__(self):
        return f"ExprStmt({self.expression})"


# ============================================
# NODOS DE EXPRESIÓN
# ============================================

class BinaryOp(ASTNode):
    """Operación binaria: left op right"""
    def __init__(self, operator, left, right, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.operator = operator  # string: '+', '-', '*', etc.
        self.left = left  # Expression
        self.right = right  # Expression
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOp(ASTNode):
    """Operación unaria: op expr"""
    def __init__(self, operator, operand, is_prefix=True, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.operator = operator  # string: '!', '-', '++', '--'
        self.operand = operand  # Expression
        self.is_prefix = is_prefix  # True para ++x, False para x++
    
    def __repr__(self):
        if self.is_prefix:
            return f"UnaryOp({self.operator}{self.operand})"
        else:
            return f"UnaryOp({self.operand}{self.operator})"


class Assignment(ASTNode):
    """Asignación: lvalue = rvalue"""
    def __init__(self, lvalue, operator, rvalue, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.lvalue = lvalue  # Expression (debe ser lvalue)
        self.operator = operator  # '=', '+=', '-=', etc.
        self.rvalue = rvalue  # Expression
    
    def __repr__(self):
        return f"Assignment({self.lvalue} {self.operator} {self.rvalue})"


class FunctionCall(ASTNode):
    """Llamada a función: func(args)"""
    def __init__(self, function, arguments, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.function = function  # Expression (típicamente Identifier)
        self.arguments = arguments  # Lista de Expression
    
    def __repr__(self):
        return f"FunctionCall({self.function}, args={len(self.arguments)})"


class MemberAccess(ASTNode):
    """Acceso a miembro: obj.member o ptr->member"""
    def __init__(self, object_expr, member, is_pointer=False, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.object = object_expr  # Expression
        self.member = member  # string (nombre del miembro)
        self.is_pointer = is_pointer  # False para '.', True para '->'
    
    def __repr__(self):
        op = "->" if self.is_pointer else "."
        return f"MemberAccess({self.object}{op}{self.member})"


class ArrayAccess(ASTNode):
    """Acceso a array: array[index]"""
    def __init__(self, array, index, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.array = array  # Expression
        self.index = index  # Expression
    
    def __repr__(self):
        return f"ArrayAccess({self.array}[{self.index}])"


class NewExpr(ASTNode):
    """Expresión nuevo: nuevo Type"""
    def __init__(self, type_expr, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.type = type_expr  # Type
    
    def __repr__(self):
        return f"NewExpr({self.type})"


class DeleteExpr(ASTNode):
    """Expresión eliminar: eliminar expr"""
    def __init__(self, expression, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.expression = expression  # Expression
    
    def __repr__(self):
        return f"DeleteExpr({self.expression})"


# ============================================
# NODOS DE LITERAL E IDENTIFICADOR
# ============================================

class Identifier(ASTNode):
    """Identificador (nombre de variable, función, etc.)"""
    def __init__(self, name, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.name = name  # string
    
    def __repr__(self):
        return f"Identifier({self.name})"


class IntLiteral(ASTNode):
    """Literal entero"""
    def __init__(self, value, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # int
    
    def __repr__(self):
        return f"IntLiteral({self.value})"


class FloatLiteral(ASTNode):
    """Literal flotante"""
    def __init__(self, value, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # float
    
    def __repr__(self):
        return f"FloatLiteral({self.value})"


class StringLiteral(ASTNode):
    """Literal cadena"""
    def __init__(self, value, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # string
    
    def __repr__(self):
        return f"StringLiteral({repr(self.value)})"


class CharLiteral(ASTNode):
    """Literal carácter"""
    def __init__(self, value, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # string (un solo carácter)
    
    def __repr__(self):
        return f"CharLiteral({repr(self.value)})"


class BoolLiteral(ASTNode):
    """Literal booleano"""
    def __init__(self, value, lineno=None, lexpos=None):
        super().__init__(lineno, lexpos)
        self.value = value  # bool
    
    def __repr__(self):
        return f"BoolLiteral({self.value})"
