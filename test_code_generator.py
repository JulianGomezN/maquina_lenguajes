"""
Script de prueba para el Generador de Código
Prueba la generación de código ensamblador Atlas desde AST
"""

from compiler.ast_nodes import *
from compiler.symbol_table import SymbolTable, Symbol
from compiler.code_generator import CodeGenerator, generate_code


def test_simple_program():
    """Prueba 1: Programa simple con variables globales y función principal"""
    print("=" * 60)
    print("PRUEBA 1: Programa Simple")
    print("=" * 60)
    
    # Código SPL equivalente:
    # entero4 x = 10;
    # entero4 y = 20;
    # 
    # funcion vacio principal() {
    #     x = x + y;
    #     retornar;
    # }
    
    # Construir AST manualmente
    var_x = VarDecl(
        var_type=Type("entero4"),
        name="x",
        init_value=IntLiteral(10)
    )
    
    var_y = VarDecl(
        var_type=Type("entero4"),
        name="y",
        init_value=IntLiteral(20)
    )
    
    # x + y
    add_expr = BinaryOp(
        operator='+',
        left=Identifier("x"),
        right=Identifier("y")
    )
    
    # x = x + y
    assignment = Assignment(
        lvalue=Identifier("x"),
        operator='=',
        rvalue=add_expr
    )
    
    # retornar
    return_stmt = ReturnStmt(value=None)
    
    # Cuerpo de principal
    main_body = Block([assignment, return_stmt])
    
    # Función principal
    main_func = FunctionDecl(
        return_type=Type("vacio"),
        name="principal",
        params=[],
        body=main_body
    )
    
    # Programa completo
    program = Program([var_x, var_y, main_func])
    
    # Construir tabla de símbolos
    symbol_table = SymbolTable()
    
    # Variables globales - necesitamos agregar atributos adicionales para el code generator
    x_symbol = Symbol("x", Type("entero4"), var_x, kind="variable")
    x_symbol.scope = "global"
    x_symbol.offset = 0  # Primera variable global
    symbol_table.define(x_symbol)
    
    y_symbol = Symbol("y", Type("entero4"), var_y, kind="variable")
    y_symbol.scope = "global"
    y_symbol.offset = 4  # Segunda variable global (después de x que ocupa 4 bytes)
    symbol_table.define(y_symbol)
    
    # Función principal
    main_symbol = Symbol("principal", Type("vacio"), main_func, kind="function")
    main_symbol.scope = "global"
    symbol_table.define(main_symbol)
    
    # Generar código
    asm_code = generate_code(program, symbol_table)
    
    print("\nCódigo SPL:")
    print("entero4 x = 10;")
    print("entero4 y = 20;")
    print("")
    print("funcion vacio principal() {")
    print("    x = x + y;")
    print("    retornar;")
    print("}")
    print("\n" + "-" * 60)
    print("Código Ensamblador Atlas Generado:")
    print("-" * 60)
    print(asm_code)
    print("\n")


def test_local_variables():
    """Prueba 2: Función con variables locales"""
    print("=" * 60)
    print("PRUEBA 2: Variables Locales")
    print("=" * 60)
    
    # Código SPL equivalente:
    # funcion entero4 suma(entero4 a, entero4 b) {
    #     entero4 resultado = a + b;
    #     retornar resultado;
    # }
    # 
    # funcion vacio principal() {
    #     entero4 x = suma(5, 3);
    # }
    
    # Parámetros de suma
    param_a = VarDecl(Type("entero4"), "a")
    param_b = VarDecl(Type("entero4"), "b")
    
    # resultado = a + b
    add_expr = BinaryOp('+', Identifier("a"), Identifier("b"))
    result_decl = VarDecl(Type("entero4"), "resultado", add_expr)
    
    # retornar resultado
    return_stmt = ReturnStmt(Identifier("resultado"))
    
    # Función suma
    suma_func = FunctionDecl(
        return_type=Type("entero4"),
        name="suma",
        params=[param_a, param_b],
        body=Block([result_decl, return_stmt])
    )
    
    # x = suma(5, 3)
    call_expr = FunctionCall(
        function=Identifier("suma"),
        arguments=[IntLiteral(5), IntLiteral(3)]
    )
    x_decl = VarDecl(Type("entero4"), "x", call_expr)
    
    # Función principal
    main_func = FunctionDecl(
        return_type=Type("vacio"),
        name="principal",
        params=[],
        body=Block([x_decl])
    )
    
    program = Program([suma_func, main_func])
    
    # Tabla de símbolos
    symbol_table = SymbolTable()
    
    # Función suma
    suma_symbol = Symbol("suma", Type("entero4"), suma_func, kind="function")
    suma_symbol.scope = "global"
    symbol_table.define(suma_symbol)
    
    # Función principal
    main_symbol = Symbol("principal", Type("vacio"), main_func, kind="function")
    main_symbol.scope = "global"
    symbol_table.define(main_symbol)
    
    # Generar código
    asm_code = generate_code(program, symbol_table)
    
    print("\nCódigo SPL:")
    print("funcion entero4 suma(entero4 a, entero4 b) {")
    print("    entero4 resultado = a + b;")
    print("    retornar resultado;")
    print("}")
    print("")
    print("funcion vacio principal() {")
    print("    entero4 x = suma(5, 3);")
    print("}")
    print("\n" + "-" * 60)
    print("Código Ensamblador Atlas Generado:")
    print("-" * 60)
    print(asm_code)
    print("\n")


