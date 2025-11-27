# syntax_analizer.py
# Analizador Sintáctico usando PLY Yacc

import ply.yacc as yacc
from compiler.Lex_analizer import tokens  # Importar tokens del lexer
from compiler.ast_nodes import *

# ============================================
# TABLA DE PRECEDENCIA
# ============================================
# De menor a mayor precedencia
precedence = (
    ('right', 'ASIGNAR', 'PLUSEQ', 'MINUSEQ', 'MULTEQ', 'DIVEQ', 'MODEQ'),  # Asignación (menor)
    ('left', 'ORLOG'),  # OR lógico
    ('left', 'ANDLOG'),  # AND lógico
    ('left', 'OR'),  # OR bitwise
    ('left', 'XOR'),  # XOR bitwise
    ('left', 'AND'),  # AND bitwise
    ('left', 'IGUAL', 'DISTINTO'),  # Igualdad
    ('left', 'MENOR', 'MENORIGUAL', 'MAYOR', 'MAYORIGUAL'),  # Relacional
    ('left', 'MAS', 'MENOS'),  # Aditivo
    ('left', 'MULT', 'DIV', 'MOD'),  # Multiplicativo
    ('right', 'UNARY'),  # Operadores unarios (!, -, ++, -- prefijos)
    ('left', 'PUNTO', 'FLECHA', 'CORCHIZQ', 'PARIZQ', 'PLUSPLUS', 'MINUSMINUS'),  # Postfijos (mayor)
)

# ============================================
# REGLAS GRAMATICALES
# ============================================

# Programa: lista de declaraciones
def p_program(p):
    '''program : declaration_list'''
    p[0] = Program(p[1], lineno=p.lineno(1))

def p_declaration_list(p):
    '''declaration_list : declaration_list declaration
                        | declaration'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# Declaraciones: función, estructura o variable
def p_declaration(p):
    '''declaration : function_decl
                   | struct_decl
                   | var_decl_stmt'''
    p[0] = p[1]

# ============================================
# DECLARACIÓN DE FUNCIÓN
# ============================================

def p_function_decl(p):
    '''function_decl : FUNCION type ID PARIZQ param_list PARDER block
                     | FUNCION type ID PARIZQ PARDER block'''
    return_type = p[2]
    name = p[3]
    
    if len(p) == 8:  # Con parámetros
        params = p[5]
        body = p[7]
    else:  # Sin parámetros
        params = []
        body = p[6]
    
    p[0] = FunctionDecl(return_type, name, params, body, lineno=p.lineno(1))

def p_function_decl_extern(p):
    '''function_decl : EXTERNO FUNCION type ID PARIZQ param_list PARDER PUNTOCOMA
                     | EXTERNO FUNCION type ID PARIZQ PARDER PUNTOCOMA'''
    return_type = p[3]
    name = p[4]
    
    if len(p) == 9:  # Con parámetros
        params = p[6]
    else:  # Sin parámetros
        params = []
    
    p[0] = FunctionDecl(return_type, name, params, None, is_extern=True, lineno=p.lineno(1))

def p_param_list(p):
    '''param_list : param_list COMA param
                  | param'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_param(p):
    '''param : type ID'''
    p[0] = VarDecl(p[1], p[2], lineno=p.lineno(2))

# ============================================
# DECLARACIÓN DE ESTRUCTURA
# ============================================

def p_struct_decl(p):
    '''struct_decl : ESTRUCTURA ID LLAVEIZQ member_list LLAVEDER PUNTOCOMA'''
    p[0] = StructDecl(p[2], p[4], lineno=p.lineno(1))

