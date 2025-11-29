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
        # Las variables globales se ubican en direcciones absolutas desde 0x1000
        self.global_data_base = 0x1000  # Dirección base de variables globales
        
        # === GESTIÓN DE OFFSETS ===
        # Los offsets se asignan dinámicamente durante la generación porque
        # el análisis semántico no conoce las convenciones de la arquitectura Atlas
        
        # Offset para próxima variable global (incrementa secuencialmente)
        self.global_offset_counter = 0
        
        # Offset para próxima variable local (crece negativamente desde BP)
        self.local_offset_counter = 0
        
        # Offset para próximo parámetro (crece positivamente desde BP+16)
        self.param_offset_counter = 0
    
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
        """
        Asigna un offset secuencial a una variable global.
        
        ESTRATEGIA DE UBICACIÓN DE VARIABLES GLOBALES:
        
        Las variables globales se almacenan en memoria de forma contigua empezando
        desde self.global_data_base (0x1000). Cada variable ocupa el espacio
        determinado por su tipo, y el contador se incrementa para la siguiente.
        
        Ejemplo de layout en memoria:
        
        Código SPL:
            entero8 x = 10;      // 8 bytes
            flotante pi = 3.14;  // 4 bytes
            entero4 z = 42;      // 4 bytes
        
        Layout en memoria:
            Dirección  Variable  Offset  Tamaño
            ─────────────────────────────────────
            0x1000     x         0       8 bytes
            0x1008     pi        8       4 bytes
            0x100C     z         12      4 bytes
            0x1010     (libre)   16      ...
        
        El acceso se realiza con instrucciones absolutas:
            LOAD8 R00, 0x1000     ; Cargar x
            STORE4 R01, 0x1008    ; Guardar pi
        
        Args:
            symbol: Símbolo de la tabla con atributo 'type'
        
        Returns:
            int: Offset relativo desde global_data_base
        
        Side Effects:
            Incrementa self.global_offset_counter por el tamaño del tipo
        """
        # Extraer nombre del tipo del símbolo
        type_name = symbol.type.name if hasattr(symbol.type, 'name') else str(symbol.type)
        
        # Obtener tamaño en bytes del tipo
        size = self.get_type_size(type_name)
        
        # El offset actual es donde se ubicará esta variable
        offset = self.global_offset_counter
        
        # Avanzar el contador para la próxima variable global
        # (layout secuencial sin gaps)
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
        size = self.get_type_size(type_name)
        
        if symbol.kind == 'parameter':
            # ===  PARÁMETROS: OFFSETS POSITIVOS ===
            # Estructura del frame antes de BP:
            # BP+8:  dirección de retorno (guardada por CALL)
            # BP+16: primer parámetro
            # BP+24: segundo parámetro
            # BP+32: tercer parámetro...
            #
            # Convención simplificada: cada parámetro ocupa 8 bytes en stack
            # (alineación, aunque el tipo real sea más pequeño)
            offset = 16 + (self.param_offset_counter * 8)
            self.param_offset_counter += 1
            return offset
        else:
            # === VARIABLES LOCALES: OFFSETS NEGATIVOS ===
            # Crecen hacia abajo desde BP:
            # BP-4: primera local (si es entero4)
            # BP-8: segunda local (si es entero4)
            # BP-16: tercera local (si es entero8)
            #
            # Respetan tamaño real del tipo (sin padding)
            self.local_offset_counter -= size
            offset = self.local_offset_counter
            return offset
    
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
        
        # Inicializar Stack Pointer en una ubicación segura
        # Usar mitad de la memoria disponible (0x8000 para memoria de 64KB)
        # Esto deja espacio para código en la parte baja y stack en la parte alta
        self.emit("; Inicializar Stack Pointer (R15) y Frame Pointer (R14)")
        self.emit("MOVV8 R15, 0x8000        ; SP en mitad de memoria (32KB)")
        self.emit("MOV8 R14, R15            ; BP = SP (frame inicial)")
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
        self.emit("; Fin del código ejecutable")
    
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
        # El análisis semántico puede haber calculado el tamaño total necesario
        func_symbol = self.symbol_table.lookup(node.name)
        local_space = 0
        if func_symbol and hasattr(func_symbol, 'local_size'):
            local_space = func_symbol.local_size
        
        if local_space > 0:
            # Mover SP hacia arriba para reservar espacio
            # Stack crece hacia direcciones mayores en Atlas
            self.emit(f"  SUBV8 R15, {local_space}  ; Reservar {local_space} bytes para locales")
        
        self.emit("")
        
        # === CUERPO DE LA FUNCIÓN ===
        # Generar código para cada statement del cuerpo
        self.emit(f"  ; Cuerpo de {node.name}")
        for stmt in node.body.statements:
            self.visit_stmt(stmt)
        
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
            
            # Cargar la dirección: BP + offset
            addr_reg = self.new_temp()
            self.emit(f"  MOVV8 R{addr_reg:02d}, {symbol.offset}")
            self.emit(f"  ADD8 R{addr_reg:02d}, R14  ; Dirección = BP + offset")
            self.emit(f"  {store_instr} R{reg:02d}, R{addr_reg:02d}  ; {node.name} = valor_inicial")
    
    def visit_assignment(self, node):
        """
        Genera código para una asignación de variable.
        
        FORMAS DE ASIGNACIÓN:
        
        1. Variable global:
           variable = expresión;
           
           Genera:
           <código para evaluar expresión en Rx>
           STORE{size} Rx, dirección_absoluta
        
        2. Variable local o parámetro:
           variable = expresión;
           
           Genera:
           <código para evaluar expresión en Rx>
           MOVV8 Ry, offset
           ADD8 Ry, R14             ; Ry = BP + offset
           STORER{size} Rx, Ry      ; [Ry] = Rx
        
        DISTINCIÓN GLOBAL vs LOCAL:
        
        Usamos symbol_table.global_scope.lookup_local() para determinar si
        una variable es global. Solo variables en el scope global usan
        direcciones absolutas; todas las demás usan offsets desde BP.
        
        ASIGNACIÓN DINÁMICA DE OFFSETS:
        
        Si una variable no tiene offset asignado (caso raro, debería estar
        asignado por el análisis semántico o en visit_function_decl), lo
        asignamos dinámicamente usando _assign_global_offset o
        _assign_local_offset según corresponda.
        
        Ejemplo 1 - Global:
            Código SPL:
                entero8 x;
                x = 42;
            
            Genera:
                MOVV8 R00, 42
                STORE8 R00, 0x1000    ; x está en 0x1000
        
        Ejemplo 2 - Local:
            Código SPL:
                funcion f() {
                    entero4 temp;
                    temp = 100;
                }
            
            Genera:
                MOVV4 R00, 100        ; Valor a asignar
                MOVV8 R01, -4         ; Offset de temp
                ADD8 R01, R14         ; R01 = BP-4 (dirección)
                STORER4 R00, R01      ; [BP-4] = 100
        
        Ejemplo 3 - Parámetro:
            Código SPL:
                funcion f(entero8 a) {
                    a = 50;
                }
            
            Genera:
                MOVV8 R00, 50         ; Valor a asignar
                MOVV8 R01, 16         ; Offset de parámetro 'a'
                ADD8 R01, R14         ; R01 = BP+16 (dirección)
                STORER8 R00, R01      ; [BP+16] = 50
        
        Args:
            node: Nodo Assignment con lvalue (Identifier) y rvalue (Expression)
        """
        # Validar que lvalue sea un identificador simple
        # (asignación a arrays/structs no implementada aún)
        if not isinstance(node.lvalue, Identifier):
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
        
        # === EVALUAR EXPRESIÓN DEL LADO DERECHO ===
        # El resultado queda en un registro temporal
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
                LOAD8 R00, 0x1000     ; Cargar x (global en 0x1000)
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
        
        # === PASO 1: EVALUAR ARGUMENTOS ===
        # Evaluar cada argumento y guardar registros donde quedaron
        arg_regs = []
        for arg in node.arguments:
            # Asumir entero8 por defecto (simplificación)
            # TODO: Obtener tipo real del parámetro formal
            arg_reg = self.visit_expr(arg, "entero8")
            arg_regs.append(arg_reg)
        
        # === PASO 2: PUSH ARGUMENTOS EN ORDEN INVERSO ===
        # Esto coloca el primer argumento más cerca de BP en memoria
        for arg_reg in reversed(arg_regs):
            self.emit(f"  PUSH8 R{arg_reg:02d}  ; Push argumento")
        
        # === PASO 3: LLAMAR A LA FUNCIÓN ===
        # CALL hace:
        # - PUSH de la dirección de retorno (IP actual + 1)
        # - JMP a la función
        self.emit(f"  CALL {func_name}  ; Llamar a {func_name}")
        
        # === PASO 4: LIMPIAR STACK (Caller-cleanup) ===
        # Después de RET, el caller es responsable de eliminar los argumentos
        # Cada argumento ocupó 8 bytes (simplificación)
        if len(arg_regs) > 0:
            stack_clean = len(arg_regs) * 8
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