def test_control_flow():
    """Prueba 3: Estructuras de control (if, while)"""
    print("=" * 60)
    print("PRUEBA 3: Estructuras de Control")
    print("=" * 60)
    
    # Código SPL equivalente:
    # entero4 contador = 0;
    # 
    # funcion vacio principal() {
    #     mientras (contador < 5) {
    #         si (contador == 3) {
    #             contador = contador + 2;
    #         } sino {
    #             contador = contador + 1;
    #         }
    #     }
    # }
    
    # Variable global contador
    contador_var = VarDecl(Type("entero4"), "contador", IntLiteral(0))
    
    # contador == 3
    if_condition = BinaryOp('==', Identifier("contador"), IntLiteral(3))
    
    # contador = contador + 2
    then_assign = Assignment(
        Identifier("contador"),
        '=',
        BinaryOp('+', Identifier("contador"), IntLiteral(2))
    )
    
    # contador = contador + 1
    else_assign = Assignment(
        Identifier("contador"),
        '=',
        BinaryOp('+', Identifier("contador"), IntLiteral(1))
    )
    
    # if completo
    if_stmt = IfStmt(if_condition, then_assign, else_assign)
    
    # contador < 5
    while_condition = BinaryOp('<', Identifier("contador"), IntLiteral(5))
    
    # while
    while_stmt = WhileStmt(while_condition, if_stmt)
    
    # Función principal
    main_func = FunctionDecl(
        Type("vacio"),
        "principal",
        [],
        Block([while_stmt])
    )
    
    program = Program([contador_var, main_func])
    
    # Tabla de símbolos
    symbol_table = SymbolTable()
    
    contador_symbol = Symbol("contador", Type("entero4"), contador_var, kind="variable")
    contador_symbol.scope = "global"
    contador_symbol.offset = 0
    symbol_table.define(contador_symbol)
    
    main_symbol = Symbol("principal", Type("vacio"), main_func, kind="function")
    main_symbol.scope = "global"
    symbol_table.define(main_symbol)
    
    # Generar código
    asm_code = generate_code(program, symbol_table)
    
    print("\nCódigo SPL:")
    print("entero4 contador = 0;")
    print("")
    print("funcion vacio principal() {")
    print("    mientras (contador < 5) {")
    print("        si (contador == 3) {")
    print("            contador = contador + 2;")
    print("        } sino {")
    print("            contador = contador + 1;")
    print("        }")
    print("    }")
    print("}")
    print("\n" + "-" * 60)
    print("Código Ensamblador Atlas Generado:")
    print("-" * 60)
    print(asm_code)
    print("\n")


def test_float_operations():
    """Prueba 4: Operaciones con punto flotante"""
    print("=" * 60)
    print("PRUEBA 4: Operaciones con Flotantes")
    print("=" * 60)
    
    # Código SPL equivalente:
    # flotante pi = 3.14;
    # flotante radio = 5.0;
    # 
    # funcion flotante calcular_area() {
    #     flotante area = pi * radio * radio;
    #     retornar area;
    # }
    # 
    # funcion vacio principal() {
    #     flotante resultado = calcular_area();
    # }
    
    # Variables globales
    pi_var = VarDecl(Type("flotante"), "pi", FloatLiteral(3.14))
    radio_var = VarDecl(Type("flotante"), "radio", FloatLiteral(5.0))
    
    # pi * radio
    mul1 = BinaryOp('*', Identifier("pi"), Identifier("radio"))
    
    # (pi * radio) * radio
    mul2 = BinaryOp('*', mul1, Identifier("radio"))
    
    # area = pi * radio * radio
    area_decl = VarDecl(Type("flotante"), "area", mul2)
    
    # retornar area
    return_stmt = ReturnStmt(Identifier("area"))
    
    # Función calcular_area
    calc_func = FunctionDecl(
        Type("flotante"),
        "calcular_area",
        [],
        Block([area_decl, return_stmt])
    )
    
    # resultado = calcular_area()
    call_expr = FunctionCall(Identifier("calcular_area"), [])
    resultado_decl = VarDecl(Type("flotante"), "resultado", call_expr)
    
    # Función principal
    main_func = FunctionDecl(
        Type("vacio"),
        "principal",
        [],
        Block([resultado_decl])
    )
    
    program = Program([pi_var, radio_var, calc_func, main_func])
    
    # Tabla de símbolos
    symbol_table = SymbolTable()
    
    pi_symbol = Symbol("pi", Type("flotante"), pi_var, kind="variable")
    pi_symbol.scope = "global"
    pi_symbol.offset = 0
    symbol_table.define(pi_symbol)
    
    radio_symbol = Symbol("radio", Type("flotante"), radio_var, kind="variable")
    radio_symbol.scope = "global"
    radio_symbol.offset = 4
    symbol_table.define(radio_symbol)
    
    calc_symbol = Symbol("calcular_area", Type("flotante"), calc_func, kind="function")
    calc_symbol.scope = "global"
    symbol_table.define(calc_symbol)
    
    main_symbol = Symbol("principal", Type("vacio"), main_func, kind="function")
    main_symbol.scope = "global"
    symbol_table.define(main_symbol)
    
    # Generar código
    asm_code = generate_code(program, symbol_table)
    
    print("\nCódigo SPL:")
    print("flotante pi = 3.14;")
    print("flotante radio = 5.0;")
    print("")
    print("funcion flotante calcular_area() {")
    print("    flotante area = pi * radio * radio;")
    print("    retornar area;")
    print("}")
    print("")
    print("funcion vacio principal() {")
    print("    flotante resultado = calcular_area();")
    print("}")
    print("\n" + "-" * 60)
    print("Código Ensamblador Atlas Generado:")
    print("-" * 60)
    print(asm_code)
    print("\n")