def p_member_list(p):
    '''member_list : member_list member
                   | member'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_member(p):
    '''member : type ID PUNTOCOMA'''
    p[0] = VarDecl(p[1], p[2], lineno=p.lineno(2))

# ============================================
# DECLARACIÓN DE VARIABLE
# ============================================

def p_var_decl_stmt(p):
    '''var_decl_stmt : var_decl PUNTOCOMA'''
    p[0] = p[1]

def p_var_decl(p):
    '''var_decl : type ID
                | type ID ASIGNAR expression'''
    var_type = p[1]
    name = p[2]
    
    if len(p) == 5:  # Con inicialización
        init_value = p[4]
    else:
        init_value = None
    
    p[0] = VarDecl(var_type, name, init_value, lineno=p.lineno(2))

def p_var_decl_const(p):
    '''var_decl : CONSTANTE type ID ASIGNAR expression'''
    p[0] = VarDecl(p[2], p[3], p[5], is_const=True, lineno=p.lineno(3))

# ============================================
# TIPOS
# ============================================

def p_type(p):
    '''type : type_base
            | type MULT'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        # Tipo puntero
        base_type = p[1]
        p[0] = Type(base_type.name, is_pointer=True, lineno=p.lineno(2))

def p_type_base(p):
    '''type_base : VACIO
                 | ENTERO2
                 | ENTERO4
                 | ENTERO8
                 | TIPO_CARACTER
                 | TIPO_CADENA
                 | FLOTANTE
                 | DOBLE
                 | BOOLEANO
                 | CON_SIGNO
                 | SIN_SIGNO
                 | ID'''
    # Para keywords de tipo, el valor es el lexema
    p[0] = Type(p[1], lineno=p.lineno(1))

# ============================================
# SENTENCIAS (STATEMENTS)
# ============================================

def p_statement(p):
    '''statement : var_decl_stmt
                 | expr_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | return_stmt
                 | break_stmt
                 | continue_stmt
                 | block'''
    p[0] = p[1]

def p_block(p):
    '''block : LLAVEIZQ statement_list LLAVEDER
             | LLAVEIZQ LLAVEDER'''
    if len(p) == 4:
        p[0] = Block(p[2], lineno=p.lineno(1))
    else:
        p[0] = Block([], lineno=p.lineno(1))

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_expr_stmt(p):
    '''expr_stmt : expression PUNTOCOMA
                 | PUNTOCOMA'''
    if len(p) == 3:
        p[0] = ExprStmt(p[1], lineno=p.lineno(2))
    else:
        p[0] = ExprStmt(None, lineno=p.lineno(1))

# ============================================
# IF STATEMENT
# ============================================

def p_if_stmt(p):
    '''if_stmt : SI PARIZQ expression PARDER statement
               | SI PARIZQ expression PARDER statement SI_NO statement'''
    condition = p[3]
    then_block = p[5]
    
    if len(p) == 8:  # Con si_no
        else_block = p[7]
    else:
        else_block = None
    
    p[0] = IfStmt(condition, then_block, else_block, lineno=p.lineno(1))

# ============================================
# WHILE STATEMENT
# ============================================

def p_while_stmt(p):
    '''while_stmt : MIENTRAS PARIZQ expression PARDER statement'''
    p[0] = WhileStmt(p[3], p[5], lineno=p.lineno(1))

# ============================================
# FOR STATEMENT
# ============================================

def p_for_stmt(p):
    '''for_stmt : PARA PARIZQ for_init_opt PUNTOCOMA expr_opt PUNTOCOMA expr_opt PARDER statement'''
    p[0] = ForStmt(p[3], p[5], p[7], p[9], lineno=p.lineno(1))

def p_for_init_opt(p):
    '''for_init_opt : var_decl
                    | expression
                    | empty'''
    p[0] = p[1]

def p_expr_opt(p):
    '''expr_opt : expression
                | empty'''
    p[0] = p[1]

# ============================================
# RETURN, BREAK, CONTINUE
# ============================================

def p_return_stmt(p):
    '''return_stmt : RETORNAR expression PUNTOCOMA
                   | RETORNAR PUNTOCOMA'''
    if len(p) == 4:
        p[0] = ReturnStmt(p[2], lineno=p.lineno(1))
    else:
        p[0] = ReturnStmt(None, lineno=p.lineno(1))

def p_break_stmt(p):
    '''break_stmt : ROMPER PUNTOCOMA'''
    p[0] = BreakStmt(lineno=p.lineno(1))

def p_continue_stmt(p):
    '''continue_stmt : CONTINUAR PUNTOCOMA'''
    p[0] = ContinueStmt(lineno=p.lineno(1))

