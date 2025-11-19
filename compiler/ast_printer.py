# ast_printer.py
# Utilidad para imprimir el AST de forma legible

from compiler.ast_nodes import *

def print_ast(node, indent=0):
    """
    Imprime el AST de forma jerárquica y legible
    
    Args:
        node: Nodo del AST
        indent: Nivel de indentación
    """
    prefix = "  " * indent
    
    if node is None:
        print(f"{prefix}None")
        return
    
    # Imprimir tipo de nodo
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        for decl in node.declarations:
            print_ast(decl, indent + 1)
    
    elif isinstance(node, FunctionDecl):
        extern_str = " [extern]" if node.is_extern else ""
        print(f"{prefix}FunctionDecl: {node.name}{extern_str}")
        print(f"{prefix}  Return Type:")
        print_ast(node.return_type, indent + 2)
        if node.params:
            print(f"{prefix}  Parameters:")
            for param in node.params:
                print_ast(param, indent + 2)
        if node.body:
            print(f"{prefix}  Body:")
            print_ast(node.body, indent + 2)
    
    elif isinstance(node, StructDecl):
        print(f"{prefix}StructDecl: {node.name}")
        print(f"{prefix}  Members:")
        for member in node.members:
            print_ast(member, indent + 2)
    
    elif isinstance(node, VarDecl):
        const_str = "const " if node.is_const else ""
        print(f"{prefix}VarDecl: {const_str}{node.name}")
        print(f"{prefix}  Type:")
        print_ast(node.var_type, indent + 2)
        if node.init_value:
            print(f"{prefix}  Init:")
            print_ast(node.init_value, indent + 2)
    
    elif isinstance(node, Type):
        ptr = "*" if node.is_pointer else ""
        print(f"{prefix}Type: {node.name}{ptr}")
    
    elif isinstance(node, Block):
        print(f"{prefix}Block: ({len(node.statements)} statements)")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, IfStmt):
        print(f"{prefix}IfStmt:")
        print(f"{prefix}  Condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  Then:")
        print_ast(node.then_block, indent + 2)
        if node.else_block:
            print(f"{prefix}  Else:")
            print_ast(node.else_block, indent + 2)
    
    elif isinstance(node, WhileStmt):
        print(f"{prefix}WhileStmt:")
        print(f"{prefix}  Condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  Body:")
        print_ast(node.body, indent + 2)
    
    elif isinstance(node, ForStmt):
        print(f"{prefix}ForStmt:")
        if node.init:
            print(f"{prefix}  Init:")
            print_ast(node.init, indent + 2)
        if node.condition:
            print(f"{prefix}  Condition:")
            print_ast(node.condition, indent + 2)
        if node.increment:
            print(f"{prefix}  Increment:")
            print_ast(node.increment, indent + 2)
        print(f"{prefix}  Body:")
        print_ast(node.body, indent + 2)
    
    elif isinstance(node, ReturnStmt):
        print(f"{prefix}ReturnStmt:")
        if node.value:
            print_ast(node.value, indent + 1)
    
    elif isinstance(node, BreakStmt):
        print(f"{prefix}BreakStmt")
    
    elif isinstance(node, ContinueStmt):
        print(f"{prefix}ContinueStmt")
    
    elif isinstance(node, ExprStmt):
        print(f"{prefix}ExprStmt:")
        print_ast(node.expression, indent + 1)
    
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp: {node.operator}")
        print(f"{prefix}  Left:")
        print_ast(node.left, indent + 2)
        print(f"{prefix}  Right:")
        print_ast(node.right, indent + 2)
    
    elif isinstance(node, UnaryOp):
        prefix_str = "prefix" if node.is_prefix else "postfix"
        print(f"{prefix}UnaryOp: {node.operator} ({prefix_str})")
        print_ast(node.operand, indent + 1)
    
    elif isinstance(node, Assignment):
        print(f"{prefix}Assignment: {node.operator}")
        print(f"{prefix}  LValue:")
        print_ast(node.lvalue, indent + 2)
        print(f"{prefix}  RValue:")
        print_ast(node.rvalue, indent + 2)
    
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall:")
        print(f"{prefix}  Function:")
        print_ast(node.function, indent + 2)
        if node.arguments:
            print(f"{prefix}  Arguments:")
            for arg in node.arguments:
                print_ast(arg, indent + 2)
    
    elif isinstance(node, MemberAccess):
        arrow = "->" if node.is_pointer else "."
        print(f"{prefix}MemberAccess: {arrow}{node.member}")
        print(f"{prefix}  Object:")
        print_ast(node.object, indent + 2)
    
    elif isinstance(node, ArrayAccess):
        print(f"{prefix}ArrayAccess:")
        print(f"{prefix}  Array:")
        print_ast(node.array, indent + 2)
        print(f"{prefix}  Index:")
        print_ast(node.index, indent + 2)
    
    elif isinstance(node, NewExpr):
        print(f"{prefix}NewExpr:")
        print_ast(node.type, indent + 1)
    
    elif isinstance(node, DeleteExpr):
        print(f"{prefix}DeleteExpr:")
        print_ast(node.expression, indent + 1)
    
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier: {node.name}")
    
    elif isinstance(node, IntLiteral):
        print(f"{prefix}IntLiteral: {node.value}")
    
    elif isinstance(node, FloatLiteral):
        print(f"{prefix}FloatLiteral: {node.value}")
    
    elif isinstance(node, StringLiteral):
        print(f"{prefix}StringLiteral: {repr(node.value)}")
    
    elif isinstance(node, CharLiteral):
        print(f"{prefix}CharLiteral: {repr(node.value)}")
    
    elif isinstance(node, BoolLiteral):
        print(f"{prefix}BoolLiteral: {node.value}")
    
    else:
        print(f"{prefix}{node}")

if __name__ == "__main__":
    import sys
    from compiler.syntax_analizer import parse
    
    # Leer código desde stdin
    code = sys.stdin.read()
    
    # Parsear
    print("=== ANÁLISIS SINTÁCTICO ===\n")
    ast = parse(code)
    
    if ast:
        print("\n=== ÁRBOL DE SINTAXIS ABSTRACTA ===\n")
        print_ast(ast)
        print("\n=== FIN DEL AST ===")
    else:
        print("\n=== ERRORES DE SINTAXIS ===")