def test_for_loop():
    """Prueba 5: Bucle for con break y continue"""
    print("=" * 60)
    print("PRUEBA 5: Bucle For con Break/Continue")
    print("=" * 60)
    
    # Código SPL equivalente:
    # entero4 suma = 0;
    # 
    # funcion vacio principal() {
    #     para (entero4 i = 0; i < 10; i = i + 1) {
    #         si (i == 5) {
    #             continuar;
    #         }
    #         si (i == 8) {
    #             romper;
    #         }
    #         suma = suma + i;
    #     }
    # }
    
    # Variable global suma
    suma_var = VarDecl(Type("entero4"), "suma", IntLiteral(0))
    
    # i = 0 (init)
    i_init = VarDecl(Type("entero4"), "i", IntLiteral(0))
    
    # i < 10 (condition)
    for_condition = BinaryOp('<', Identifier("i"), IntLiteral(10))
    
    # i = i + 1 (increment)
    i_increment = Assignment(
        Identifier("i"),
        '=',
        BinaryOp('+', Identifier("i"), IntLiteral(1))
    )
    
    # si (i == 5) continuar;
    if1_condition = BinaryOp('==', Identifier("i"), IntLiteral(5))
    if1_stmt = IfStmt(if1_condition, ContinueStmt())
    
    # si (i == 8) romper;
    if2_condition = BinaryOp('==', Identifier("i"), IntLiteral(8))
    if2_stmt = IfStmt(if2_condition, BreakStmt())
    
    # suma = suma + i
    suma_assign = Assignment(
        Identifier("suma"),
        '=',
        BinaryOp('+', Identifier("suma"), Identifier("i"))
    )
    
    # Cuerpo del for
    for_body = Block([if1_stmt, if2_stmt, suma_assign])
    
    # for completo
    for_stmt = ForStmt(i_init, for_condition, i_increment, for_body)
    
    # Función principal
    main_func = FunctionDecl(
        Type("vacio"),
        "principal",
        [],
        Block([for_stmt])
    )
    
    program = Program([suma_var, main_func])
    
    # Tabla de símbolos
    symbol_table = SymbolTable()
    
    suma_symbol = Symbol("suma", Type("entero4"), suma_var, kind="variable")
    suma_symbol.scope = "global"
    suma_symbol.offset = 0
    symbol_table.define(suma_symbol)
    
    main_symbol = Symbol("principal", Type("vacio"), main_func, kind="function")
    main_symbol.scope = "global"
    symbol_table.define(main_symbol)
    
    # Generar código
    asm_code = generate_code(program, symbol_table)
    
    print("\nCódigo SPL:")
    print("entero4 suma = 0;")
    print("")
    print("funcion vacio principal() {")
    print("    para (entero4 i = 0; i < 10; i = i + 1) {")
    print("        si (i == 5) {")
    print("            continuar;")
    print("        }")
    print("        si (i == 8) {")
    print("            romper;")
    print("        }")
    print("        suma = suma + i;")
    print("    }")
    print("}")
    print("\n" + "-" * 60)
    print("Código Ensamblador Atlas Generado:")
    print("-" * 60)
    print(asm_code)
    print("\n")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "TEST SUITE - GENERADOR DE CÓDIGO" + " " * 16 + "║")
    print("║" + " " * 15 + "Compilador SPL → Atlas Assembly" + " " * 12 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        test_simple_program()
        test_local_variables()
        test_control_flow()
        test_float_operations()
        test_for_loop()
        
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 10 + "✓ TODAS LAS PRUEBAS COMPLETADAS" + " " * 17 + "║")
        print("╚" + "═" * 58 + "╝")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