# ============================================
# EXPRESIONES
# ============================================

def p_expression(p):
    '''expression : assignment'''
    p[0] = p[1]

# Asignación (menor precedencia)
def p_assignment(p):
    '''assignment : logical ASIGNAR assignment
                  | logical PLUSEQ assignment
                  | logical MINUSEQ assignment
                  | logical MULTEQ assignment
                  | logical DIVEQ assignment
                  | logical MODEQ assignment
                  | logical'''
    if len(p) == 4:
        p[0] = Assignment(p[1], p[2], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# OR lógico
def p_logical_or(p):
    '''logical : logical ORLOG logical_and
               | logical_and'''
    if len(p) == 4:
        p[0] = BinaryOp('||', p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# AND lógico
def p_logical_and(p):
    '''logical_and : logical_and ANDLOG bitwise_or
                   | bitwise_or'''
    if len(p) == 4:
        p[0] = BinaryOp('&&', p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# OR bitwise
def p_bitwise_or(p):
    '''bitwise_or : bitwise_or OR bitwise_xor
                  | bitwise_xor'''
    if len(p) == 4:
        p[0] = BinaryOp('|', p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# XOR bitwise
def p_bitwise_xor(p):
    '''bitwise_xor : bitwise_xor XOR bitwise_and
                   | bitwise_and'''
    if len(p) == 4:
        p[0] = BinaryOp('^', p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# AND bitwise
def p_bitwise_and(p):
    '''bitwise_and : bitwise_and AND equality
                   | equality'''
    if len(p) == 4:
        p[0] = BinaryOp('&', p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# Igualdad
def p_equality(p):
    '''equality : equality IGUAL relational
                | equality DISTINTO relational
                | relational'''
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# Relacional
def p_relational(p):
    '''relational : relational MENOR additive
                  | relational MENORIGUAL additive
                  | relational MAYOR additive
                  | relational MAYORIGUAL additive
                  | additive'''
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# Aditivo
def p_additive(p):
    '''additive : additive MAS multiplicative
                | additive MENOS multiplicative
                | multiplicative'''
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# Multiplicativo
def p_multiplicative(p):
    '''multiplicative : multiplicative MULT unary
                      | multiplicative DIV unary
                      | multiplicative MOD unary
                      | unary'''
    if len(p) == 4:
        p[0] = BinaryOp(p[2], p[1], p[3], lineno=p.lineno(2))
    else:
        p[0] = p[1]

# Unario (prefijo)
def p_unary(p):
    '''unary : NOT unary
             | MENOS unary %prec UNARY
             | PLUSPLUS unary
             | MINUSMINUS unary
             | MULT unary %prec UNARY
             | AND unary %prec UNARY
             | postfix'''
    if len(p) == 3:
        # Operador unario prefijo
        operator = p[1]
        # * es desreferencia, & es dirección
        p[0] = UnaryOp(operator, p[2], is_prefix=True, lineno=p.lineno(1))
    else:
        p[0] = p[1]

# Postfijo
def p_postfix(p):
    '''postfix : postfix PLUSPLUS
               | postfix MINUSMINUS
               | postfix PUNTO ID
               | postfix FLECHA ID
               | postfix CORCHIZQ expression CORCHDER
               | postfix PARIZQ argument_list PARDER
               | postfix PARIZQ PARDER
               | primary'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        # Incremento/decremento postfijo
        p[0] = UnaryOp(p[2], p[1], is_prefix=False, lineno=p.lineno(2))
    elif p[2] == '.':
        # Acceso a miembro: obj.member
        p[0] = MemberAccess(p[1], p[3], is_pointer=False, lineno=p.lineno(2))
    elif p[2] == '->':
        # Acceso a miembro puntero: ptr->member
        p[0] = MemberAccess(p[1], p[3], is_pointer=True, lineno=p.lineno(2))
    elif p[2] == '[':
        # Acceso a array: array[index]
        p[0] = ArrayAccess(p[1], p[3], lineno=p.lineno(2))
    elif p[2] == '(':
        # Llamada a función
        if len(p) == 5:  # Con argumentos
            p[0] = FunctionCall(p[1], p[3], lineno=p.lineno(2))
        else:  # Sin argumentos
            p[0] = FunctionCall(p[1], [], lineno=p.lineno(2))

def p_argument_list(p):
    '''argument_list : argument_list COMA expression
                     | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# Primarios
def p_primary(p):
    '''primary : ID
               | ENTERO
               | FLOT
               | CARACTER
               | CADENA
               | PARIZQ expression PARDER
               | new_expr
               | delete_expr'''
    if len(p) == 2:
        # Literales o identificador
        token_val = p[1]
        if isinstance(token_val, str) and p.slice[1].type == 'ID':
            # Es un identificador
            p[0] = Identifier(token_val, lineno=p.lineno(1))
        elif isinstance(token_val, int):
            # Literal entero
            p[0] = IntLiteral(token_val, lineno=p.lineno(1))
        elif isinstance(token_val, float):
            # Literal flotante
            p[0] = FloatLiteral(token_val, lineno=p.lineno(1))
        elif p.slice[1].type == 'CARACTER':
            # Literal carácter
            p[0] = CharLiteral(token_val, lineno=p.lineno(1))
        elif p.slice[1].type == 'CADENA':
            # Literal cadena
            p[0] = StringLiteral(token_val, lineno=p.lineno(1))
        else:
            # NewExpr, DeleteExpr
            p[0] = token_val
    elif len(p) == 4:
        # Expresión entre paréntesis
        p[0] = p[2]

# Expresión nuevo
def p_new_expr(p):
    '''new_expr : NUEVO type'''
    p[0] = NewExpr(p[2], lineno=p.lineno(1))

# Expresión eliminar
def p_delete_expr(p):
    '''delete_expr : ELIMINAR unary'''
    p[0] = DeleteExpr(p[2], lineno=p.lineno(1))

# Regla vacía
def p_empty(p):
    '''empty :'''
    p[0] = None

# ============================================
# MANEJO DE ERRORES
# ============================================

def p_error(p):
    if p:
        print(f"Error de sintaxis en línea {p.lineno}, token '{p.type}' con valor '{p.value}'")
        print(f"Contexto: ...{p.lexer.lexdata[max(0, p.lexpos-20):p.lexpos+20]}...")
        # Recuperación en modo pánico: saltar hasta el próximo punto y coma o llave
        while True:
            tok = parser.token()
            if not tok or tok.type in ('PUNTOCOMA', 'LLAVEDER'):
                break
        parser.errok()
        return tok
    else:
        print("Error de sintaxis: fin de archivo inesperado")

# ============================================
# CONSTRUIR EL PARSER
# ============================================

parser = yacc.yacc()

# ============================================
# FUNCIÓN DE AYUDA PARA PARSEAR
# ============================================

def parse(code, debug=False):
    """
    Parsea código fuente y retorna el AST.
    
    Args:
        code: String con el código fuente
        debug: Booleano para activar modo debug
    
    Returns:
        Program (nodo raíz del AST) o None si hay errores
    """
    from compiler.Lex_analizer import lexer
    
    result = parser.parse(code, lexer=lexer, debug=debug)
    return result

# ============================================
# PRUEBA (Powershell)
# cat .\Algoritmos\Ejemplos_alto_nivel\1.txt | python .\compiler\syntax_analizer.py
# ============================================

if __name__ == "__main__":
    import sys
    
    # Leer código desde stdin
    code = sys.stdin.read()
    
    # Parsear
    print("=== INICIANDO ANÁLISIS SINTÁCTICO ===\n")
    ast = parse(code, debug=False)
    
    if ast:
        print("\n=== ANÁLISIS EXITOSO ===")
        print(f"\nAST Raíz: {ast}")
        print(f"Declaraciones encontradas: {len(ast.declarations)}\n")
        
        # Imprimir resumen de declaraciones
        for i, decl in enumerate(ast.declarations, 1):
            print(f"{i}. {decl}")
    else:
        print("\n=== ERRORES DE SINTAXIS ENCONTRADOS ===")
