"""
Generador de Código para el compilador SPL -> Atlas Assembly
Traduce el Árbol de Sintaxis Abstracta (AST) a código ensamblador Atlas
"""

from .ast_nodes import *
from .symbol_table import SymbolTable, Symbol


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
        Inicializa el generador de código Atlas desde el AST y tabla de símbolos.
        
        Args:
            ast: Nodo raíz del AST (Program) con declaraciones globales y funciones
            symbol_table: Tabla de símbolos con información de tipos, scopes y símbolos
        
        CONVENCIONES DE ARQUITECTURA ATLAS:
        
        1. REGISTROS (64 bits cada uno):
           - R00-R13: Registros de propósito general para temporales y cálculos
           - R14 (BP): Base Pointer, apunta al inicio del stack frame actual
           - R15 (SP): Stack Pointer, apunta al tope del stack
           - R00: Registro especial, también se usa para valores de retorno
        
        2. MEMORIA (64KB total, arquitectura von Neumann):
           - 0x0000-0x0FFF: Código ejecutable y datos constantes (4KB)
           - 0x1000-0x7FFF: Variables globales y heap dinámico (28KB)
           - 0x8000-0xFFFF: Stack (32KB, crece hacia arriba)
        
        3. STACK FRAME (convención de llamada):
           Cuando se llama a una función f(a, b):
           
           Memoria:                     Offset desde BP:
           ┌──────────────────────┐
           │ param_b (segundo)    │     BP+24
           ├──────────────────────┤
           │ param_a (primero)    │     BP+16
           ├──────────────────────┤
           │ dirección_retorno    │     BP+8  (guardada por CALL)
           ├──────────────────────┤
           │ BP_anterior          │  ←  BP (guardado por PUSH8 R14)
           ├──────────────────────┤
           │ variable_local_1     │     BP-4
           ├──────────────────────┤
           │ variable_local_2     │     BP-8
           └──────────────────────┘
           
           - Parámetros: offsets POSITIVOS desde BP (BP+16, BP+24, ...)
           - Locales: offsets NEGATIVOS desde BP (BP-4, BP-8, ...)
           - Stack crece hacia ARRIBA (incrementa direcciones)
        
        4. INSTRUCCIONES Y TAMAÑOS:
           Sufijos indican tamaño de operación:
           - Sufijo 1: 1 byte  (caracter, booleano)
           - Sufijo 2: 2 bytes (entero2)
           - Sufijo 4: 4 bytes (entero4, flotante)
           - Sufijo 8: 8 bytes (entero8, doble, puntero)
           
           Prefijo F para operaciones de punto flotante:
           - FADD4, FSUB4, FMUL4, FDIV4 (flotante)
           - FADD8, FSUB8, FMUL8, FDIV8 (doble)
        
        5. CONVENCIÓN DE LLAMADA A FUNCIÓN:
           a) Caller: PUSH argumentos en orden inverso (último primero)
           b) Caller: CALL función (pushea IP de retorno)
           c) Callee: PUSH8 R14 (guarda BP anterior)
           d) Callee: MOV8 R14, R15 (BP apunta al nuevo frame)
           e) Callee: SUBV8 R15, tamaño_locales (reserva espacio)
           f) Callee: ejecuta cuerpo de función
           g) Callee: MOV8 R00, valor_retorno (si hay return)
           h) Callee: MOV8 R15, R14 (libera locales)
           i) Callee: POP8 R14 (restaura BP anterior)
           j) Callee: RET (pop IP y retorna)
           k) Caller: ADDV8 R15, tamaño_args (limpia argumentos del stack)
        """
        self.ast = ast
        self.symbol_table = symbol_table
        self.code = []  # Acumulador de líneas de código ensamblador
        
        # === GESTIÓN DE REGISTROS TEMPORALES ===
        # Usamos R00-R13 como registros temporales (14 disponibles)
        # R14 y R15 están reservados para BP y SP respectivamente
        self.temp_counter = 0  # Índice del próximo registro temporal (0-13)
        self.max_temps = 14    # Límite de registros temporales
        
        # === GESTIÓN DE ETIQUETAS ===
        # Generamos etiquetas únicas para estructuras de control (if, while, for)
        self.label_counter = 0  # Contador global para garantizar unicidad
        
        # === STACK DE CONTEXTO DE BUCLES ===
        # Para implementar break y continue, necesitamos saber a qué labels saltar
        # Cada entrada es: (label_inicio, label_fin)
        # - break salta a label_fin (salir del bucle)
        # - continue salta a label_inicio (próxima iteración)
        self.loop_stack = []
        
        # === CONTEXTO DE FUNCIÓN ACTUAL ===
        # Almacena el nombre de la función que se está generando
        # Usado para validar returns y generar labels de epílogo
        self.current_function = None
        
        # === LAYOUT DE MEMORIA PARA VARIABLES GLOBALES ===
        # Las variables globales se ubican en direcciones absolutas después del código (64KB)
        self.global_data_base = 0x10000  # Dirección base de variables globales (inicio del heap/global)
        self.string_data_base = 0x18000  # Dirección base de strings y datos (zona separada)
        
        # === GESTIÓN DE OFFSETS ===
        # Los offsets se asignan dinámicamente durante la generación porque
        # el análisis semántico no conoce las convenciones de la arquitectura Atlas
        
        # Offset para próxima variable global (incrementa secuencialmente)
        self.global_offset_counter = 0
        
        # Offset para próxima variable local (crece negativamente desde BP)
        self.local_offset_counter = 0
        
        # Offset para próximo parámetro (crece positivamente desde BP+16)
        self.param_offset_counter = 0
        
        # === DICCIONARIO DE FUNCIONES ===
        # Mapea nombre de función -> nodo FunctionDecl
        # Usado para obtener tipos de parámetros en llamadas a función
        self.function_decls = {}
        
        # === STRING LITERALS ===
        # Diccionario para almacenar strings literales y sus etiquetas
        # key: contenido del string, value: etiqueta única
        self.string_literals = {}
        self.string_counter = 0
        # Diccionario para almacenar direcciones de strings
        # key: contenido del string, value: dirección en memoria
        self.string_addresses = {}
    
    def generate(self):
        """
        Punto de entrada principal: genera el código completo.
        
        Returns:
            String con el código ensamblador Atlas completo
        """
        # Primero, recolectar todos los string literals del AST
        self._collect_string_literals(self.ast)
        
        self.emit("; Código generado por el compilador SPL -> Atlas")
        self.emit("; Arquitectura: Atlas CPU (64-bit)")
        self.emit("")
        
        # Verificar si se necesitan las bibliotecas
        self.needs_memory = self._has_dynamic_memory(self.ast)
        needs_stdio = self._has_print_stmt(self.ast)
        
        # Incluir bibliotecas necesarias
        if needs_stdio or self.needs_memory:
            if needs_stdio:
                self._include_stdio()
            else:
                # Solo memory.asm sin stdio
                self._include_memory()
        
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
    
    def get_expression_type(self, expr):
        """
        Obtiene el tipo de una expresión consultando la tabla de símbolos.
        
        Args:
            expr: Nodo de expresión del AST
        
        Returns:
            Type object o None si no se puede determinar
        """
        from compiler.ast_nodes import Identifier, IntLiteral, FloatLiteral, StringLiteral, CharLiteral, MemberAccess, ArrayAccess
        
        if isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup(expr.name)
            return symbol.type if symbol else None
        
        elif isinstance(expr, ArrayAccess):
            # Para acceso a arreglo, obtener el tipo base del arreglo
            # arreglo[0] tiene el mismo tipo que los elementos del arreglo
            if isinstance(expr.array, Identifier):
                symbol = self.symbol_table.lookup(expr.array.name)
                if symbol and symbol.type:
                    # El tipo del arreglo puede ser Type('flotante[10]') o similar
                    # Necesitamos extraer el tipo base
                    base_type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
                    # Remover los corchetes si existen: 'flotante[10]' -> 'flotante'
                    if '[' in base_type_name:
                        base_type_name = base_type_name.split('[')[0]
                    from compiler.ast_nodes import Type
                    return Type(base_type_name, is_pointer=False)
            return None
        
        elif isinstance(expr, MemberAccess):
            # Obtener tipo de la estructura
            if isinstance(expr.object, Identifier):
                obj_symbol = self.symbol_table.lookup(expr.object.name)
                if obj_symbol:
                    struct_type = obj_symbol.type.name if hasattr(obj_symbol.type, 'name') else str(obj_symbol.type)
                    if expr.is_pointer:
                        struct_type = struct_type.rstrip('*')
                    
                    # Buscar la estructura
                    struct_symbol = self.symbol_table.lookup(struct_type)
                    if struct_symbol and hasattr(struct_symbol, 'members'):
                        # Buscar el miembro
                        for member in struct_symbol.members:
                            if member.name == expr.member:
                                return member.var_type
            return None
        
        elif isinstance(expr, IntLiteral):
            from compiler.ast_nodes import Type
            return Type('entero8', is_pointer=False)
        
        elif isinstance(expr, FloatLiteral):
            from compiler.ast_nodes import Type
            return Type('doble', is_pointer=False)
        
        elif isinstance(expr, StringLiteral):
            from compiler.ast_nodes import Type
            return Type('cadena', is_pointer=False)
        
        elif isinstance(expr, CharLiteral):
            from compiler.ast_nodes import Type
            return Type('caracter', is_pointer=False)
        
        # Para otros tipos de expresiones, retornar None
        return None
    
    def get_sized_instruction(self, base_instr, type_name):
        """
        Genera el nombre completo de una instrucción con sufijo de tamaño apropiado.
        
        La arquitectura Atlas requiere especificar el tamaño de datos en cada operación.
        Este método automatiza la generación del nombre correcto basándose en el tipo.
        
        REGLAS DE SUFIJOS:
        
        1. Instrucciones ENTERAS: sufijo indica bytes
           - ADD1, SUB1, MUL1, DIV1 (1 byte)
           - ADD4, SUB4, MUL4, DIV4 (4 bytes)
           - ADD8, SUB8, MUL8, DIV8 (8 bytes)
           - LOAD4, STORE4, MOV4, etc.
        
        2. Instrucciones FLOTANTES: prefijo F + sufijo de bytes
           - FADD4, FSUB4, FMUL4, FDIV4 (flotante, 32 bits)
           - FADD8, FSUB8, FMUL8, FDIV8 (doble, 64 bits)
        
        3. Instrucciones SIN SUFIJO (operan en modo registro):
           - CMP, CMPV (comparaciones)
           - JMP, JEQ, JNE, JLT, JGT (saltos)
           - CALL, RET, PUSH8, POP8
        
        Ejemplos:
        - get_sized_instruction("ADD", "entero4")  → "ADD4"
        - get_sized_instruction("MUL", "doble")    → "FMUL8"
        - get_sized_instruction("LOAD", "entero8") → "LOAD8"
        - get_sized_instruction("CMP", "entero4")  → "CMP"
        
        Args:
            base_instr: Instrucción base sin sufijo (ej: "ADD", "LOAD", "STORE")
            type_name: Tipo SPL (ej: "entero4", "flotante", "doble", "caracter")
        
        Returns:
            String con instrucción completa incluyendo sufijo/prefijo apropiado
        """
        # Obtener tamaño en bytes del tipo
        size = self.get_type_size(type_name)
        
        # Instrucciones que NO requieren sufijo de tamaño
        # Estas operan directamente con valores de registro o son saltos
        if base_instr in ["CMP", "CMPV", "JMP", "JEQ", "JNE", "JLT", "JGT", "JLE", "JGE"]:
            return base_instr
        
        # Instrucciones de punto flotante: prefijo F + sufijo de tamaño
        # Solo para operaciones aritméticas (ADD, SUB, MUL, DIV)
        if type_name in ["flotante", "doble"]:
            if base_instr in ["ADD", "SUB", "MUL", "DIV"]:
                return f"F{base_instr}{size}"
        
        # Instrucciones enteras estándar: sufijo de tamaño
        # Cubre: ADD, SUB, MUL, DIV, LOAD, STORE, MOV, etc.
        return f"{base_instr}{size}"
    
    def _assign_global_offset(self, symbol):
        """Asigna un offset secuencial a una variable global.

        Las variables globales se colocan de forma contigua comenzando en
        ``self.global_data_base`` (por defecto situado después del espacio de código).

        Args:
            symbol: Símbolo de la tabla con atributo `type`.

        Returns:
            int: Offset relativo (en bytes) desde ``self.global_data_base``.
        """
        # Extraer nombre del tipo del símbolo
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)

        # Obtener tamaño en bytes del tipo
        size = self.get_type_size(type_name)

        # Offset actual donde se ubicará esta variable (relativo a global_data_base)
        offset = self.global_offset_counter

        # Avanzar el contador para la próxima variable global
        self.global_offset_counter += size

        return offset
    
    def _assign_local_offset(self, symbol):
        """
        Asigna un offset relativo a BP (R14) para variables locales y parámetros.
        
        CONVENCIÓN DE STACK FRAME DETALLADA:
        
        Cuando se llama a una función: funcion(arg1, arg2, arg3)
        
        1. CALLER (quien llama):
           - PUSH8 arg3  ; Push argumentos en orden INVERSO
           - PUSH8 arg2
           - PUSH8 arg1
           - CALL funcion ; Pushea dirección de retorno
        
        2. CALLEE (la función):
           - PUSH8 R14        ; Guarda BP anterior
           - MOV8 R14, R15    ; BP apunta al inicio del frame
           - SUBV8 R15, N     ; Reserva espacio para N bytes de locales
        
        3. RESULTADO EN MEMORIA:
        
        Dirección    Contenido           Offset    Acceso
        ──────────────────────────────────────────────────────────────
        BP+32        arg3 (tercero)      +32       LOADR Rx, [BP+32]
        BP+24        arg2 (segundo)      +24       LOADR Rx, [BP+24]
        BP+16        arg1 (primero)      +16       LOADR Rx, [BP+16]
        BP+8         ret_address         +8        (usado por RET)
        BP           old_BP              0    ←    BP apunta aquí
        BP-4         local1 (entero4)    -4        LOADR Rx, [BP-4]
        BP-8         local2 (entero4)    -8        LOADR Rx, [BP-8]
        BP-16        local3 (entero8)    -16       LOADR Rx, [BP-16]
        BP-N         ...                 -N
        
        REGLAS DE ASIGNACIÓN:
        
        A) PARÁMETROS (offsets POSITIVOS):
           - Primer parámetro: BP+16 (porque BP+8 es ret_address, BP es old_BP)
           - Segundo parámetro: BP+24 (incremento de 8 bytes)
           - Tercer parámetro: BP+32
           - etc.
           
           Simplificación: Todos los parámetros ocupan 8 bytes en stack,
           independiente de su tipo real (convención de alineación).
        
        B) VARIABLES LOCALES (offsets NEGATIVOS):
           - Primera local: BP - tamaño_tipo
           - Segunda local: BP - acumulado_anterior - tamaño_tipo
           - Crecen hacia abajo (direcciones menores)
           
           Respetan tamaño real: entero4 ocupa 4 bytes, entero8 ocupa 8.
        
        EJEMPLO COMPLETO:
        
        Código SPL:
            funcion sumar(entero8 a, entero8 b) -> entero8 {
                entero4 temp;      // local1: BP-4
                entero8 result;    // local2: BP-12 (BP-4-8)
                ...
            }
        
        Layout:
            BP+24: b (parámetro 2)
            BP+16: a (parámetro 1)
            BP+8:  ret_address
            BP:    old_BP
            BP-4:  temp (4 bytes)
            BP-12: result (8 bytes)
        
        Args:
            symbol: Símbolo con atributos 'kind' ("parameter" o "local") y 'type'
        
        Returns:
            int: Offset relativo a BP (positivo para params, negativo para locales)
        
        Side Effects:
            - Incrementa param_offset_counter si es parámetro
            - Decrementa local_offset_counter si es local
        """
        # Extraer nombre del tipo
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        # Obtener tamaño en bytes del tipo
        if hasattr(symbol.type, 'dimensions') and symbol.type.dimensions:
            # Para arrays multidimensionales: tamaño_elemento * total_elementos
            element_size = self.get_type_size(type_name)
            total_elements = 1
            for dim in symbol.type.dimensions:
                total_elements *= dim
            size = element_size * total_elements
        elif hasattr(symbol.type, 'is_array') and symbol.type.is_array:
            # Compatibilidad con arrays 1D antiguos
            element_size = self.get_type_size(type_name)
            array_size = symbol.type.array_size
            size = element_size * array_size
        else:
            size = self.get_type_size(type_name)
        
        if symbol.kind == 'parameter':
            # ===  PARÁMETROS: OFFSETS NEGATIVOS ===
            # Con stack creciendo hacia arriba (PUSH incrementa SP):
            # - PUSH args en orden inverso
            # - CALL pushea dirección retorno (8 bytes)
            # - PUSH8 R14 guarda BP anterior (8 bytes)
            # - MOV8 R14, R15 establece nuevo BP
            #
            # Estructura:
            # BP-8:  old_BP guardado
            # BP-16: dirección retorno  
            # BP-16-size1: primer parámetro
            # BP-16-size1-size2: segundo parámetro...
            #
            # Cada parámetro ocupa su tamaño real en bytes
            self.param_offset_counter += size
            offset = -(16 + self.param_offset_counter)
            return offset
        else:
            # === VARIABLES LOCALES: OFFSETS POSITIVOS ===
            # Crecen hacia arriba desde BP (stack crece hacia arriba):
            # BP+0: primera local (si es entero4)
            # BP+4: segunda local (si es entero4)
            # BP+12: tercera local (si es entero8)
            #
            # Respetan tamaño real del tipo (sin padding)
            offset = self.local_offset_counter
            self.local_offset_counter += size
            return offset
    
    def is_float_type(self, type_name):
        """Determina si un tipo es de punto flotante."""
        return type_name in ["flotante", "doble"]
    
    def _has_print_stmt(self, node):
        """
        Detecta recursivamente si hay algún PrintStmt en el AST.
        
        Args:
            node: Nodo del AST a inspeccionar
        
        Returns:
            bool: True si encuentra al menos un PrintStmt
        """
        from compiler.ast_nodes import PrintStmt, Program, FunctionDecl, Block, IfStmt, WhileStmt, ForStmt
        
        if isinstance(node, PrintStmt):
            return True
        
        # Buscar en nodos que pueden contener statements
        if isinstance(node, Program):
            return any(self._has_print_stmt(decl) for decl in node.declarations)
        
        elif isinstance(node, FunctionDecl):
            return self._has_print_stmt(node.body) if node.body else False
        
        elif isinstance(node, Block):
            return any(self._has_print_stmt(stmt) for stmt in node.statements)
        
        elif isinstance(node, IfStmt):
            return (self._has_print_stmt(node.then_block) or 
                    (self._has_print_stmt(node.else_block) if node.else_block else False))
        
        elif isinstance(node, WhileStmt):
            return self._has_print_stmt(node.body)
        
        elif isinstance(node, ForStmt):
            return self._has_print_stmt(node.body)
        
        return False
    
    def _has_dynamic_memory(self, node):
        """
        Detecta recursivamente si hay uso de memoria dinámica (nuevo/eliminar) en el AST.
        
        Args:
            node: Nodo del AST a inspeccionar
        
        Returns:
            bool: True si encuentra al menos un NewExpr o DeleteExpr
        """
        from compiler.ast_nodes import NewExpr, DeleteExpr, Program, FunctionDecl, Block, IfStmt, WhileStmt, ForStmt, ExprStmt, Assignment, BinaryOp, UnaryOp, VarDecl, ReturnStmt
        
        if isinstance(node, (NewExpr, DeleteExpr)):
            return True
        
        # Buscar en nodos que pueden contener expresiones
        if isinstance(node, Program):
            return any(self._has_dynamic_memory(decl) for decl in node.declarations)
        
        elif isinstance(node, FunctionDecl):
            return self._has_dynamic_memory(node.body) if node.body else False
        
        elif isinstance(node, Block):
            return any(self._has_dynamic_memory(stmt) for stmt in node.statements)
        
        elif isinstance(node, (IfStmt, WhileStmt)):
            result = self._has_dynamic_memory(node.condition) if hasattr(node, 'condition') else False
            if isinstance(node, IfStmt):
                result = result or self._has_dynamic_memory(node.then_block)
                if node.else_block:
                    result = result or self._has_dynamic_memory(node.else_block)
            else:
                result = result or self._has_dynamic_memory(node.body)
            return result
        
        elif isinstance(node, ForStmt):
            result = False
            if node.init:
                result = result or self._has_dynamic_memory(node.init)
            if node.condition:
                result = result or self._has_dynamic_memory(node.condition)
            if node.update:
                result = result or self._has_dynamic_memory(node.update)
            result = result or self._has_dynamic_memory(node.body)
            return result
        
        elif isinstance(node, (ExprStmt, ReturnStmt)):
            expr = node.expression if hasattr(node, 'expression') else None
            return self._has_dynamic_memory(expr) if expr else False
        
        elif isinstance(node, (Assignment, BinaryOp)):
            left = getattr(node, 'left', None) or getattr(node, 'lvalue', None)
            right = getattr(node, 'right', None) or getattr(node, 'rvalue', None)
            result = False
            if left:
                result = result or self._has_dynamic_memory(left)
            if right:
                result = result or self._has_dynamic_memory(right)
            return result
        
        elif isinstance(node, UnaryOp):
            return self._has_dynamic_memory(node.operand)
        
        elif isinstance(node, VarDecl):
            return self._has_dynamic_memory(node.init_value) if node.init_value else False
        
        return False
    
    def _collect_string_literals(self, node):
        """
        Recorre el AST y recolecta todos los string literals.
        Asigna una etiqueta única a cada string.
        """
        from compiler.ast_nodes import StringLiteral, Program, FunctionDecl, Block, PrintStmt, VarDecl, Assignment, ReturnStmt, IfStmt, WhileStmt, ForStmt, BinaryOp, UnaryOp, FunctionCall, ExprStmt
        
        if isinstance(node, StringLiteral):
            if node.value not in self.string_literals:
                label = f"__STR{self.string_counter}"
                self.string_literals[node.value] = label
                self.string_counter += 1
        
        # Recorrer recursivamente los nodos que pueden contener string literals
        elif isinstance(node, Program):
            for decl in node.declarations:
                self._collect_string_literals(decl)
        
        elif isinstance(node, FunctionDecl):
            if node.body:
                self._collect_string_literals(node.body)
        
        elif isinstance(node, Block):
            for stmt in node.statements:
                self._collect_string_literals(stmt)
        
        elif isinstance(node, PrintStmt):
            for expr in node.expressions:
                self._collect_string_literals(expr)
        
        elif isinstance(node, ExprStmt):
            self._collect_string_literals(node.expression)
        
        elif isinstance(node, VarDecl):
            if node.init_value:
                self._collect_string_literals(node.init_value)
        
        elif isinstance(node, Assignment):
            self._collect_string_literals(node.lvalue)
            self._collect_string_literals(node.rvalue)
        
        elif isinstance(node, ReturnStmt):
            if node.value:
                self._collect_string_literals(node.value)
        
        elif isinstance(node, IfStmt):
            self._collect_string_literals(node.condition)
            self._collect_string_literals(node.then_block)
            if node.else_block:
                self._collect_string_literals(node.else_block)
        
        elif isinstance(node, WhileStmt):
            self._collect_string_literals(node.condition)
            self._collect_string_literals(node.body)
        
        elif isinstance(node, ForStmt):
            if node.init:
                self._collect_string_literals(node.init)
            if node.condition:
                self._collect_string_literals(node.condition)
            if node.update:
                self._collect_string_literals(node.update)
            self._collect_string_literals(node.body)
        
        elif isinstance(node, BinaryOp):
            self._collect_string_literals(node.left)
            self._collect_string_literals(node.right)
        
        elif isinstance(node, UnaryOp):
            self._collect_string_literals(node.operand)
        
        elif isinstance(node, FunctionCall):
            for arg in node.arguments:
                self._collect_string_literals(arg)
    
    def _include_stdio(self):
        """Incluye el contenido de lib/stdio.asm en el código generado."""
        import os
        
        # Construir ruta a stdio.asm
        current_dir = os.path.dirname(__file__)
        stdio_path = os.path.join(current_dir, "..", "..", "lib", "stdio.asm")
        stdio_path = os.path.normpath(stdio_path)
        
        if os.path.exists(stdio_path):
            with open(stdio_path, 'r', encoding='utf-8') as f:
                # CRÍTICO: Saltar stdio.asm e ir directo al código de inicialización
                self.emit("; Saltar biblioteca stdio.asm e iniciar programa")
                self.emit("JMP __START_PROGRAM")
                self.emit("")
                self.emit("; === BIBLIOTECA stdio.asm ===")
                for line in f:
                    self.code.append(line.rstrip())
                self.emit("; === FIN BIBLIOTECA ===")
                self.emit("")
        else:
            self.emit(f"; ADVERTENCIA: No se encontró lib/stdio.asm en {stdio_path}")
            self.emit("")
        
        # Incluir memory.asm (siempre, ya que puede ser necesario para malloc/free)
        self._include_memory()
    
    def _include_memory(self):
        """Incluye el contenido de lib/memory.asm en el código generado."""
        import os
        
        current_dir = os.path.dirname(__file__)
        memory_path = os.path.join(current_dir, "..", "..", "lib", "memory.asm")
        memory_path = os.path.normpath(memory_path)
        
        # Si no hay stdio, necesitamos el JMP inicial
        if not self.code or "JMP __START_PROGRAM" not in self.code[0]:
            self.emit("; Saltar bibliotecas e iniciar programa")
            self.emit("JMP __START_PROGRAM")
            self.emit("")
        
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                self.emit("; === BIBLIOTECA memory.asm ===")
                for line in f:
                    self.code.append(line.rstrip())
                self.emit("; === FIN BIBLIOTECA ===")
                self.emit("")
        else:
            self.emit(f"; ADVERTENCIA: No se encontró lib/memory.asm en {memory_path}")
            self.emit("")
    
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
        
        # Primero procesar declaraciones de estructuras (metadata)
        for decl in node.declarations:
            if isinstance(decl, StructDecl):
                self.visit_struct_decl(decl)
        
        # Generar declaraciones globales
        for decl in node.declarations:
            if isinstance(decl, VarDecl):
                self.visit_global_var_decl(decl)
        
        self.emit("")
        self.emit("; === CÓDIGO DE INICIALIZACIÓN ===")
        self.emit("")
        self.emit("__START_PROGRAM:")
        self.emit("; Inicializar Stack Pointer en una ubicación segura")
        # Usar mitad de la memoria disponible (0x8000 para memoria de 64KB)
        # Esto deja espacio para código en la parte baja y stack en la parte alta
        self.emit("; Inicializar Stack Pointer (R15) y Frame Pointer (R14)")
        self.emit("; Nueva ubicación de stack: colocar al inicio de la zona de stack (0x1C000)")
        self.emit("MOVV8 R15, 0x1C000        ; SP en 0x1C000 (inicio de la región de stack)")
        self.emit("MOV8 R14, R15            ; BP = SP (frame inicial)")
        self.emit("")
        
        # Inicializar heap para malloc/free (solo si se usa memoria dinámica)
        if self.needs_memory:
            self.emit("; Inicializar heap para asignación dinámica")
            self.emit("CALL __init_heap")
            self.emit("")
        
        # Inicializar string literals en memoria (área separada 0x18000+)
        if self.string_literals:
            self.emit("; Inicializar string literals en memoria (área 0x18000+)")
            string_offset = 0
            for string_val, label in self.string_literals.items():
                addr = self.string_data_base + string_offset
                self.string_addresses[string_val] = addr
                self.emit(f"; {label} = \"{string_val}\" @ 0x{addr:X}")
                
                # Escribir string completo usando STORE1 (dirección absoluta)
                for i, char in enumerate(string_val):
                    char_addr = addr + i
                    self.emit(f"  MOVV1 R01, {ord(char)}  ; '{char}'")
                    self.emit(f"  STORE1 R01, {char_addr}  ; Escribir en 0x{char_addr:X}")
                
                # Escribir NULL terminator
                null_addr = addr + len(string_val)
                self.emit(f"  MOVV1 R01, 0  ; NULL")
                self.emit(f"  STORE1 R01, {null_addr}  ; Escribir en 0x{null_addr:X}")
                
                # Avanzar offset (para el siguiente string)
                string_offset += len(string_val) + 1
            
            self.emit("")
        
        # Llamar a la función principal
        self.emit("; Llamar a la función principal")
        main_func = self.symbol_table.lookup("principal")
        if main_func and main_func.kind == "function":
            self.emit("CALL principal")
            self.emit("JMP END_PROGRAM")
        else:
            self.emit("; ADVERTENCIA: No se encontró la función 'principal'")
            self.emit("PARAR")
        self.emit("")
        
        # Generar código para todas las funciones
        self.emit("; === FUNCIONES ===")
        self.emit("")
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                self.visit_function_decl(decl)
        
        self.emit("")
        self.emit("END_PROGRAM:")
        self.emit("; Fin del código ejecutable")
    
    def visit_global_var_decl(self, node):
        """
        Genera código para una declaración de variable global.
        
        Las variables globales se asignan a direcciones absolutas de memoria
        comenzando desde self.global_data_base.
        
        OPTIMIZACIÓN DE CONSTANTES:
        Las constantes no ocupan memoria, su valor se usa directamente como inmediato.
        """
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            return
        
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        size = self.get_type_size(type_name)
        
        # OPTIMIZACIÓN: Constantes no ocupan memoria
        if symbol.is_const:
            # Guardar el valor en el símbolo para uso posterior
            if node.init_value:
                if isinstance(node.init_value, (IntLiteral, FloatLiteral)):
                    symbol.const_value = node.init_value.value
                    self.emit(f"; Constante: {node.name} = {symbol.const_value} (tipo: {type_name}, no ocupa memoria)")
                else:
                    # Constante con expresión compleja (evaluar en tiempo de compilación si es posible)
                    self.emit(f"; Constante: {node.name} (tipo: {type_name}, expresión no evaluada en compile-time)")
            return
        
        # Variable normal: asignar memoria y offset si no está asignado
        if not hasattr(symbol, 'offset'):
            symbol.offset = self._assign_global_offset(symbol)
        
        address = self.global_data_base + symbol.offset
        self.emit(f"; Variable global: {node.name} (tipo: {type_name}, tamaño: {size} bytes, dirección: {address})")
        
        # Emit .DATA for the global variable (deterministic load-time initialization)
        # Format: .DATA <ADDR_HEX> <SIZE> <HEXBYTES> ; NAME=<symbol> ; RELOCS=
        if node.init_value:
            from compiler.ast_nodes import IntLiteral, FloatLiteral, CharLiteral, StringLiteral
            lit = node.init_value
            try:
                if isinstance(lit, IntLiteral) or isinstance(lit, CharLiteral):
                    # integer / char initializer
                    value = int(lit.value)
                    b = (value & ((1 << (size*8)) - 1)).to_bytes(size, byteorder='little', signed=False)
                    hexbytes = b.hex().upper()
                    self.emit(f".DATA {address:08X} {size} {hexbytes} ; NAME={node.name} ; RELOCS=")
                    self.emit(f"; {node.name} = {value} ({size} bytes)")
                elif isinstance(lit, FloatLiteral):
                    import struct
                    if size == 4:
                        b = struct.pack('<f', float(lit.value))
                    else:
                        b = struct.pack('<d', float(lit.value))
                    hexbytes = b.hex().upper()
                    self.emit(f".DATA {address:08X} {size} {hexbytes} ; NAME={node.name} ; RELOCS=")
                    self.emit(f"; {node.name} = {lit.value} ({size} bytes float)")
                elif isinstance(lit, StringLiteral):
                    # For string initializer for a global, store pointer/address or raw bytes?
                    # Here we emit raw bytes of the string (truncated/padded to size)
                    val_bytes = bytes(lit.value.encode('utf-8'))[:size]
                    if len(val_bytes) < size:
                        val_bytes = val_bytes + b'\x00' * (size - len(val_bytes))
                    hexbytes = val_bytes.hex().upper()
                    self.emit(f".DATA {address:08X} {size} {hexbytes} ; NAME={node.name} ; RELOCS=")
                    self.emit(f"; {node.name} = \"{lit.value}\" (string)")
                else:
                    # Complex initializer: emit zero-filled data and record the NAME
                    zero_bytes = (0).to_bytes(size, byteorder='little') * 1
                    hexbytes = zero_bytes.hex().upper()
                    self.emit(f".DATA {address:08X} {size} {hexbytes} ; NAME={node.name} ; RELOCS=")
                    self.emit(f"; {node.name} = <initializer emitted separately or requires relocations>")
            except Exception:
                zero_bytes = (0).to_bytes(size, byteorder='little') * 1
                hexbytes = zero_bytes.hex().upper()
                self.emit(f".DATA {address:08X} {size} {hexbytes} ; NAME={node.name} ; RELOCS=")
                self.emit(f"; {node.name} = <initializer error, zero-filled>")
    
    def visit_struct_decl(self, node):
        """
        Procesa declaración de estructura.
        Las estructuras no generan código ejecutable, solo metadata.
        
        Args:
            node: StructDecl con name y members (lista de VarDecl)
        """
        self.emit(f"; Estructura: {node.name}")
        
        # Calcular offsets y tamaño total de la estructura
        current_offset = 0
        for member in node.members:
            member_type = member.var_type.name if hasattr(member.var_type, 'name') else 'entero4'
            member_size = self.get_type_size(member_type)
            
            # Asignar offset al miembro
            member.offset = current_offset
            self.emit(f";   {member.name}: {member_type} (offset: {current_offset}, size: {member_size})")
            
            current_offset += member_size
        
        # Guardar metadata de la estructura en la tabla de símbolos
        struct_symbol = self.symbol_table.lookup(node.name)
        if struct_symbol:
            struct_symbol.members = node.members
            struct_symbol.size = current_offset
        
        self.emit(f";   Tamaño total: {current_offset} bytes")
        self.emit("")
    
    def visit_function_decl(self, node):
        """
        Genera código completo para una declaración de función.
        
        ESTRUCTURA DE UNA FUNCIÓN:
        
        nombre_funcion:           ; Label de entrada
          ; Prólogo
          PUSH8 R14              ; Guardar BP del caller
          MOV8 R14, R15          ; Establecer nuevo BP
          SUBV8 R15, N           ; Reservar N bytes para locales
          
          ; Cuerpo
          <código de statements>
          
        nombre_funcion_epilogue: ; Label de salida
          ; Epílogo
          MOV8 R15, R14          ; Liberar locales (SP = BP)
          POP8 R14               ; Restaurar BP del caller
          RET                    ; Retornar al caller
        
        CONVENCIÓN DE LLAMADA COMPLETA:
        
        Dado: funcion(a, b) -> resultado
        
        1. CALLER prepara llamada:
           PUSH8 valor_b         ; Pushear args en orden inverso
           PUSH8 valor_a
           CALL funcion          ; Pushea IP+1 y salta
        
        2. FUNCIÓN ejecuta PRÓLOGO:
           PUSH8 R14             ; Preservar BP del caller
           MOV8 R14, R15         ; BP apunta al nuevo frame base
           SUBV8 R15, local_size ; Reservar espacio para variables locales
        
        3. FUNCIÓN ejecuta CUERPO:
           - Accede parámetros: BP+16 (a), BP+24 (b)
           - Accede locales: BP-4, BP-8, etc.
           - Si hay return, coloca valor en R00 y salta a epilogue
        
        4. FUNCIÓN ejecuta EPÍLOGO:
           MOV8 R15, R14         ; SP = BP (libera locales)
           POP8 R14              ; Restaura BP del caller
           RET                   ; Pop IP de retorno y salta
        
        5. CALLER limpia stack:
           ADDV8 R15, 16         ; Elimina args (2 * 8 bytes)
           MOV8 resultado, R00   ; Obtiene valor de retorno
        
        GESTIÓN DE OFFSETS:
        
        Es crítico pre-asignar offsets a PARÁMETROS antes de procesar el cuerpo,
        porque las variables locales usan un contador negativo que no debe
        interferir con los parámetros (que usan contador positivo).
        
        Ejemplo:
            funcion calcular(entero8 x, entero4 y) -> entero8 {
                entero8 temp;
                entero4 result;
                ...
            }
        
        Pre-asignación:
            x.offset = 16      (parámetro 1)
            y.offset = 24      (parámetro 2)
        
        Durante el cuerpo:
            temp.offset = -8   (local 1, entero8)
            result.offset = -12 (local 2, entero4 después de entero8)
        
        Args:
            node: Nodo FunctionDecl con name, params, return_type, body
        """
        # === FUNCIONES EXTERNAS ===
        # Las funciones externas (is_extern=True) no tienen cuerpo ni código
        # Solo están declaradas para que el análisis semántico las reconozca
        if node.is_extern or node.body is None:
            # No generar código para funciones externas
            return
        
        # === REGISTRAR FUNCIÓN ===
        # Guardar el nodo de la función para poder consultar sus parámetros
        # cuando se haga una llamada a esta función
        self.function_decls[node.name] = node
        
        # === LABEL DE ENTRADA ===
        self.emit(f"{node.name}:  ; Función: {node.name}")
        
        # Establecer contexto de función actual (para returns)
        self.current_function = node.name
        
        # === ENTRAR AL SCOPE DE LA FUNCIÓN ===
        # CRÍTICO: Recrear el contexto de scope para que lookup() funcione
        # El análisis semántico ya creó estos scopes pero los destruyó con exit_scope()
        self.symbol_table.enter_scope(
            name=f"function_{node.name}",
            is_function=True,
            return_type=node.return_type
        )
        
        # Resetear contadores para nueva función
        self.reset_temps()              # Registros temporales desde R00
        self.local_offset_counter = 0   # Locales desde BP-0
        self.param_offset_counter = 0   # Parámetros desde BP+16
        
        # === DECLARAR PARÁMETROS EN EL SCOPE ACTUAL ===
        # Recrear los símbolos de parámetros en este scope
        for param in node.params:
            param_symbol = Symbol(param.name, param.var_type, param, kind='parameter')
            self.symbol_table.define(param_symbol)
        
        # === PRE-ASIGNACIÓN DE OFFSETS A PARÁMETROS ===
        # CRÍTICO: Hacer esto ANTES de procesar el cuerpo para que los
        # parámetros tengan offsets positivos establecidos y las locales
        # no interfieran con el contador de parámetros
        for param in node.params:
            param_symbol = self.symbol_table.lookup(param.name)
            if param_symbol and not hasattr(param_symbol, 'offset'):
                # Asignar offset positivo (BP+16, BP+24, ...)
                param_symbol.offset = self._assign_local_offset(param_symbol)
        
        # === PRÓLOGO DE LA FUNCIÓN ===
        # El prólogo configura el stack frame según la convención de llamada
        self.emit(f"  ; Prólogo de {node.name}")
        
        # Paso 1: Guardar BP del caller
        # Esto preserva la cadena de frames para poder hacer stack unwinding
        self.emit(f"  PUSH8 R14          ; Guardar BP del caller en stack")
        
        # Paso 2: Establecer nuevo BP
        # BP ahora apunta a la base del frame actual (donde está old_BP)
        self.emit(f"  MOV8 R14, R15      ; BP = SP (inicio del frame actual)")
        
        # Paso 3: Reservar espacio para variables locales
        # Calcular el tamaño total de variables locales antes de procesar el cuerpo
        # Nota: local_offset_counter será negativo y acumulará el espacio total
        # Por ahora, procesaremos el cuerpo y luego calcularemos
        # Guardar la posición actual para insertar la reserva después
        local_space_line_index = len(self.code)
        self.emit(f"  ; [PLACEHOLDER: Reservar espacio para locales]")
        
        self.emit("")
        
        # === CUERPO DE LA FUNCIÓN ===
        # Generar código para cada statement del cuerpo
        self.emit(f"  ; Cuerpo de {node.name}")
        for stmt in node.body.statements:
            self.visit_stmt(stmt)
        
        # Después de procesar el cuerpo, sabemos cuánto espacio necesitan las locales
        # local_offset_counter contiene el total usado (positivo, stack crece hacia arriba)
        local_space = self.local_offset_counter
        if local_space > 0:
            # Actualizar la línea placeholder con el valor real
            self.code[local_space_line_index] = f"  ADDV8 R15, {local_space}  ; Reservar {local_space} bytes para locales"
        else:
            # No hay locales, eliminar el placeholder
            self.code[local_space_line_index] = "  ; Sin variables locales"
        
        self.emit("")
        
        # === EPÍLOGO DE LA FUNCIÓN ===
        # El epílogo se ejecuta cuando:
        # 1. Se llega al final de la función sin return explícito
        # 2. Un return statement hace JMP a este label
        self.emit(f"{node.name}_epilogue:")
        self.emit(f"  ; Epílogo de {node.name}")
        
        # Paso 1: Liberar variables locales
        # Restaurar SP a la posición de BP (elimina locales)
        self.emit(f"  MOV8 R15, R14      ; SP = BP (liberar locales)")
        
        # Paso 2: Restaurar BP del caller
        # Pop del valor que guardamos en el prólogo
        self.emit(f"  POP8 R14           ; Restaurar BP del caller")
        
        # Paso 3: Retornar al caller
        # RET hace: IP = POP(); (salta a dirección de retorno)
        self.emit(f"  RET                ; Retornar al caller")
        self.emit("")
        
        # === SALIR DEL SCOPE DE LA FUNCIÓN ===
        # Emit local-symbol metadata so the loader can register local names at load time
        # We compute absolute addresses using the initial BP value used by the program (0x1C000)
        try:
            # initial SP set to 0x1C000 in program prologue; after CALL and function prologue
            # (CALL pushes return addr) and (PUSH8 R14 saves old BP) the effective BP is
            # initial SP + 16. Use that to compute absolute addresses for emitted .LOCAL metadata.
            stack_base = 0x1C000 + 16
            current_scope = self.symbol_table.current_scope
            # Emit .LOCAL entries for parameters and locals defined in this function scope
            for sym_name, sym in current_scope.symbols.items():
                if sym.kind in ('local', 'parameter'):
                    # determine size
                    type_name = sym.type.name if hasattr(sym.type, 'name') else str(sym.type)
                    size = self.get_type_size(type_name)
                    # Emit relative local metadata instead of absolute addresses.
                    # The loader/VM will resolve these at runtime using BP.
                    rel = getattr(sym, 'offset', 0)
                    # .LOCAL_REL <OFFSET> <SIZE> <NAME> ; FUNC=<func_name>
                    self.emit(f".LOCAL_REL {rel} {size} {sym.name} ; FUNC={node.name}")
        except Exception:
            # don't fail code generation on metadata emission problems
            self.emit(f"; ERROR: failed to emit local metadata for function {node.name}")

        self.symbol_table.exit_scope()
        
        # Limpiar contexto de función
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
        elif isinstance(node, PrintStmt):
            self.visit_print_stmt(node)
        elif isinstance(node, ExprStmt):
            self.visit_expr_stmt(node)
        elif isinstance(node, Block):
            self.visit_block(node)
        else:
            self.emit(f"  ; ERROR: Statement type {type(node).__name__} not handled!")
    
    def visit_local_var_decl(self, node):
        """
        Genera código para una declaración de variable local.
        
        Las variables locales se acceden mediante offset desde BP (R14).
        """
        # Buscar si ya existe el símbolo
        symbol = self.symbol_table.lookup(node.name)
        
        # Si no existe, crearlo y agregarlo al scope actual
        if not symbol:
            symbol = Symbol(node.name, node.var_type, node, kind='local')
            self.symbol_table.define(symbol)
        
        # Asignar offset si no existe
        if not hasattr(symbol, 'offset'):
            symbol.offset = self._assign_local_offset(symbol)
        
        self.emit(f"  ; Variable local: {node.name} (offset: {symbol.offset})")
        
        # Si tiene inicializador, almacenarlo
        if node.init_value:
            type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
            reg = self.visit_expr(node.init_value, type_name)
            store_instr = self.get_sized_instruction("STORER", type_name)
            mov_instr = self.get_sized_instruction("MOV", type_name)
            
            # CRÍTICO: Si el valor está en R00 (común para valores de retorno de funciones),
            # guardarlo en otro registro antes de calcular la dirección para evitar sobrescritura
            value_reg = reg
            if reg == 0:
                value_reg = self.new_temp()
                self.emit(f"  {mov_instr} R{value_reg:02d}, R{reg:02d}  ; Guardar valor de R00")
            
            # Cargar la dirección: BP + offset
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            self.emit(f"  {store_instr} R{value_reg:02d}, R{addr_reg:02d}  ; {node.name} = valor_inicial")
    
    def visit_assignment(self, node):
        """
        Genera código para una asignación de variable.
        
        FORMAS DE ASIGNACIÓN:
        
        1. Simple (=): variable = expresión
        2. Compuesta (+=, -=, *=, /=, %=): variable op= expresión
           Equivale a: variable = variable op expresión
        
        OPERADORES COMPUESTOS:
        Para i += 1:
        - Cargar valor actual de i
        - Sumar 1
        - Guardar resultado en i
        
        Args:
            node: Nodo Assignment con lvalue, operator, rvalue
        """
        # Validar que lvalue sea un identificador simple o acceso a miembro/array
        if isinstance(node.lvalue, MemberAccess):
            return self.visit_member_access_assignment(node)
        elif isinstance(node.lvalue, ArrayAccess):
            return self.visit_array_access_assignment(node)
        elif not isinstance(node.lvalue, Identifier):
            self.emit("  ; ADVERTENCIA: Asignación a expresión compleja no implementada")
            return
        
        # Obtener nombre y símbolo de la variable
        target_name = node.lvalue.name
        symbol = self.symbol_table.lookup(target_name)
        if not symbol:
            self.emit(f"  ; ERROR: Variable '{target_name}' no encontrada")
            return
        
        # Obtener tipo para generar instrucción con sufijo correcto
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        # === MANEJAR OPERADORES COMPUESTOS ===
        # Para +=, -=, *=, /=, %=: convertir a operación binaria
        if node.operator != '=':
            # Mapeo de operador compuesto a binario
            op_map = {
                '+=': '+',
                '-=': '-',
                '*=': '*',
                '/=': '/',
                '%=': '%'
            }
            if node.operator in op_map:
                # Crear nodo binario: variable op rvalue
                binary_op = BinaryOp(
                    left=node.lvalue,  # Identifier de la variable
                    operator=op_map[node.operator],
                    right=node.rvalue
                )
                # Evaluar como: variable = (variable op rvalue)
                reg = self.visit_expr(binary_op, type_name)
            else:
                self.emit(f"  ; ERROR: Operador '{node.operator}' no soportado")
                return
        else:
            # === ASIGNACIÓN SIMPLE ===
            # Evaluar expresión del lado derecho
            reg = self.visit_expr(node.rvalue, type_name)
        
        # === DETERMINAR SCOPE: GLOBAL vs LOCAL/PARÁMETRO ===
        # Una variable es global solo si está en el scope global
        # Locales y parámetros están en scopes de función
        is_global = (self.symbol_table.global_scope.lookup_local(target_name) is not None)
        
        if is_global:
            # === CASO 1: VARIABLE GLOBAL ===
            # Usar dirección absoluta: global_data_base + offset
            
            # Asignar offset si no existe (fallback de seguridad)
            if not hasattr(symbol, 'offset'):
                symbol.offset = self._assign_global_offset(symbol)
            
            # Calcular dirección absoluta
            address = self.global_data_base + symbol.offset
            
            # Generar instrucción STORE con tamaño apropiado
            store_instr = self.get_sized_instruction("STORE", type_name)
            self.emit(f"  {store_instr} R{reg:02d}, {address}  ; {target_name} = valor")
        else:
            # === CASO 2: VARIABLE LOCAL O PARÁMETRO ===
            # Usar offset relativo a BP (puede ser positivo o negativo)
            
            # Asignar offset si no existe (fallback de seguridad)
            if not hasattr(symbol, 'offset'):
                symbol.offset = self._assign_local_offset(symbol)
            
            # Generar instrucción STORER (Store Relative)
            store_instr = self.get_sized_instruction("STORER", type_name)
            
            # Paso 1: Calcular dirección efectiva en un registro temporal
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}  ; Offset desde BP")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            
            # Paso 2: Almacenar valor en la dirección calculada
            self.emit(f"  {store_instr} R{reg:02d}, R{addr_reg:02d}  ; {target_name} = valor")
    
    def visit_member_access_assignment(self, node):
        """Maneja asignación a miembros de estructura: obj.member = value o ptr->member = value"""
        if not isinstance(node.lvalue, MemberAccess):
            return
        
        member_node = node.lvalue
        
        # Obtener tipo del objeto/puntero
        if isinstance(member_node.object, Identifier):
            obj_symbol = self.symbol_table.lookup(member_node.object.name)
            if not obj_symbol:
                self.emit("  ; ERROR: Objeto no encontrado para acceso a miembro")
                return
            
            # Obtener tipo de estructura
            struct_type = obj_symbol.type.name if hasattr(obj_symbol.type, 'name') else str(obj_symbol.type)
            if member_node.is_pointer:
                # Remover el * del tipo para obtener el tipo base
                struct_type = struct_type.rstrip('*')
            
            # Buscar estructura en tabla de símbolos
            struct_symbol = self.symbol_table.lookup(struct_type)
            if not struct_symbol or not hasattr(struct_symbol, 'members'):
                self.emit(f"  ; ERROR: Estructura '{struct_type}' no encontrada")
                return
            
            # Buscar miembro en la estructura
            member_offset = None
            member_type = None
            for member in struct_symbol.members:
                if member.name == member_node.member:
                    member_offset = member.offset if hasattr(member, 'offset') else 0
                    member_type = member.var_type.name if hasattr(member.var_type, 'name') else 'entero4'
                    break
            
            if member_offset is None:
                self.emit(f"  ; ERROR: Miembro '{member_node.member}' no encontrado")
                return
            
            # Evaluar expresión del lado derecho
            value_reg = self.visit_expr(node.rvalue, member_type)
            
            # Calcular dirección del miembro
            if member_node.is_pointer:
                # ptr->member: cargar puntero y sumar offset
                ptr_reg = self.visit_identifier(member_node.object, 'entero8')
                addr_reg = self.new_temp()
                self.emit(f"  MOVV8 R{addr_reg:02d}, {member_offset}")
                self.emit(f"  ADD8 R{addr_reg:02d}, R{ptr_reg:02d}  ; Dirección del miembro")
            else:
                # obj.member: calcular dirección base del objeto + offset del miembro
                base_reg = self.new_temp()
                self.emit(f"  MOVV8 R{base_reg:02d}, {obj_symbol.offset}")
                self.emit(f"  ADD8 R{base_reg:02d}, R14  ; Base del objeto")
                addr_reg = self.new_temp()
                self.emit(f"  MOVV8 R{addr_reg:02d}, {member_offset}")
                self.emit(f"  ADD8 R{addr_reg:02d}, R{base_reg:02d}  ; Dirección del miembro")
            
            # Guardar valor
            store_instr = self.get_sized_instruction("STORER", member_type)
            self.emit(f"  {store_instr} R{value_reg:02d}, R{addr_reg:02d}  ; {member_node.member} = valor")
        else:
            self.emit("  ; ERROR: Acceso a miembro complejo no implementado")
    
    def visit_array_access_assignment(self, node):
        """Maneja asignación a elementos de array: arr[index] = value o arr[i][j] = value"""
        from compiler.ast_nodes import ArrayAccess, Identifier
        
        if not isinstance(node.lvalue, ArrayAccess):
            return
        
        array_node = node.lvalue
        
        # Recolectar todos los índices para acceso multidimensional
        indices = []
        current = array_node
        while isinstance(current, ArrayAccess):
            indices.insert(0, current.index)
            current = current.array
        
        # Obtener símbolo del array
        if isinstance(current, Identifier):
            array_symbol = self.symbol_table.lookup(current.name)
            if not array_symbol:
                self.emit("  ; ERROR: Array no encontrado")
                return
            
            # Obtener tipo del elemento
            element_type = array_symbol.type.name if hasattr(array_symbol.type, 'name') else 'entero4'
            element_size = self.get_type_size(element_type)
            
            # Obtener dimensiones del array
            if hasattr(array_symbol.type, 'dimensions') and array_symbol.type.dimensions:
                dimensions = array_symbol.type.dimensions
            else:
                dimensions = [array_symbol.type.array_size] if hasattr(array_symbol.type, 'array_size') else []
            
            if len(indices) != len(dimensions):
                self.emit(f"  ; ERROR: Dimensiones incorrectas: esperaba {len(dimensions)}, recibió {len(indices)}")
                return
            
            # Evaluar valor a asignar PRIMERO (antes de calcular offset para evitar sobreescribir registros)
            value_reg = self.visit_expr(node.rvalue, element_type)
            
            # Calcular offset multidimensional
            offset_reg = self.visit_expr(indices[0], 'entero4')
            
            for i in range(1, len(indices)):
                # offset *= dimensions[i]
                dim_reg = self.new_temp()
                self.emit(f"  MOVV4 R{dim_reg:02d}, {dimensions[i]}")
                self.emit(f"  MUL4 R{offset_reg:02d}, R{dim_reg:02d}")
                
                # offset += indices[i]
                index_reg = self.visit_expr(indices[i], 'entero4')
                self.emit(f"  ADD4 R{offset_reg:02d}, R{index_reg:02d}")
            
            # Multiplicar por tamaño del elemento
            size_reg = self.new_temp()
            self.emit(f"  MOVV4 R{size_reg:02d}, {element_size}")
            self.emit(f"  MUL4 R{offset_reg:02d}, R{size_reg:02d}")
            
            # Obtener dirección base del array
            base_reg = self.new_temp()
            if hasattr(array_symbol, 'offset'):
                self.emit(f"  MOVV8 R{base_reg:02d}, {array_symbol.offset}")
                self.emit(f"  ADD8 R{base_reg:02d}, R14  ; Base del array")
            
            # Sumar offset al base
            self.emit(f"  ADD8 R{base_reg:02d}, R{offset_reg:02d}  ; Dirección del elemento")
            
            # Guardar valor
            store_instr = self.get_sized_instruction("STORER", element_type)
            self.emit(f"  {store_instr} R{value_reg:02d}, R{base_reg:02d}  ; arr[...] = valor")
        else:
            self.emit("  ; ERROR: Acceso a array complejo no implementado")
    
    def visit_if_stmt(self, node):
        """
        Genera código para un statement if con soporte para elif.
        
        Estructura:
          <evaluar condición if>
          CMP + JEQ elif1_label
          <then_block>
          JMP end_label
        elif1_label:
          <evaluar condición elif1>
          CMP + JEQ elif2_label (o else_label)
          <elif1_block>
          JMP end_label
        elif2_label:
          ...
        else_label:
          <else_block>
        end_label:
        """
        end_label = self.new_label("ENDIF")
        
        # Evaluar condición principal
        cond_reg = self.visit_expr(node.condition, "booleano")
        
        # Determinar siguiente etiqueta
        if node.elif_clauses:
            next_label = self.new_label("ELIF")
        elif node.else_block:
            next_label = self.new_label("ELSE")
        else:
            next_label = end_label
        
        # Si la condición principal es falsa, saltar a siguiente sección
        self.emit(f"  CMPV R{cond_reg:02d}, 0")
        self.emit(f"  JEQ {next_label}")
        
        # Bloque then
        self.visit_stmt(node.then_block)
        self.emit(f"  JMP {end_label}")
        
        # Generar código para cada cláusula elif
        for i, elif_clause in enumerate(node.elif_clauses):
            self.emit(f"{next_label}:")
            
            # Evaluar condición elif
            elif_cond_reg = self.visit_expr(elif_clause.condition, "booleano")
            
            # Determinar siguiente etiqueta
            if i < len(node.elif_clauses) - 1:
                next_label = self.new_label("ELIF")
            elif node.else_block:
                next_label = self.new_label("ELSE")
            else:
                next_label = end_label
            
            # Si la condición elif es falsa, saltar a siguiente sección
            self.emit(f"  CMPV R{elif_cond_reg:02d}, 0")
            self.emit(f"  JEQ {next_label}")
            
            # Bloque elif
            self.visit_stmt(elif_clause.block)
            self.emit(f"  JMP {end_label}")
        
        # Bloque else (si existe)
        if node.else_block:
            self.emit(f"{next_label}:")
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
    
    def visit_print_stmt(self, node):
        """Genera código para imprimir()."""
        self.emit("  ; imprimir()")
        
        # Si no hay expresiones, solo imprimir newline
        if not node.expressions:
            self.emit("  CALL __print_newline")
            return
        
        # Imprimir cada expresión
        for expr in node.expressions:
            # Primero obtener el tipo de la expresión
            expr_type = self.get_expression_type(expr)
            type_name = expr_type.name if expr_type else 'entero8'
            
            # Evaluar la expresión con su tipo correcto
            reg = self.visit_expr(expr, type_name)
            
            # Determinar qué función de impresión usar según el tipo
            # Cadenas (puntero a char)
            if type_name == 'cadena' or (type_name == 'caracter' and expr_type and expr_type.pointer_level > 0):
                self.emit(f"  PUSH8 R{reg:02d}")
                self.emit("  CALL __print_string")
                self.emit(f"  ADDV8 R15, 8  ; Limpiar stack")
            
            # Carácter individual
            elif type_name == 'caracter':
                self.emit(f"  PUSH8 R{reg:02d}")
                self.emit("  CALL __print_char")
                self.emit(f"  ADDV8 R15, 8  ; Limpiar stack")
            
            # Números flotantes (incluir flotante y doble)
            elif type_name in ['flotante', 'doble']:
                self.emit(f"  PUSH4 R{reg:02d}")
                self.emit("  CALL __print_float")
                self.emit(f"  ADDV8 R15, 4  ; Limpiar stack")
            
            # Números enteros o tipo desconocido
            else:
                self.emit(f"  PUSH8 R{reg:02d}")
                self.emit("  CALL __print_int8")
                self.emit(f"  ADDV8 R15, 8  ; Limpiar stack")
        
        # Salto de línea final
        self.emit("  CALL __print_newline")
    
    def visit_expr_stmt(self, node):
        """Genera código para un statement de expresión (ej: llamada a función o assignment)."""
        # ExprStmt puede contener una expresión o un assignment
        if isinstance(node.expression, Assignment):
            self.visit_assignment(node.expression)
        else:
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
        elif isinstance(node, MemberAccess):
            return self.visit_member_access(node, expected_type)
        elif isinstance(node, ArrayAccess):
            return self.visit_array_access(node, expected_type)
        elif isinstance(node, NewExpr):
            return self.visit_new_expr(node, expected_type)
        elif isinstance(node, DeleteExpr):
            self.visit_delete_expr(node)
            return 0  # delete no retorna valor
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
            # Cargar la dirección del string literal
            addr = self.string_addresses.get(node.value)
            label = self.string_literals.get(node.value, "STR")
            if addr is not None:
                self.emit(f"  MOVV8 R{reg:02d}, 0x{addr:X}  ; {label}")
            else:
                self.emit(f"  MOVV8 R{reg:02d}, 0  ; ERROR: String no inicializado")
        else:
            self.emit(f"  MOVV8 R{reg:02d}, 0  ; Literal no soportado")
        
        return reg
    
    def visit_identifier(self, node, expected_type):
        """
        Genera código para leer el valor de una variable.
        
        ESTRATEGIAS DE CARGA SEGÚN SCOPE:
        
        1. Variable GLOBAL:
           Usa dirección absoluta calculada como: global_data_base + offset
           
           Genera:
           LOAD{size} Rx, dirección_absoluta
        
        2. Variable LOCAL o PARÁMETRO:
           Usa offset relativo a BP (puede ser positivo o negativo)
           
           Genera:
           MOVV8 Ry, offset
           ADD8 Ry, R14             ; Ry = BP + offset
           LOADR{size} Rx, Ry       ; Rx = [Ry]
        
        DETECCIÓN DE SCOPE:
        
        Una variable es global si y solo si está definida en el scope global.
        Usamos symbol_table.global_scope.lookup_local() que busca SOLO en
        ese scope sin subir por la cadena de scopes.
        
        ASIGNACIÓN DINÁMICA DE OFFSETS:
        
        Si una variable no tiene offset asignado, se asigna dinámicamente:
        - Globales: offset secuencial desde 0
        - Parámetros: offset positivo desde BP+16
        - Locales: offset negativo desde BP-tamaño
        
        Esta asignación dinámica es un fallback de seguridad. Normalmente,
        los offsets ya fueron asignados en visit_function_decl (parámetros)
        o visit_local_var_decl (locales).
        
        Ejemplo 1 - Leer global:
            Código SPL:
                entero8 x = 10;
                entero8 y = x + 5;
            
            Genera (para x + 5):
                LOAD8 R00, 0x10000     ; Cargar x (global en 0x10000)
                MOVV8 R01, 5
                ADD8 R00, R01
        
        Ejemplo 2 - Leer local:
            Código SPL:
                funcion f() {
                    entero4 temp = 100;
                    entero4 result = temp * 2;
                }
            
            Genera (para temp * 2):
                MOVV8 R01, -4         ; Offset de temp
                ADD8 R01, R14         ; R01 = BP-4
                LOADR4 R00, R01       ; R00 = [BP-4] (cargar temp)
                MOVV4 R02, 2
                MUL4 R00, R02
        
        Ejemplo 3 - Leer parámetro:
            Código SPL:
                funcion calcular(entero8 a, entero8 b) -> entero8 {
                    retornar a + b;
                }
            
            Genera (para a + b):
                MOVV8 R01, 16         ; Offset de 'a'
                ADD8 R01, R14         ; R01 = BP+16
                LOADR8 R00, R01       ; R00 = [BP+16] (cargar a)
                
                MOVV8 R02, 24         ; Offset de 'b'
                ADD8 R02, R14         ; R02 = BP+24
                LOADR8 R03, R02       ; R03 = [BP+24] (cargar b)
                
                ADD8 R00, R03         ; R00 = a + b
        
        Args:
            node: Nodo Identifier con atributo 'name'
            expected_type: Tipo esperado del resultado (para seleccionar instrucción)
        
        Returns:
            int: Número de registro temporal donde quedó cargado el valor
        """
        # Buscar símbolo en la tabla
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            # Variable no encontrada: generar error y retornar 0
            reg = self.new_temp()
            self.emit(f"  ; ERROR: Variable '{node.name}' no encontrada en tabla de símbolos")
            self.emit(f"  MOVV8 R{reg:02d}, 0  ; Valor por defecto")
            return reg
        
        # Asignar registro temporal para el resultado
        reg = self.new_temp()
        
        # Extraer nombre del tipo
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        # === OPTIMIZACIÓN: CONSTANTES USAN VALORES INMEDIATOS ===
        # Si es constante con valor conocido, usar MOVV directamente
        if symbol.is_const and hasattr(symbol, 'const_value'):
            mov_instr = self.get_sized_instruction("MOVV", type_name)
            
            # Para flotantes, convertir a hexadecimal IEEE 754
            if type_name in ["flotante", "doble"]:
                import struct
                if type_name == "flotante":
                    hex_val = struct.unpack('>I', struct.pack('>f', float(symbol.const_value)))[0]
                    self.emit(f"  {mov_instr} R{reg:02d}, 0x{hex_val:X}  ; Constante {node.name} = {symbol.const_value}")
                else:  # doble
                    hex_val = struct.unpack('>Q', struct.pack('>d', float(symbol.const_value)))[0]
                    self.emit(f"  {mov_instr} R{reg:02d}, 0x{hex_val:X}  ; Constante {node.name} = {symbol.const_value}")
            else:
                # Enteros: usar valor directo
                self.emit(f"  {mov_instr} R{reg:02d}, {symbol.const_value}  ; Constante {node.name}")
            
            return reg
        
        # === DETERMINAR SCOPE: GLOBAL vs LOCAL/PARÁMETRO ===
        # lookup_local busca SOLO en ese scope, no en padres
        is_global = (self.symbol_table.global_scope.lookup_local(node.name) is not None)
        
        if is_global:
            # === CASO 1: VARIABLE GLOBAL ===
            # Cargar desde dirección absoluta
            
            # Asignar offset si no existe (fallback)
            if not hasattr(symbol, 'offset'):
                symbol.offset = self._assign_global_offset(symbol)
            
            # Calcular dirección absoluta
            address = self.global_data_base + symbol.offset
            
            # Generar instrucción LOAD con tamaño apropiado
            load_instr = self.get_sized_instruction("LOAD", type_name)
            self.emit(f"  {load_instr} R{reg:02d}, {address}  ; Cargar {node.name} (global)")
        else:
            # === CASO 2: VARIABLE LOCAL O PARÁMETRO ===
            # Cargar usando offset relativo a BP
            
            # Asignar offset si no existe (fallback)
            if not hasattr(symbol, 'offset'):
                symbol.offset = self._assign_local_offset(symbol)
            
            # Generar instrucción LOADR (Load Relative)
            load_instr = self.get_sized_instruction("LOADR", type_name)
            
            # Paso 1: Calcular dirección efectiva en un registro temporal
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}  ; Offset desde BP")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            
            # Paso 2: Cargar valor desde la dirección calculada
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
            '%': 'MOD',  # Operador módulo
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
        elif node.operator == '&&':
            # Operador lógico AND - usar AND8 (bitwise funciona para booleanos)
            self.emit(f"  MOV8 R{result_reg:02d}, R{left_reg:02d}")
            self.emit(f"  AND8 R{result_reg:02d}, R{right_reg:02d}  ; AND lógico")
        elif node.operator == '||':
            # Operador lógico OR - usar OR8 (bitwise funciona para booleanos)
            self.emit(f"  MOV8 R{result_reg:02d}, R{left_reg:02d}")
            self.emit(f"  OR8 R{result_reg:02d}, R{right_reg:02d}  ; OR lógico")
        else:
            # Operadores aritméticos
            instr = self.get_sized_instruction(base_instr, expected_type)
            mov_instr = self.get_sized_instruction("MOV", expected_type)
            self.emit(f"  {mov_instr} R{result_reg:02d}, R{left_reg:02d}")
            self.emit(f"  {instr} R{result_reg:02d}, R{right_reg:02d}")
        
        return result_reg
    
    def visit_unary_op(self, node, expected_type):
        """Genera código para operaciones unarias: -, !, ++, --"""
        
        # Incremento/decremento requieren lvalue
        if node.operator in ['++', '--']:
            if not isinstance(node.operand, Identifier):
                self.emit(f"  ; ERROR: {node.operator} requiere variable")
                return self.new_temp()
            
            var_name = node.operand.name
            symbol = self.symbol_table.lookup(var_name)
            if not symbol:
                self.emit(f"  ; ERROR: Variable '{var_name}' no encontrada")
                return self.new_temp()
            
            type_name = symbol.type.name if hasattr(symbol.type, 'name') else 'entero4'
            
            # Cargar valor actual
            current_reg = self.visit_identifier(node.operand, type_name)
            
            # Incrementar o decrementar
            if node.operator == '++':
                add_instr = self.get_sized_instruction("ADDV", type_name)
                self.emit(f"  {add_instr} R{current_reg:02d}, 1  ; Incrementar")
            else:  # --
                sub_instr = self.get_sized_instruction("SUBV", type_name)
                self.emit(f"  {sub_instr} R{current_reg:02d}, 1  ; Decrementar")
            
            # Guardar nuevo valor
            is_global = (self.symbol_table.global_scope.lookup_local(var_name) is not None)
            if is_global:
                address = self.global_data_base + symbol.offset
                store_instr = self.get_sized_instruction("STORE", type_name)
                self.emit(f"  {store_instr} R{current_reg:02d}, {address}  ; Guardar {var_name}")
            else:
                addr_reg = self.new_temp()
                self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
                self.emit(f"  ADD8 R{addr_reg:02d}, R14")
                store_instr = self.get_sized_instruction("STORER", type_name)
                self.emit(f"  {store_instr} R{current_reg:02d}, R{addr_reg:02d}  ; Guardar {var_name}")
            
            # Retornar valor (post-incremento retorna valor original, pre-incremento el nuevo)
            # Por simplicidad, retornamos el nuevo valor
            return current_reg
        
        # Operadores normales (-, !)
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
    
    def visit_member_access(self, node, expected_type):
        """Genera código para acceso a miembro: obj.member o ptr->member"""
        if not isinstance(node.object, Identifier):
            self.emit("  ; ERROR: Acceso a miembro de expresión compleja no implementado")
            return self.new_temp()
        
        obj_symbol = self.symbol_table.lookup(node.object.name)
        if not obj_symbol:
            self.emit("  ; ERROR: Objeto no encontrado")
            return self.new_temp()
        
        # Obtener tipo de estructura
        struct_type = obj_symbol.type.name if hasattr(obj_symbol.type, 'name') else str(obj_symbol.type)
        if node.is_pointer:
            struct_type = struct_type.rstrip('*')
        
        # Buscar estructura
        struct_symbol = self.symbol_table.lookup(struct_type)
        if not struct_symbol or not hasattr(struct_symbol, 'members'):
            self.emit(f"  ; ERROR: Estructura '{struct_type}' no encontrada")
            return self.new_temp()
        
        # Buscar miembro
        member_offset = None
        member_type = None
        for member in struct_symbol.members:
            if member.name == node.member:
                member_offset = member.offset if hasattr(member, 'offset') else 0
                member_type = member.var_type.name if hasattr(member.var_type, 'name') else 'entero4'
                break
        
        if member_offset is None:
            self.emit(f"  ; ERROR: Miembro '{node.member}' no encontrado")
            return self.new_temp()
        
        # Calcular dirección y cargar valor
        if node.is_pointer:
            # ptr->member
            ptr_reg = self.visit_identifier(node.object, 'entero8')
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {member_offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R{ptr_reg:02d}")
        else:
            # obj.member
            base_reg = self.new_temp()
            self.emit(f"  MOVV8 R{base_reg:02d}, {obj_symbol.offset}")
            self.emit(f"  ADD8 R{base_reg:02d}, R14")
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {member_offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R{base_reg:02d}")
        
        # Cargar valor del miembro
        result_reg = self.new_temp()
        load_instr = self.get_sized_instruction("LOADR", member_type)
        self.emit(f"  {load_instr} R{result_reg:02d}, R{addr_reg:02d}  ; Cargar {node.member}")
        return result_reg
    
    def visit_array_access(self, node, expected_type):
        """Genera código para acceso a array: arr[index] o arr[i][j]"""
        from compiler.ast_nodes import ArrayAccess, Identifier
        
        # Recolectar todos los índices para acceso multidimensional
        indices = []
        current = node
        while isinstance(current, ArrayAccess):
            indices.insert(0, current.index)  # Insertar al inicio para mantener orden
            current = current.array
        
        # Obtener el identificador base
        if not isinstance(current, Identifier):
            self.emit("  ; ERROR: Array complejo no implementado")
            return self.new_temp()
        
        array_symbol = self.symbol_table.lookup(current.name)
        if not array_symbol:
            self.emit("  ; ERROR: Array no encontrado")
            return self.new_temp()
        
        element_type = array_symbol.type.name if hasattr(array_symbol.type, 'name') else 'entero4'
        element_size = self.get_type_size(element_type)
        
        # Obtener dimensiones del array
        if hasattr(array_symbol.type, 'dimensions') and array_symbol.type.dimensions:
            dimensions = array_symbol.type.dimensions
        else:
            dimensions = [array_symbol.type.array_size] if hasattr(array_symbol.type, 'array_size') else []
        
        # Calcular offset total para arrays multidimensionales
        # Para arr[i][j] con dims [D1][D2]: offset = (i * D2 + j) * element_size
        # Para arr[i][j][k] con dims [D1][D2][D3]: offset = ((i * D2 + j) * D3 + k) * element_size
        
        if len(indices) != len(dimensions):
            self.emit(f"  ; ERROR: Dimensiones incorrectas: esperaba {len(dimensions)}, recibió {len(indices)}")
            return self.new_temp()
        
        # Evaluar primer índice
        offset_reg = self.visit_expr(indices[0], 'entero4')
        
        # Para cada dimensión subsecuente: offset = offset * dim[i+1] + index[i+1]
        for i in range(1, len(indices)):
            # offset *= dimensions[i]
            dim_reg = self.new_temp()
            self.emit(f"  MOVV4 R{dim_reg:02d}, {dimensions[i]}")
            self.emit(f"  MUL4 R{offset_reg:02d}, R{dim_reg:02d}")
            
            # offset += indices[i]
            index_reg = self.visit_expr(indices[i], 'entero4')
            self.emit(f"  ADD4 R{offset_reg:02d}, R{index_reg:02d}")
        
        # Multiplicar por tamaño del elemento
        size_reg = self.new_temp()
        self.emit(f"  MOVV4 R{size_reg:02d}, {element_size}")
        self.emit(f"  MUL4 R{offset_reg:02d}, R{size_reg:02d}")
        
        # Dirección base
        base_reg = self.new_temp()
        self.emit(f"  MOVV8 R{base_reg:02d}, {array_symbol.offset}")
        self.emit(f"  ADD8 R{base_reg:02d}, R14")
        self.emit(f"  ADD8 R{base_reg:02d}, R{offset_reg:02d}")
        
        # Cargar elemento
        result_reg = self.new_temp()
        load_instr = self.get_sized_instruction("LOADR", element_type)
        self.emit(f"  {load_instr} R{result_reg:02d}, R{base_reg:02d}")
        return result_reg
    
    def visit_new_expr(self, node, expected_type):
        """Genera código para nuevo Tipo (malloc)"""
        # Obtener tamaño del tipo
        type_name = node.type.name if hasattr(node.type, 'name') else 'entero4'
        
        # Verificar si es una estructura para obtener su tamaño total
        struct_symbol = self.symbol_table.lookup(type_name)
        if struct_symbol and struct_symbol.kind == 'struct' and hasattr(struct_symbol.node, 'total_size'):
            type_size = struct_symbol.node.total_size
        else:
            type_size = self.get_type_size(type_name)
        
        # Llamar a función de sistema malloc (debe estar implementada)
        size_reg = self.new_temp()
        self.emit(f"  MOVV8 R{size_reg:02d}, {type_size}  ; Tamaño a asignar para {type_name}")
        self.emit(f"  PUSH8 R{size_reg:02d}  ; Argumento para malloc")
        self.emit(f"  CALL __malloc  ; Asignar memoria")
        self.emit(f"  ADDV8 R15, 8  ; Limpiar argumento")
        self.emit(f"  ; R00 contiene puntero a memoria asignada")
        
        return 0  # malloc retorna en R00
    
    def visit_delete_expr(self, node):
        """Genera código para eliminar ptr (free)"""
        # Evaluar expresión del puntero
        ptr_reg = self.visit_expr(node.expression, 'entero8')
        
        # Llamar a free
        self.emit(f"  PUSH8 R{ptr_reg:02d}  ; Argumento para free")
        self.emit(f"  CALL __free  ; Liberar memoria")
        self.emit(f"  ADDV8 R15, 8  ; Limpiar argumento")
    
    def visit_function_call(self, node, expected_type):
        """
        Genera código para una llamada a función.
        
        CONVENCIÓN DE LLAMADA (Calling Convention):
        
        1. CALLER (quien llama):
           a) Evaluar cada argumento y guardar en registro temporal
           b) PUSH argumentos en orden INVERSO (último primero)
           c) CALL función (pushea IP de retorno y salta)
           d) Limpiar stack (ADDV8 SP, tamaño_args)
           e) Obtener resultado desde R00
        
        2. CALLEE (la función llamada):
           a) Ejecuta prólogo (guarda BP, reserva locales)
           b) Accede parámetros como variables locales con offset positivo
           c) Ejecuta cuerpo
           d) Coloca resultado en R00 (si retorna algo)
           e) Ejecuta epílogo (restaura BP, limpia locales, RET)
        
        ORDEN DE ARGUMENTOS EN STACK:
        
        Para la llamada: funcion(arg1, arg2, arg3)
        
        Stack antes de CALL:
        ┌────────────┐
        │ arg1       │ ← Primer push (último argumento se pushea primero)
        ├────────────┤
        │ arg2       │
        ├────────────┤
        │ arg3       │
        └────────────┘ ← SP aquí
        
        Stack después de CALL (dentro de la función):
        ┌────────────┐
        │ arg1       │ ← BP+16 (primer parámetro)
        ├────────────┤
        │ arg2       │ ← BP+24 (segundo parámetro)
        ├────────────┤
        │ arg3       │ ← BP+32 (tercer parámetro)
        ├────────────┤
        │ ret_addr   │ ← BP+8 (guardada por CALL)
        ├────────────┤
        │ old_BP     │ ← BP (guardado por prólogo)
        └────────────┘
        
        POR QUÉ ORDEN INVERSO:
        
        Pushear en orden inverso hace que el primer parámetro quede más
        cerca de BP, facilitando el acceso secuencial (BP+16, BP+24, ...).
        
        EJEMPLO COMPLETO:
        
        Código SPL:
            entero8 suma(entero8 a, entero8 b) {
                retornar a + b;
            }
            
            funcion principal() {
                entero8 x = suma(10, 20);
            }
        
        Código generado para llamada:
            ; Evaluar argumentos
            MOVV8 R00, 10          ; arg1 = 10
            MOVV8 R01, 20          ; arg2 = 20
            
            ; Push en orden inverso
            PUSH8 R01              ; Push 20 (segundo arg)
            PUSH8 R00              ; Push 10 (primer arg)
            
            ; Llamar
            CALL suma              ; Pushea IP+1, salta a 'suma'
            
            ; Limpiar stack (2 args * 8 bytes)
            ADDV8 R15, 16          ; SP += 16 (elimina argumentos)
            
            ; Resultado en R00
            MOV8 R02, R00          ; x = resultado
        
        Código generado para 'suma':
            suma:
              PUSH8 R14            ; Guarda BP
              MOV8 R14, R15        ; BP = SP
              
              ; Cargar a (BP+16)
              MOVV8 R01, 16
              ADD8 R01, R14
              LOADR8 R00, R01
              
              ; Cargar b (BP+24)
              MOVV8 R02, 24
              ADD8 R02, R14
              LOADR8 R03, R02
              
              ; a + b
              ADD8 R00, R03        ; Resultado en R00
              
            suma_epilogue:
              MOV8 R15, R14
              POP8 R14
              RET                  ; Retorna con resultado en R00
        
        VALOR DE RETORNO:
        
        Siempre se retorna en R00. Este método retorna 0 para indicar
        que el resultado está en R00, no en otro registro temporal.
        
        Args:
            node: Nodo FunctionCall con 'function' (Identifier) y 'arguments' (lista)
            expected_type: Tipo esperado del resultado (no usado actualmente)
        
        Returns:
            int: 0 (indica que resultado está en R00)
        """
        # Extraer nombre de la función
        if isinstance(node.function, Identifier):
            func_name = node.function.name
        else:
            # Caso raro: llamada a expresión compleja
            func_name = "UNKNOWN_FUNCTION"
            self.emit(f"  ; ADVERTENCIA: Llamada a función no identificada")
        
        # === PASO 1: OBTENER INFORMACIÓN DE LA FUNCIÓN ===
        # Buscar el nodo de la función para conocer los tipos de parámetros
        param_types = []
        if func_name in self.function_decls:
            func_node = self.function_decls[func_name]
            if hasattr(func_node, 'params'):
                param_types = [p.var_type for p in func_node.params]
        
        # === PASO 2: EVALUAR ARGUMENTOS ===
        # Evaluar cada argumento con su tipo correspondiente
        arg_regs = []
        arg_types = []
        for i, arg in enumerate(node.arguments):
            # Obtener tipo del parámetro formal si existe
            if i < len(param_types):
                param_type_node = param_types[i]
                # param_types[i] es un Type node, extraer el nombre
                if hasattr(param_type_node, 'name'):
                    type_name = param_type_node.name
                elif hasattr(param_type_node, 'base_type'):
                    type_name = param_type_node.base_type
                else:
                    type_name = str(param_type_node)
            else:
                type_name = "entero8"  # Default fallback
            
            arg_reg = self.visit_expr(arg, type_name)
            arg_regs.append(arg_reg)
            arg_types.append(type_name)
        
        # === PASO 3: PUSH ARGUMENTOS EN ORDEN INVERSO ===
        # Esto coloca el primer argumento más cerca de BP en memoria
        for arg_reg, arg_type in zip(reversed(arg_regs), reversed(arg_types)):
            # Usar el tamaño correcto según el tipo
            type_size = self.get_type_size(arg_type)
            push_instr = self.get_sized_instruction("PUSH", arg_type)
            self.emit(f"  {push_instr} R{arg_reg:02d}  ; Push argumento ({arg_type})")
        
        # === PASO 4: LLAMAR A LA FUNCIÓN ===
        # CALL hace:
        # - PUSH de la dirección de retorno (IP actual + 1)
        # - JMP a la función
        self.emit(f"  CALL {func_name}  ; Llamar a {func_name}")
        
        # === PASO 5: LIMPIAR STACK (Caller-cleanup) ===
        # Después de RET, el caller es responsable de eliminar los argumentos
        # Sumar el tamaño real de cada argumento
        if len(arg_regs) > 0:
            stack_clean = sum(self.get_type_size(t) for t in arg_types)
            self.emit(f"  ADDV8 R15, {stack_clean}  ; Limpiar {len(arg_regs)} argumentos del stack")
        
        # === PASO 5: RESULTADO EN R00 ===
        # Por convención, el valor de retorno siempre está en R00
        # Retornamos 0 para indicar esto
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