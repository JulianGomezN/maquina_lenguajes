# symbol_table.py
# Estructuras para tablas de símbolos y gestión de scopes

from compiler.ast_nodes import Type, FunctionDecl, StructDecl, VarDecl

class Symbol:
    """Representa un símbolo en la tabla de símbolos"""
    def __init__(self, name, symbol_type, node, kind='variable'):
        """
        Args:
            name: Nombre del símbolo
            symbol_type: Type (tipo del símbolo)
            node: Nodo AST asociado (VarDecl, FunctionDecl, StructDecl)
            kind: Tipo de símbolo ('variable', 'function', 'struct', 'parameter')
        """
        self.name = name
        self.type = symbol_type  # Type object
        self.node = node  # Nodo AST original
        self.kind = kind  # 'variable', 'function', 'struct', 'parameter'
        self.is_const = False
        if isinstance(node, VarDecl):
            self.is_const = node.is_const
    
    def __repr__(self):
        const_str = "const " if self.is_const else ""
        return f"Symbol({self.kind}: {const_str}{self.name}: {self.type})"


class Scope:
    """Representa un ámbito (scope) con su tabla de símbolos"""
    def __init__(self, parent=None, name="global"):
        self.parent = parent  # Scope padre (None para scope global)
        self.name = name  # Nombre del scope (para debugging)
        self.symbols = {}  # Diccionario: name -> Symbol
        self.is_loop = False  # True si estamos dentro de un loop (while/for)
        self.is_function = False  # True si estamos dentro de una función
        self.return_type = None  # Tipo de retorno de la función (si aplica)
    
    def define(self, symbol):
        """Define un símbolo en este scope"""
        if symbol.name in self.symbols:
            return False  # Símbolo ya existe
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name):
        """Busca un símbolo en este scope y sus padres"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name):
        """Busca un símbolo solo en este scope (no en padres)"""
        return self.symbols.get(name)
    
    def __repr__(self):
        return f"Scope({self.name}, symbols={len(self.symbols)})"


class SymbolTable:
    """Gestor de tablas de símbolos con pila de scopes"""
    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        self.scope_stack = [self.global_scope]
    
    def enter_scope(self, name="block", is_loop=False, is_function=False, return_type=None):
        """Entra a un nuevo scope"""
        new_scope = Scope(parent=self.current_scope, name=name)
        new_scope.is_loop = is_loop
        new_scope.is_function = is_function
        new_scope.return_type = return_type
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
        return new_scope
    
    def exit_scope(self):
        """Sale del scope actual"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
        else:
            raise RuntimeError("No se puede salir del scope global")
    
    def define(self, symbol):
        """Define un símbolo en el scope actual"""
        return self.current_scope.define(symbol)
    
    def lookup(self, name):
        """Busca un símbolo en todos los scopes"""
        return self.current_scope.lookup(name)
    
    def lookup_local(self, name):
        """Busca un símbolo solo en el scope actual"""
        return self.current_scope.lookup_local(name)
    
    def is_in_loop(self):
        """Verifica si estamos dentro de un loop"""
        scope = self.current_scope
        while scope:
            if scope.is_loop:
                return True
            scope = scope.parent
        return False
    
    def get_current_function_return_type(self):
        """Obtiene el tipo de retorno de la función actual"""
        scope = self.current_scope
        while scope:
            if scope.is_function and scope.return_type:
                return scope.return_type
            scope = scope.parent
        return None
    
    def __repr__(self):
        return f"SymbolTable(current={self.current_scope.name}, depth={len(self.scope_stack)})"

