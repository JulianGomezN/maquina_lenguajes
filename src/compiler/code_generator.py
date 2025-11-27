"""
Generador de Código para el compilador SPL -> Atlas Assembly
Traduce el Árbol de Sintaxis Abstracta (AST) a código ensamblador Atlas
"""

from .ast_nodes import *
from .symbol_table import SymbolTable


class CodeGenerator:
    """
    Generador de código que traduce AST + Tabla de Símbolos a código ensamblador Atlas.
    
    Estrategia de generación:
    1. Variables globales: Se asignan a direcciones absolutas de memoria
    2. Variables locales: Se acceden mediante desplazamiento desde el Frame Pointer (R14)
    3. Expresiones: Se evalúan usando registros temporales (R00-R13)
    4. Funciones: Usan convención de llamada con prólogo/epílogo estándar
    5. Tipos: Se generan instrucciones con sufijos de tamaño según el tipo (1/2/4/8 bytes)
    """
    
    def __init__(self, ast, symbol_table):
        """
        Inicializa el generador de código.
        
        Args:
            ast: Nodo raíz del AST (Program)
            symbol_table: Tabla de símbolos generada por el análisis semántico
        """
        self.ast = ast
        self.symbol_table = symbol_table
        self.code = []  # Lista de líneas de código ensamblador generadas
        
        # Gestión de registros temporales (R00-R13, reservando R14=BP y R15=SP)
        self.temp_counter = 0  # Contador para asignar registros temporales
        self.max_temps = 14  # Máximo número de registros disponibles (R00-R13)
        
        # Gestión de etiquetas
        self.label_counter = 0  # Contador para generar etiquetas únicas
        
        # Stack de contexto para bucles (para break/continue)
        self.loop_stack = []  # [(label_start, label_end), ...]
        
        # Función actual (para validar returns)
        self.current_function = None
        
        # Dirección base para variables globales
        self.global_data_base = 0x1000  # Las globales empiezan en dirección 0x1000
    
    def generate(self):
        """
        Punto de entrada principal: genera el código completo.
        
        Returns:
            String con el código ensamblador Atlas completo
        """
        self.emit("; Código generado por el compilador SPL -> Atlas")
        self.emit("; Arquitectura: Atlas CPU (64-bit)")
        self.emit("")
        
        # Generar código para el programa
        self.visit_program(self.ast)
        
        # Asegurar que el programa termine con PARAR
        self.emit("")
        self.emit("; Fin del programa")
        self.emit("PARAR")
        
        return "\n".join(self.code)
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def emit(self, line):
        """Añade una línea de código al resultado."""
        self.code.append(line)
    
    def new_temp(self):
        """
        Asigna un nuevo registro temporal.
        
        Returns:
            Integer con el número del registro (ej: 0, 1, 2, ...)
        """
        if self.temp_counter >= self.max_temps:
            # Si nos quedamos sin registros, reutilizamos desde R00
            self.temp_counter = 0
        
        reg = self.temp_counter
        self.temp_counter += 1
        return reg
    
    def reset_temps(self):
        """Resetea el contador de temporales (útil al inicio de funciones/bloques)."""
        self.temp_counter = 0
    
    def new_label(self, prefix="L"):
        """
        Genera una etiqueta única.
        
        Args:
            prefix: Prefijo para la etiqueta (ej: "IF", "WHILE", "L")
        
        Returns:
            String con el nombre de la etiqueta
        """
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label
    
    def get_type_size(self, type_name):
        """
        Obtiene el tamaño en bytes de un tipo.
        
        Args:
            type_name: Nombre del tipo (ej: "entero4", "flotante", "doble")
        
        Returns:
            Tamaño en bytes (1, 2, 4, u 8)
        """
        if type_name == "entero1" or type_name == "caracter" or type_name == "booleano":
            return 1
        elif type_name == "entero2":
            return 2
        elif type_name == "entero4" or type_name == "flotante":
            return 4
        elif type_name == "entero8" or type_name == "doble" or type_name == "puntero":
            return 8
        else:
            return 8  # Por defecto, asumir 8 bytes
    
    def get_sized_instruction(self, base_instr, type_name):
        """
        Genera el nombre de instrucción con sufijo de tamaño.
        
        Args:
            base_instr: Instrucción base (ej: "ADD", "LOAD", "STORE", "FADD")
            type_name: Tipo de dato
        
        Returns:
            Instrucción con sufijo (ej: "ADD4", "LOAD8", "FADD8")
        """
        size = self.get_type_size(type_name)
        
        # Instrucciones que NO usan sufijo de tamaño
        if base_instr in ["CMP", "CMPV"]:
            return base_instr
        
        # Instrucciones de punto flotante usan prefijo F
        if type_name in ["flotante", "doble"]:
            if base_instr in ["ADD", "SUB", "MUL", "DIV"]:
                return f"F{base_instr}{size}"
        
        # Instrucciones enteras usan sufijo de tamaño
        return f"{base_instr}{size}"
    
    def is_float_type(self, type_name):
        """Determina si un tipo es de punto flotante."""
        return type_name in ["flotante", "doble"]
    
    # ==================== VISITANTES DEL AST ====================
    
    def visit_program(self, node):
        """
        Genera código para el nodo Program (raíz del AST).
        
        Estructura generada:
        1. Sección de datos globales (variables globales)
        2. Código de inicialización (setup del stack)
        3. Llamada a la función principal
        4. Funciones definidas por el usuario
        """
        self.emit("; === SECCIÓN DE DATOS GLOBALES ===")
        self.emit("")
        
        # Generar declaraciones globales
        for decl in node.declarations:
            if isinstance(decl, VarDecl):
                self.visit_global_var_decl(decl)
        
        self.emit("")
        self.emit("; === CÓDIGO DE INICIALIZACIÓN ===")
        self.emit("")
        
        # Configurar el stack pointer (R15) y frame pointer (R14)
        self.emit("; Inicializar Stack Pointer (R15) y Frame Pointer (R14)")
        self.emit("MOVV8 R15, 0xFFFF  ; SP apunta al final de la memoria (64KB)")
        self.emit("MOV8 R14, R15      ; BP = SP (frame inicial)")
        self.emit("")
        
        # Buscar la función principal y llamarla
        self.emit("; Llamar a la función principal")
        main_func = self.symbol_table.lookup("principal")
        if main_func and main_func.kind == "function":
            self.emit("CALL principal")
        else:
            self.emit("; ADVERTENCIA: No se encontró la función 'principal'")
        
        self.emit("JMP END_PROGRAM")
        self.emit("")
        
        # Generar código para todas las funciones
        self.emit("; === FUNCIONES ===")
        self.emit("")
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                self.visit_function_decl(decl)
        
        self.emit("")
        self.emit("END_PROGRAM:")
    
    def visit_global_var_decl(self, node):
        """
        Genera código para una declaración de variable global.
        
        Las variables globales se asignan a direcciones absolutas de memoria
        comenzando desde self.global_data_base.
        """
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            return
        
        # La dirección ya fue asignada por el análisis semántico en symbol.offset
        address = self.global_data_base + symbol.offset
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        size = self.get_type_size(type_name)
        
        self.emit(f"; Variable global: {node.name} (tipo: {type_name}, tamaño: {size} bytes, dirección: {address})")
        
        # Si tiene inicializador, generar código para inicializarla
        if node.init_value:
            reg = self.visit_expr(node.init_value, type_name)
            store_instr = self.get_sized_instruction("STORE", type_name)
            self.emit(f"{store_instr} R{reg:02d}, {address}  ; {node.name} = valor_inicial")
    
    def visit_function_decl(self, node):
        """
        Genera código para una declaración de función.
        
        Convención de llamada:
        1. Prólogo: Guardar BP, configurar nuevo frame
        2. Cuerpo: Ejecutar statements
        3. Epílogo: Restaurar BP, retornar
        """
        self.emit(f"{node.name}:  ; Función: {node.name}")
        self.current_function = node.name
        self.reset_temps()
        
        # === PRÓLOGO ===
        self.emit(f"  ; Prólogo de {node.name}")
        self.emit(f"  PUSH8 R14          ; Guardar BP anterior")
        self.emit(f"  MOV8 R14, R15      ; BP = SP (nuevo frame)")
        
        # Calcular espacio para variables locales
        func_symbol = self.symbol_table.lookup(node.name)
        local_space = 0
        if func_symbol and hasattr(func_symbol, 'local_size'):
            local_space = func_symbol.local_size
        
        if local_space > 0:
            self.emit(f"  SUBV8 R15, {local_space}  ; Reservar espacio para locales")
        
        self.emit("")
        
        # === CUERPO ===
        self.emit(f"  ; Cuerpo de {node.name}")
        for stmt in node.body.statements:
            self.visit_stmt(stmt)
        
        self.emit("")
        
        # === EPÍLOGO (si no hubo return explícito) ===
        self.emit(f"{node.name}_epilogue:")
        self.emit(f"  ; Epílogo de {node.name}")
        self.emit(f"  MOV8 R15, R14      ; SP = BP (liberar locales)")
        self.emit(f"  POP8 R14           ; Restaurar BP anterior")
        self.emit(f"  RET                ; Retornar")
        self.emit("")
        
        self.current_function = None
    
    def visit_stmt(self, node):
        """Dispatcher para diferentes tipos de statements."""
        if isinstance(node, VarDecl):
            self.visit_local_var_decl(node)
        elif isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, IfStmt):
            self.visit_if_stmt(node)
        elif isinstance(node, WhileStmt):
            self.visit_while_stmt(node)
        elif isinstance(node, ForStmt):
            self.visit_for_stmt(node)
        elif isinstance(node, ReturnStmt):
            self.visit_return_stmt(node)
        elif isinstance(node, BreakStmt):
            self.visit_break_stmt(node)
        elif isinstance(node, ContinueStmt):
            self.visit_continue_stmt(node)
        elif isinstance(node, ExprStmt):
            self.visit_expr_stmt(node)
        elif isinstance(node, Block):
            self.visit_block(node)
        # Agregar más tipos según sea necesario
    
    def visit_local_var_decl(self, node):
        """
        Genera código para una declaración de variable local.
        
        Las variables locales se acceden mediante offset desde BP (R14).
        """
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            return
        
        self.emit(f"  ; Variable local: {node.name} (offset: {symbol.offset})")
        
        # Si tiene inicializador, almacenarlo
        if node.init_value:
            type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
            reg = self.visit_expr(node.init_value, type_name)
            store_instr = self.get_sized_instruction("STORER", type_name)
            
            # Cargar la dirección: BP + offset
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            self.emit(f"  {store_instr} R{reg:02d}, R{addr_reg:02d}  ; {node.name} = valor_inicial")
    
    def visit_assignment(self, node):
        """Genera código para una asignación."""
        # node.lvalue es típicamente un Identifier, pero podría ser ArrayAccess o MemberAccess
        if not isinstance(node.lvalue, Identifier):
            self.emit("  ; ADVERTENCIA: Asignación a expresión compleja no implementada")
            return
        
        target_name = node.lvalue.name
        symbol = self.symbol_table.lookup(target_name)
        if not symbol:
            return
        
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        # Evaluar expresión del lado derecho
        reg = self.visit_expr(node.rvalue, type_name)
        
        if symbol.scope == "global":
            # Variable global: STORE a dirección absoluta
            address = self.global_data_base + symbol.offset
            store_instr = self.get_sized_instruction("STORE", type_name)
            self.emit(f"  {store_instr} R{reg:02d}, {address}  ; {target_name} = valor")
        else:
            # Variable local: STORER con offset desde BP
            store_instr = self.get_sized_instruction("STORER", type_name)
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            self.emit(f"  {store_instr} R{reg:02d}, R{addr_reg:02d}  ; {target_name} = valor")
    
    def visit_if_stmt(self, node):
        """
        Genera código para un statement if.
        
        Estructura:
          <evaluar condición>
          CMP + JEQ else_label
          <then_block>
          JMP end_label
        else_label:
          <else_block>
        end_label:
        """
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")
        
        # Evaluar condición (debe ser booleano)
        cond_reg = self.visit_expr(node.condition, "booleano")
        
        # Si la condición es falsa (0), saltar a else
        self.emit(f"  CMPV R{cond_reg:02d}, 0")
        self.emit(f"  JEQ {else_label}")
        
        # Bloque then
        self.visit_stmt(node.then_block)
        self.emit(f"  JMP {end_label}")
        
        # Bloque else (si existe)
        self.emit(f"{else_label}:")
        if node.else_block:
            self.visit_stmt(node.else_block)
        
        self.emit(f"{end_label}:")
    
    def visit_while_stmt(self, node):
        """
        Genera código para un bucle while.
        
        Estructura:
        start_label:
          <evaluar condición>
          CMP + JEQ end_label
          <body>
          JMP start_label
        end_label:
        """
        start_label = self.new_label("WHILE_START")
        end_label = self.new_label("WHILE_END")
        
        # Añadir contexto al stack de bucles (para break/continue)
        self.loop_stack.append((start_label, end_label))
        
        self.emit(f"{start_label}:")
        
        # Evaluar condición
        cond_reg = self.visit_expr(node.condition, "booleano")
        self.emit(f"  CMPV R{cond_reg:02d}, 0")
        self.emit(f"  JEQ {end_label}")
        
        # Cuerpo del bucle
        self.visit_stmt(node.body)
        
        # Volver al inicio
        self.emit(f"  JMP {start_label}")
        
        self.emit(f"{end_label}:")
        
        # Remover contexto del stack
        self.loop_stack.pop()
    
    def visit_for_stmt(self, node):
        """
        Genera código para un bucle for.
        
        Estructura:
          <init>
        start_label:
          <evaluar condición>
          CMP + JEQ end_label
          <body>
        continue_label:
          <update>
          JMP start_label
        end_label:
        """
        start_label = self.new_label("FOR_START")
        continue_label = self.new_label("FOR_CONTINUE")
        end_label = self.new_label("FOR_END")
        
        # Añadir contexto al stack (continue debe ir a continue_label)
        self.loop_stack.append((continue_label, end_label))
        
        # Inicialización
        if node.init:
            self.visit_stmt(node.init)
        
        self.emit(f"{start_label}:")
        
        # Condición
        if node.condition:
            cond_reg = self.visit_expr(node.condition, "booleano")
            self.emit(f"  CMPV R{cond_reg:02d}, 0")
            self.emit(f"  JEQ {end_label}")
        
        # Cuerpo
        self.visit_stmt(node.body)
        
        # Actualización
        self.emit(f"{continue_label}:")
        if node.increment:
            self.visit_stmt(node.increment)
        
        self.emit(f"  JMP {start_label}")
        
        self.emit(f"{end_label}:")
        
        self.loop_stack.pop()
    
    def visit_return_stmt(self, node):
        """
        Genera código para un return.
        
        El valor de retorno se coloca en R00 antes del epílogo.
        """
        if node.value:
            # Obtener el tipo de retorno de la función actual
            func_symbol = self.symbol_table.lookup(self.current_function)
            if func_symbol and hasattr(func_symbol.type, 'name'):
                return_type = func_symbol.type.name
            elif func_symbol:
                return_type = str(func_symbol.type)
            else:
                return_type = "entero8"
            
            # Evaluar expresión y guardar en R00
            reg = self.visit_expr(node.value, return_type)
            if reg != 0:  # Si no está ya en R00, moverlo
                mov_instr = self.get_sized_instruction("MOV", return_type)
                self.emit(f"  {mov_instr} R00, R{reg:02d}  ; Valor de retorno en R00")
        
        # Saltar al epílogo
        self.emit(f"  JMP {self.current_function}_epilogue")
    
    def visit_break_stmt(self, node):
        """Genera código para break (salir del bucle actual)."""
        if not self.loop_stack:
            self.emit("  ; ERROR: break fuera de un bucle")
            return
        
        _, end_label = self.loop_stack[-1]
        self.emit(f"  JMP {end_label}  ; break")
    
    def visit_continue_stmt(self, node):
        """Genera código para continue (siguiente iteración del bucle)."""
        if not self.loop_stack:
            self.emit("  ; ERROR: continue fuera de un bucle")
            return
        
        start_label, _ = self.loop_stack[-1]
        self.emit(f"  JMP {start_label}  ; continue")
    
    def visit_expr_stmt(self, node):
        """Genera código para un statement de expresión (ej: llamada a función)."""
        self.visit_expr(node.expression, "vacio")
    
    def visit_block(self, node):
        """Genera código para un bloque de statements."""
        for stmt in node.statements:
            self.visit_stmt(stmt)
    
    # ==================== EXPRESIONES ====================
    
    def visit_expr(self, node, expected_type="entero8"):
        """
        Dispatcher para expresiones.
        
        Args:
            node: Nodo de expresión del AST
            expected_type: Tipo esperado del resultado
        
        Returns:
            Número de registro temporal donde está el resultado
        """
        if isinstance(node, (IntLiteral, FloatLiteral, StringLiteral, CharLiteral, BoolLiteral)):
            return self.visit_literal(node, expected_type)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node, expected_type)
        elif isinstance(node, BinaryOp):
            return self.visit_binary_op(node, expected_type)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node, expected_type)
        elif isinstance(node, FunctionCall):
            return self.visit_function_call(node, expected_type)
        # Agregar más tipos de expresiones según sea necesario
        else:
            # Expresión no soportada, retornar registro R00 por defecto
            return 0
    
    def visit_literal(self, node, expected_type):
        """Genera código para un literal (constante)."""
        reg = self.new_temp()
        mov_instr = self.get_sized_instruction("MOVV", expected_type)
        
        if isinstance(node, IntLiteral):
            self.emit(f"  {mov_instr} R{reg:02d}, {node.value}")
        elif isinstance(node, FloatLiteral):
            # Para flotantes, convertir a representación hexadecimal IEEE 754
            import struct
            if expected_type == "flotante":
                hex_val = struct.unpack('>I', struct.pack('>f', float(node.value)))[0]
            else:  # doble
                hex_val = struct.unpack('>Q', struct.pack('>d', float(node.value)))[0]
            self.emit(f"  {mov_instr} R{reg:02d}, 0x{hex_val:X}")
        elif isinstance(node, CharLiteral):
            self.emit(f"  MOVV1 R{reg:02d}, {ord(node.value)}")
        elif isinstance(node, BoolLiteral):
            val = 1 if node.value else 0
            self.emit(f"  MOVV1 R{reg:02d}, {val}")
        elif isinstance(node, StringLiteral):
            # Para cadenas, necesitaríamos un manejo especial (no implementado aquí)
            self.emit(f"  MOVV8 R{reg:02d}, 0  ; String literal no soportado aún")
        else:
            self.emit(f"  MOVV8 R{reg:02d}, 0  ; Literal no soportado")
        
        return reg
    
    def visit_identifier(self, node, expected_type):
        """Genera código para acceder a una variable."""
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            reg = self.new_temp()
            self.emit(f"  ; ERROR: Variable {node.name} no encontrada")
            self.emit(f"  MOVV8 R{reg:02d}, 0")
            return reg
        
        reg = self.new_temp()
        
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        if symbol.scope == "global":
            # Variable global: LOAD desde dirección absoluta
            address = self.global_data_base + symbol.offset
            load_instr = self.get_sized_instruction("LOAD", type_name)
            self.emit(f"  {load_instr} R{reg:02d}, {address}  ; Cargar {node.name}")
        else:
            # Variable local: LOADR con offset desde BP
            load_instr = self.get_sized_instruction("LOADR", type_name)
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            self.emit(f"  {load_instr} R{reg:02d}, R{addr_reg:02d}  ; Cargar {node.name}")
        
        return reg
    
    def visit_binary_op(self, node, expected_type):
        """Genera código para operaciones binarias."""
        # Evaluar operandos
        left_reg = self.visit_expr(node.left, expected_type)
        right_reg = self.visit_expr(node.right, expected_type)
        
        result_reg = self.new_temp()
        
        # Determinar la instrucción según el operador
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '==': 'CMP',  # Comparación requiere manejo especial
            '!=': 'CMP',
            '<': 'CMP',
            '<=': 'CMP',
            '>': 'CMP',
            '>=': 'CMP',
            '&&': 'AND',
            '||': 'OR',
        }
        
        base_instr = op_map.get(node.operator)
        if not base_instr:
            self.emit(f"  ; ERROR: Operador {node.operator} no soportado")
            self.emit(f"  MOVV8 R{result_reg:02d}, 0")
            return result_reg
        
        # Generar instrucción con tamaño apropiado
        if node.operator in ['==', '!=', '<', '<=', '>', '>=']:
            # Operadores de comparación
            cmp_instr = self.get_sized_instruction("CMP", expected_type)
            self.emit(f"  {cmp_instr} R{left_reg:02d}, R{right_reg:02d}")
            
            # Según el operador, usar salto condicional
            jump_map = {
                '==': 'JEQ',
                '!=': 'JNE',
                '<': 'JLT',
                '<=': ('JLT', 'JEQ'),  # Requiere dos saltos
                '>': 'JGE',  # Mayor: no cumple < ni ==
                '>=': 'JGE',
            }
            
            true_label = self.new_label("CMP_TRUE")
            end_label = self.new_label("CMP_END")
            
            self.emit(f"  MOVV1 R{result_reg:02d}, 0  ; Asumir falso")
            
            if node.operator == '<=':
                self.emit(f"  JLT {true_label}")
                self.emit(f"  JEQ {true_label}")
            else:
                jump = jump_map[node.operator]
                self.emit(f"  {jump} {true_label}")
            
            self.emit(f"  JMP {end_label}")
            self.emit(f"{true_label}:")
            self.emit(f"  MOVV1 R{result_reg:02d}, 1  ; Verdadero")
            self.emit(f"{end_label}:")
        else:
            # Operadores aritméticos/lógicos
            instr = self.get_sized_instruction(base_instr, expected_type)
            self.emit(f"  MOV8 R{result_reg:02d}, R{left_reg:02d}")
            self.emit(f"  {instr} R{result_reg:02d}, R{right_reg:02d}")
        
        return result_reg
    
    def visit_unary_op(self, node, expected_type):
        """Genera código para operaciones unarias."""
        operand_reg = self.visit_expr(node.operand, expected_type)
        result_reg = self.new_temp()
        
        if node.operator == '-':
            # Negación: 0 - operando
            self.emit(f"  MOVV8 R{result_reg:02d}, 0")
            sub_instr = self.get_sized_instruction("SUB", expected_type)
            self.emit(f"  {sub_instr} R{result_reg:02d}, R{operand_reg:02d}")
        elif node.operator == '!':
            # NOT lógico
            self.emit(f"  NOT R{result_reg:02d}")
        else:
            self.emit(f"  ; ERROR: Operador unario {node.operator} no soportado")
            self.emit(f"  MOV8 R{result_reg:02d}, R{operand_reg:02d}")
        
        return result_reg
    
    def visit_function_call(self, node, expected_type):
        """
        Genera código para una llamada a función.
        
        Convención: Los argumentos se pasan en la pila (push en orden inverso).
        El valor de retorno queda en R00.
        """
        # node.function es típicamente un Identifier
        if isinstance(node.function, Identifier):
            func_name = node.function.name
        else:
            func_name = "UNKNOWN_FUNCTION"
        
        # Evaluar argumentos y pushearlos en orden inverso
        arg_regs = []
        for arg in node.arguments:
            arg_reg = self.visit_expr(arg, "entero8")  # Asumir entero8 por defecto
            arg_regs.append(arg_reg)
        
        # Push argumentos en orden inverso
        for arg_reg in reversed(arg_regs):
            self.emit(f"  PUSH8 R{arg_reg:02d}  ; Push argumento")
        
        # Llamar a la función
        self.emit(f"  CALL {func_name}")
        
        # Limpiar argumentos de la pila
        if len(arg_regs) > 0:
            stack_clean = len(arg_regs) * 8
            self.emit(f"  ADDV8 R15, {stack_clean}  ; Limpiar argumentos")
        
        # El resultado está en R00
        result_reg = 0
        return result_reg


# Función de utilidad para uso externo
def generate_code(ast, symbol_table):
    """
    Función de conveniencia para generar código.
    
    Args:
        ast: Árbol de sintaxis abstracta (nodo Program)
        symbol_table: Tabla de símbolos del análisis semántico
    
    Returns:
        String con el código ensamblador Atlas
    """
    generator = CodeGenerator(ast, symbol_table)
    return generator.generate()