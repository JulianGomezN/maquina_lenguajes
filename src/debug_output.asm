; Código generado por el compilador SPL -> Atlas
; Arquitectura: Atlas CPU (64-bit)

; Saltar biblioteca stdio.asm e iniciar programa
JMP __START_PROGRAM

; === BIBLIOTECA stdio.asm ===
; ============================================================================
; BIBLIOTECA STDIO - Entrada/Salida Estándar
; ============================================================================

; INPUT ----------------------------------------------------------------------------
;
; leer cadena y ponerla en memoria
; R2 apunta a donde empieza la cadena
; termina hasta encontrar 0 (NULL)
INPUT_STRING:
    PUSH8 R01
    PUSH8 R02
    PUSH8 R03

WAIT_INPUT:
    LOADIO R03, 0x200
    CMPV R03, 0xFF
    JEQ WAIT_INPUT    ; esperar carácter valido

    CMPV R03, 0
    JEQ FIN_INPUT_LINE     ; caracter null

    STORER1 R03, R02         ; buffer[i] = char
    ADDV8 R02, 1
    JMP WAIT_INPUT

FIN_INPUT_LINE:
    MOVV8 R03, 0
    STORER1 R03, R02          ; terminar cadena
    POP8 R03
    POP8 R02
    POP8 R01
    RET

; ----------------------------------------------------
; INPUT_INT: Leer una cadena numérica y convertirla a entero
; Entrada:
;   R2 = puntero al buffer donde guardar la entrada
; Salida:
;   R1 = entero leído
; ----------------------------------------------------

INPUT_INT:
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04
    PUSH8 R05
    PUSH8 R06      ; R06 será el flag de signo

    ; Leer texto a buffer[R02]
    CALL INPUT_STRING

    MOVV8 R01, 0       ; acumulador
    MOVV8 R06, 1       ; signo = +1

    ; Revisar primer carácter
    LOADR1 R03, R02
    CMPV R03, 45       ; '-' ?
    JNE CHECK_PLUS

    ; es negativo
    MOVV8 R06, -1
    ADDV8 R02, 1        ; avanzar al siguiente carácter
    JMP START_PARSE

CHECK_PLUS:
    CMPV R03, 43       ; '+' ?
    JNE START_PARSE
    ADDV8 R02, 1        ; saltar '+' si existe

START_PARSE:
CONVERT_LOOP:
    LOADR1 R03, R02
    CMPV R03, 0
    JEQ APPLY_SIGN

    ; ASCII → dígito
    SUBV8 R03, 48

    ; R01 = R01 * 10
    MOV8 R04, R01
    MOVV8 R05, 10
    MUL8 R04, R05
    MOV8 R01, R04

    ; R01 += dígito
    ADD8 R01, R03

    ADDV8 R02, 1
    JMP CONVERT_LOOP

APPLY_SIGN:
    ; si R06 == -1, entonces R01 = -R01
    CMPV R06, -1
    JNE END_INPUT_INT

    ; R01 = -R01
    MOVV8 R04, 0
    SUB8 R04, R01
    MOV8 R01, R04

END_INPUT_INT:
    POP8 R06
    POP8 R05
    POP8 R04
    POP8 R03
    POP8 R02
    RET

; OUTPUT -----------------------------------------------------------------------------

; PRINT_STRING: Imprime una cadena terminada en NULL
; Entrada: R2 = puntero a la cadena
; Salida: imprime por SVIO 0x100
PRINT_STRING:
    PUSH8 R01
    PUSH8 R02

PRINT_NEXT_CHAR:
    LOADR1 R01, R02 ; R01 = mem[R02]
    CMPV R01, 0
    JEQ FIN_PRINT_STRING
    SVIO R01, 0x100
    SHOWIO 0x100
    ADDV8 R02, 1
    JMP PRINT_NEXT_CHAR

FIN_PRINT_STRING:
    POP8 R02
    POP8 R01
    RET

; PRINT_INT: Imprime un entero decimal positivo
; Entrada: R1 = entero sin signo
; Salida: imprime dígitos por SVIO 0x100
PRINT_INT:
    PUSH8 R01             ; Guardar argumento
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04

    ; Caso especial: si R01 == 0, imprimir '0' directamente
    CMPV R01, 0
    JNE PRINT_INT_DIGITS
    MOVV1 R03, 48        ; ASCII '0'
    SVIO R03, 0x100
    SHOWIO 0x100
    JMP PRINT_INT_END

PRINT_INT_DIGITS:
    MOVV1 R02, 0
    PUSH1 R02            ; Terminador en pila

NEXT_DIGIT:
    MOVV8 R04, 10        ; Divisor = 10
    MOV8 R03, R01         ; R03 = copia de R01
    MOD8 R03, R04         ; R03 = R01 % 10
    ADDV8 R03, 48        ; Convertir a ASCII '0'..'9'
    PUSH1 R03            ; Guardar en pila
    DIV8 R01, R04         ; R01 = R01 / 10
    CMPV R01, 0
    JNE NEXT_DIGIT      ; Repetir si R01 != 0

FIN_PRINT_INT:
    POP1 R03             ; Obtener carácter
    CMPV R03, 0          ; ¿Era terminador?
    JEQ PRINT_INT_END   ; Si es terminador, terminar
    SVIO R03, 0x100      ; Imprimir
    SHOWIO 0x100
    JMP FIN_PRINT_INT   ; Repetir

PRINT_INT_END:
    POP8 R04
    POP8 R03
    POP8 R02
    POP8 R01              ; Restaurar argumento
    RET

; ============================================================================
; FUNCIONES DE SOPORTE PARA imprimir()
; ============================================================================

; __print_int8: Imprime un entero de 64 bits (con signo)
; Entrada: valor en el tope de la pila
; Salida: imprime el valor y un espacio
__print_int8:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP

    ; CRÍTICO: Cargar argumento ANTES de guardar registros
    ; Stack: [argumento] [ret_addr 8B] [BP_old 8B] <- BP apunta después de todo
    ; Argumento está 24 bytes debajo de BP (8B por BP_old + 8B por ret_addr + 8B del argumento mismo)
    MOV8 R03, R14       ; R03 = BP
    SUBV8 R03, 24       ; R03 = BP - 24 para llegar al inicio del argumento
    LOADR8 R01, R03     ; R01 = argumento

    PUSH8 R01           ; Ahora guardar registros
    PUSH8 R02
    PUSH8 R03

    ; Verificar si es negativo
    CMPV R01, 0
    JGE __print_int8_positive

    ; Es negativo: imprimir '-' y convertir a positivo
    MOVV1 R02, 45       ; ASCII '-'
    SVIO R02, 0x100
    SHOWIO 0x100
    ; Negar: R01 = 0 - R01
    PUSH8 R04
    MOVV8 R04, 0
    SUB8 R04, R01
    MOV8 R01, R04
    POP8 R04

__print_int8_positive:
    CALL PRINT_INT      ; Imprimir el número

    ; Imprimir espacio
    MOVV1 R02, 32       ; ASCII ' '
    SVIO R02, 0x100
    SHOWIO 0x100

    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_string: Imprime una cadena (puntero)
; Entrada: puntero en el tope de la pila
; Salida: imprime la cadena y un espacio
__print_string:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP

    ; Cargar argumento ANTES de guardar registros
    ; Stack: [arg, ret_addr, old_BP] <- BP después de PUSH8 R14
    ; arg está en BP - 24
    MOV8 R03, R14       ; R03 = BP
    SUBV8 R03, 24       ; R03 = BP - 24
    LOADR8 R02, R03     ; R02 = puntero al string

    ; Guardar registros
    PUSH8 R02
    PUSH8 R03

    ; Llamar PRINT_STRING con R02 = puntero
    CALL PRINT_STRING

    ; Imprimir espacio
    MOVV1 R02, 32       ; ASCII ' '
    SVIO R02, 0x100
    SHOWIO 0x100

    ; Restaurar registros
    POP8 R03
    POP8 R02
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_char: Imprime un carácter
; Entrada: carácter en el tope de la pila
; Salida: imprime el carácter y un espacio
__print_char:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP

    ; CRÍTICO: Cargar carácter ANTES de guardar registros
    ; Argumento en BP-24
    MOV8 R02, R14       ; R02 = BP
    SUBV8 R02, 24       ; R02 = BP - 24
    LOADR8 R01, R02     ; R01 = carácter

    PUSH8 R01           ; Ahora guardar registros
    PUSH8 R02    SVIO R01, 0x100     ; Imprimir
    SHOWIO 0x100        ; Imprimir espacio

    MOVV1 R01, 32       ; ASCII ' '
    SVIO R01, 0x100
    SHOWIO 0x100

    POP8 R02
    POP8 R01
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_float: Imprime un valor flotante con 2 decimales
; Argumento en stack: flotante de 32 bits (4 bytes)
__print_float:
    PUSH8 R14
    MOV8 R14, R15

    ; Cargar el flotante desde el stack (argumento en BP-20: 8B ret + 8B BP + 4B arg)
    MOV8 R03, R14
    SUBV8 R03, 20
    LOADR4 R01, R03     ; R01 = valor flotante (4 bytes)    PUSH8 R01
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04
    PUSH8 R05

    ; Convertir flotante a entero (parte entera)
    CVTF2I4 R02, R01    ; R02 = int(R01)    ; Guardar signo
    MOVV4 R05, 0
    CMP4 R02, R05
    JGE __print_float_positive_int

    ; Si es negativo, imprimir '-' y convertir a positivo
    MOVV1 R04, 45       ; ASCII '-'
    SVIO R04, 0x100
    SHOWIO 0x100

    ; Negar el entero
    MOVV4 R04, 0
    SUB4 R04, R02
    MOV4 R02, R04

    ; También negar el flotante original para decimales
    MOVV4 R04, 0
    CVTI2F4 R04, R04    ; Convertir 0 a flotante
    FSUB4 R04, R01      ; R04 = 0.0 - R01
    MOV4 R01, R04

__print_float_positive_int:
    ; Guardar el flotante original en R06 antes de imprimir el entero
    PUSH8 R06
    MOV4 R06, R01       ; R06 = flotante original

    ; Imprimir parte entera
    MOV8 R01, R02
    CALL PRINT_INT

    ; Imprimir punto decimal
    MOVV1 R01, 46       ; ASCII '.'
    SVIO R01, 0x100
    SHOWIO 0x100

    ; Restaurar el flotante original desde R06
    MOV4 R01, R06
    POP8 R06

    ; Obtener parte decimal: (float - int(float)) * 100
    CVTF2I4 R02, R01    ; R02 = int(R01)
    CVTI2F4 R03, R02    ; R03 = float(int(R01))
    FSUB4 R01, R03      ; R01 = R01 - R03 (parte decimal)

    ; Multiplicar por 100
    MOVV4 R02, 100
    CVTI2F4 R02, R02    ; Convertir 100 a flotante
    FMUL4 R01, R02      ; R01 = parte_decimal * 100

    ; Convertir a entero
    CVTF2I4 R01, R01    ; R01 = int(parte_decimal * 100)    ; Asegurar que sea positivo
    MOVV4 R03, 0
    CMP4 R01, R03
    JGE __print_float_decimal_positive
    MOVV4 R03, 0
    SUB4 R03, R01
    MOV4 R01, R03

__print_float_decimal_positive:
    ; Imprimir primer dígito
    MOV4 R02, R01
    MOVV4 R03, 10
    DIV4 R02, R03
    ADDV4 R02, 48       ; Convertir a ASCII
    SVIO R02, 0x100
    SHOWIO 0x100

    ; Imprimir segundo dígito
    MOVV4 R03, 10
    MOD4 R01, R03
    ADDV4 R01, 48       ; Convertir a ASCII
    SVIO R01, 0x100
    SHOWIO 0x100

    ; Imprimir espacio
    MOVV1 R01, 32
    SVIO R01, 0x100
    SHOWIO 0x100

    POP8 R04
    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14
    POP8 R14
    RET

; __print_newline: Imprime un salto de línea
; Sin argumentos
__print_newline:
    PUSH8 R01
    MOVV1 R01, 10       ; ASCII '\n'
    SVIO R01, 0x100
    SHOWIO 0x100
    POP8 R01
    RET
; === FIN BIBLIOTECA ===

; Saltar bibliotecas e iniciar programa
JMP __START_PROGRAM

; === BIBLIOTECA memory.asm ===
; ============================================================================
; BIBLIOTECA MEMORY - Gestión de memoria dinámica
; ============================================================================
; Implementa malloc y free para asignación dinámica de memoria
;
; Estrategia simple: Heap estático con lista enlazada de bloques libres
;
; Estructura de bloque:
;   [8 bytes: tamaño] [8 bytes: siguiente bloque libre] [datos...]
;
; Memoria layout (128KB):
;   0x0000-0xFFFF: Código ejecutable y datos constantes (64KB)
;   0x10000-0x17FFF: Globales y heap (32KB)
;   0x18000-0x1BFFF: Strings y datos (16KB)
;   0x1C000-0x1FFFF: Stack (16KB)
; ============================================================================

; Constantes (usadas como valores inmediatos en el código)
; HEAP_START:     0x10000     ; Inicio del heap (64KB desde inicio)
; HEAP_END:       0x17FFF     ; Fin del heap (96KB desde inicio)
; HEAP_SIZE:      0x8000      ; 32KB de heap
; BLOCK_HEADER:   16          ; Tamaño del header (8B size + 8B next)
; FREE_LIST_PTR:  0x10000     ; Variable global: puntero al primer bloque libre

; ============================================================================
; __init_heap: Inicializa el heap con un gran bloque libre
; Debe llamarse al inicio del programa (desde __START_PROGRAM)
; No recibe parámetros, no retorna valor
; ============================================================================
__init_heap:
    PUSH8 R01
    PUSH8 R02
    PUSH8 R03

    ; Crear primer bloque libre: todo el heap
    MOVV8 R01, 0x10000          ; R01 = dirección del primer bloque (HEAP_START)

    ; Escribir tamaño del bloque (HEAP_SIZE - header)
    MOVV8 R02, 0x8000           ; HEAP_SIZE
    SUBV8 R02, 16               ; Restar BLOCK_HEADER
    STORER8 R02, R01            ; mem[HEAP_START] = tamaño

    ; Escribir puntero al siguiente bloque (NULL = 0)
    ADDV8 R01, 8                ; R01 = HEAP_START + 8
    MOVV8 R02, 0
    STORER8 R02, R01            ; mem[HEAP_START+8] = NULL

    ; Guardar puntero inicial en FREE_LIST_PTR
    MOVV8 R01, 0x10000          ; HEAP_START
    MOVV8 R03, 0x10000          ; FREE_LIST_PTR
    STORER8 R01, R03            ; FREE_LIST_PTR = HEAP_START

    POP8 R03
    POP8 R02
    POP8 R01
    RET

; ============================================================================
; __malloc: Asigna un bloque de memoria del heap
; Entrada:
;   Stack: [tamaño solicitado (8 bytes)]
; Salida:
;   R00 = puntero a memoria asignada (o 0 si falla)
;
; Usa estrategia "first fit": busca el primer bloque que sea suficientemente grande
; ============================================================================
__malloc:
    PUSH8 R14                   ; Guardar BP
    MOV8 R14, R15               ; BP = SP

    ; Cargar argumento (tamaño solicitado)
    MOV8 R03, R14
    SUBV8 R03, 24               ; R03 = BP - 24 (argumento)
    LOADR8 R01, R03             ; R01 = tamaño solicitado

    ; Guardar registros
    PUSH8 R01
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04
    PUSH8 R05
    PUSH8 R06

    ; R01 = tamaño solicitado
    ; R02 = puntero actual (iterador)
    ; R03 = puntero previo
    ; R04 = tamaño del bloque actual
    ; R05 = siguiente bloque
    ; R06 = auxiliar

    ; Cargar FREE_LIST_PTR
    MOVV8 R06, 0x10000          ; FREE_LIST_PTR
    LOADR8 R02, R06             ; R02 = primer bloque libre
    MOVV8 R03, 0                ; R03 = previo (NULL al inicio)

__malloc_loop:
    ; Verificar si llegamos al final de la lista
    CMPV R02, 0
    JEQ __malloc_fail           ; Si R02 == NULL, no hay bloques

    ; Leer tamaño del bloque actual
    LOADR8 R04, R02             ; R04 = tamaño del bloque

    ; Comparar con tamaño solicitado
    CMP8 R04, R01
    JLT __malloc_next           ; Si tamaño < solicitado, probar siguiente

    ; Bloque encontrado! Asignarlo
    ; R02 apunta al bloque que vamos a asignar

    ; Leer puntero al siguiente bloque
    MOV8 R06, R02
    ADDV8 R06, 8                ; R06 = R02 + 8
    LOADR8 R05, R06             ; R05 = siguiente bloque

    ; Actualizar lista enlazada
    CMPV R03, 0
    JEQ __malloc_update_head    ; Si previo == NULL, actualizar head

    ; previo->next = actual->next
    MOV8 R06, R03
    ADDV8 R06, 8                ; R06 = previo + 8
    STORER8 R05, R06            ; previo->next = siguiente
    JMP __malloc_return_block

__malloc_update_head:
    ; FREE_LIST_PTR = actual->next
    MOVV8 R06, 0x10000          ; FREE_LIST_PTR
    STORER8 R05, R06            ; FREE_LIST_PTR = siguiente

__malloc_return_block:
    ; Retornar puntero al área de datos (después del header)
    MOV8 R00, R02
    ADDV8 R00, 16               ; R00 = bloque + 16 (saltar header, BLOCK_HEADER)
    JMP __malloc_end

__malloc_next:
    ; Avanzar al siguiente bloque
    MOV8 R03, R02               ; previo = actual
    MOV8 R06, R02
    ADDV8 R06, 8                ; R06 = actual + 8
    LOADR8 R02, R06             ; actual = actual->next
    JMP __malloc_loop

__malloc_fail:
    ; No se encontró bloque, retornar NULL
    MOVV8 R00, 0

__malloc_end:
    ; Restaurar registros
    POP8 R06
    POP8 R05
    POP8 R04
    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14               ; SP = BP
    POP8 R14                    ; Restaurar BP
    RET

; ============================================================================
; __free: Libera un bloque de memoria previamente asignado
; Entrada:
;   Stack: [puntero a memoria (8 bytes)]
; Salida:
;   Ninguna
;
; Simplemente devuelve el bloque a la lista de bloques libres (sin coalescing)
; ============================================================================
__free:
    PUSH8 R14                   ; Guardar BP
    MOV8 R14, R15               ; BP = SP

    ; Cargar argumento (puntero)
    MOV8 R03, R14
    SUBV8 R03, 24               ; R03 = BP - 24
    LOADR8 R01, R03             ; R01 = puntero a liberar

    ; Guardar registros
    PUSH8 R01
    PUSH8 R02
    PUSH8 R03

    ; Verificar que el puntero no sea NULL
    CMPV R01, 0
    JEQ __free_end              ; Si es NULL, no hacer nada

    ; Retroceder al inicio del bloque (restar BLOCK_HEADER)
    SUBV8 R01, 16               ; R01 = inicio del bloque (BLOCK_HEADER)

    ; Insertar al inicio de FREE_LIST
    ; bloque->next = FREE_LIST_PTR
    MOVV8 R03, 0x10000          ; FREE_LIST_PTR
    LOADR8 R02, R03             ; R02 = FREE_LIST_PTR
    MOV8 R03, R01
    ADDV8 R03, 8                ; R03 = bloque + 8
    STORER8 R02, R03            ; bloque->next = FREE_LIST_PTR

    ; FREE_LIST_PTR = bloque
    MOVV8 R03, 0x10000          ; FREE_LIST_PTR
    STORER8 R01, R03            ; FREE_LIST_PTR = bloque

__free_end:
    ; Restaurar registros
    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14               ; SP = BP
    POP8 R14                    ; Restaurar BP
    RET
; === FIN BIBLIOTECA ===

; === SECCIÓN DE DATOS GLOBALES ===


; === CÓDIGO DE INICIALIZACIÓN ===

__START_PROGRAM:
; Inicializar Stack Pointer en una ubicación segura
; Inicializar Stack Pointer (R15) y Frame Pointer (R14)
; Nueva ubicación de stack: colocar al inicio de la zona de stack (0x1C000)
MOVV8 R15, 0x1C000        ; SP en 0x1C000 (inicio de la región de stack)
MOV8 R14, R15            ; BP = SP (frame inicial)

; Strings recolectados:
;   __STR0: Extremadamente caliente - Peligro de muerte 
;   __STR1: Muy caliente - Peligroso 
;   __STR2: Caliente - Extremo cuidado 
;   __STR3: Caluroso - Usar protecci Ã³n
;   __STR4: CÃ¡lido - Agradable 
;   __STR5: Templado - Confortable 
;   __STR6: Fresco - Ligeramente fr Ã­o
;   __STR7: FrÃ­o - Usar abrigo 
;   __STR8: Muy fr Ã­o - Ropa t Ã©rmica
;   __STR9: Bajo cero - Peligro de congelaci Ã³n
;   __STR10: === Clasificaci Ã³n de Temperatura ===
;   __STR11: === Anos Bisiestos ===
;   __STR12: 2024 es bisiesto 
;   __STR13: 2023 no es bisiesto 
;   __STR14: === D Ã­as en Mes ===
; Inicializar string literals en memoria (área 0x18000+)
; __STR0 @ 0x18000
  MOVV1 R01, 69  ; byte 0x45
  STORE1 R01, 98304  ; Escribir en 0x18000
  MOVV1 R01, 120  ; byte 0x78
  STORE1 R01, 98305  ; Escribir en 0x18001
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98306  ; Escribir en 0x18002
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98307  ; Escribir en 0x18003
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98308  ; Escribir en 0x18004
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98309  ; Escribir en 0x18005
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98310  ; Escribir en 0x18006
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98311  ; Escribir en 0x18007
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98312  ; Escribir en 0x18008
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98313  ; Escribir en 0x18009
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98314  ; Escribir en 0x1800A
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98315  ; Escribir en 0x1800B
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98316  ; Escribir en 0x1800C
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98317  ; Escribir en 0x1800D
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98318  ; Escribir en 0x1800E
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98319  ; Escribir en 0x1800F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98320  ; Escribir en 0x18010
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98321  ; Escribir en 0x18011
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98322  ; Escribir en 0x18012
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98323  ; Escribir en 0x18013
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98324  ; Escribir en 0x18014
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98325  ; Escribir en 0x18015
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98326  ; Escribir en 0x18016
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98327  ; Escribir en 0x18017
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98328  ; Escribir en 0x18018
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98329  ; Escribir en 0x18019
  MOVV1 R01, 80  ; byte 0x50
  STORE1 R01, 98330  ; Escribir en 0x1801A
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98331  ; Escribir en 0x1801B
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98332  ; Escribir en 0x1801C
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98333  ; Escribir en 0x1801D
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98334  ; Escribir en 0x1801E
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98335  ; Escribir en 0x1801F
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98336  ; Escribir en 0x18020
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98337  ; Escribir en 0x18021
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98338  ; Escribir en 0x18022
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98339  ; Escribir en 0x18023
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98340  ; Escribir en 0x18024
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98341  ; Escribir en 0x18025
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98342  ; Escribir en 0x18026
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98343  ; Escribir en 0x18027
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98344  ; Escribir en 0x18028
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98345  ; Escribir en 0x18029
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98346  ; Escribir en 0x1802A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98347  ; Escribir en 0x1802B
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98348  ; Escribir en 0x1802C
; __STR1 @ 0x1802D
  MOVV1 R01, 77  ; byte 0x4D
  STORE1 R01, 98349  ; Escribir en 0x1802D
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98350  ; Escribir en 0x1802E
  MOVV1 R01, 121  ; byte 0x79
  STORE1 R01, 98351  ; Escribir en 0x1802F
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98352  ; Escribir en 0x18030
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98353  ; Escribir en 0x18031
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98354  ; Escribir en 0x18032
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98355  ; Escribir en 0x18033
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98356  ; Escribir en 0x18034
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98357  ; Escribir en 0x18035
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98358  ; Escribir en 0x18036
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98359  ; Escribir en 0x18037
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98360  ; Escribir en 0x18038
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98361  ; Escribir en 0x18039
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98362  ; Escribir en 0x1803A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98363  ; Escribir en 0x1803B
  MOVV1 R01, 80  ; byte 0x50
  STORE1 R01, 98364  ; Escribir en 0x1803C
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98365  ; Escribir en 0x1803D
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98366  ; Escribir en 0x1803E
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98367  ; Escribir en 0x1803F
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98368  ; Escribir en 0x18040
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98369  ; Escribir en 0x18041
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98370  ; Escribir en 0x18042
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98371  ; Escribir en 0x18043
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98372  ; Escribir en 0x18044
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98373  ; Escribir en 0x18045
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98374  ; Escribir en 0x18046
; __STR2 @ 0x18047
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98375  ; Escribir en 0x18047
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98376  ; Escribir en 0x18048
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98377  ; Escribir en 0x18049
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98378  ; Escribir en 0x1804A
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98379  ; Escribir en 0x1804B
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98380  ; Escribir en 0x1804C
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98381  ; Escribir en 0x1804D
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98382  ; Escribir en 0x1804E
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98383  ; Escribir en 0x1804F
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98384  ; Escribir en 0x18050
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98385  ; Escribir en 0x18051
  MOVV1 R01, 69  ; byte 0x45
  STORE1 R01, 98386  ; Escribir en 0x18052
  MOVV1 R01, 120  ; byte 0x78
  STORE1 R01, 98387  ; Escribir en 0x18053
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98388  ; Escribir en 0x18054
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98389  ; Escribir en 0x18055
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98390  ; Escribir en 0x18056
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98391  ; Escribir en 0x18057
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98392  ; Escribir en 0x18058
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98393  ; Escribir en 0x18059
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98394  ; Escribir en 0x1805A
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98395  ; Escribir en 0x1805B
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98396  ; Escribir en 0x1805C
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98397  ; Escribir en 0x1805D
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98398  ; Escribir en 0x1805E
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98399  ; Escribir en 0x1805F
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98400  ; Escribir en 0x18060
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98401  ; Escribir en 0x18061
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98402  ; Escribir en 0x18062
; __STR3 @ 0x18063
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98403  ; Escribir en 0x18063
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98404  ; Escribir en 0x18064
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98405  ; Escribir en 0x18065
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98406  ; Escribir en 0x18066
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98407  ; Escribir en 0x18067
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98408  ; Escribir en 0x18068
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98409  ; Escribir en 0x18069
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98410  ; Escribir en 0x1806A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98411  ; Escribir en 0x1806B
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98412  ; Escribir en 0x1806C
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98413  ; Escribir en 0x1806D
  MOVV1 R01, 85  ; byte 0x55
  STORE1 R01, 98414  ; Escribir en 0x1806E
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98415  ; Escribir en 0x1806F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98416  ; Escribir en 0x18070
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98417  ; Escribir en 0x18071
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98418  ; Escribir en 0x18072
  MOVV1 R01, 112  ; byte 0x70
  STORE1 R01, 98419  ; Escribir en 0x18073
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98420  ; Escribir en 0x18074
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98421  ; Escribir en 0x18075
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98422  ; Escribir en 0x18076
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98423  ; Escribir en 0x18077
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98424  ; Escribir en 0x18078
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98425  ; Escribir en 0x18079
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98426  ; Escribir en 0x1807A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98427  ; Escribir en 0x1807B
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98428  ; Escribir en 0x1807C
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98429  ; Escribir en 0x1807D
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98430  ; Escribir en 0x1807E
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98431  ; Escribir en 0x1807F
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98432  ; Escribir en 0x18080
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98433  ; Escribir en 0x18081
; __STR4 @ 0x18082
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98434  ; Escribir en 0x18082
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98435  ; Escribir en 0x18083
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98436  ; Escribir en 0x18084
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98437  ; Escribir en 0x18085
  MOVV1 R01, 161  ; byte 0xA1
  STORE1 R01, 98438  ; Escribir en 0x18086
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98439  ; Escribir en 0x18087
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98440  ; Escribir en 0x18088
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98441  ; Escribir en 0x18089
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98442  ; Escribir en 0x1808A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98443  ; Escribir en 0x1808B
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98444  ; Escribir en 0x1808C
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98445  ; Escribir en 0x1808D
  MOVV1 R01, 65  ; byte 0x41
  STORE1 R01, 98446  ; Escribir en 0x1808E
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98447  ; Escribir en 0x1808F
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98448  ; Escribir en 0x18090
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98449  ; Escribir en 0x18091
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98450  ; Escribir en 0x18092
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98451  ; Escribir en 0x18093
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98452  ; Escribir en 0x18094
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98453  ; Escribir en 0x18095
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98454  ; Escribir en 0x18096
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98455  ; Escribir en 0x18097
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98456  ; Escribir en 0x18098
; __STR5 @ 0x18099
  MOVV1 R01, 84  ; byte 0x54
  STORE1 R01, 98457  ; Escribir en 0x18099
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98458  ; Escribir en 0x1809A
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98459  ; Escribir en 0x1809B
  MOVV1 R01, 112  ; byte 0x70
  STORE1 R01, 98460  ; Escribir en 0x1809C
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98461  ; Escribir en 0x1809D
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98462  ; Escribir en 0x1809E
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98463  ; Escribir en 0x1809F
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98464  ; Escribir en 0x180A0
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98465  ; Escribir en 0x180A1
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98466  ; Escribir en 0x180A2
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98467  ; Escribir en 0x180A3
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98468  ; Escribir en 0x180A4
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98469  ; Escribir en 0x180A5
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98470  ; Escribir en 0x180A6
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98471  ; Escribir en 0x180A7
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98472  ; Escribir en 0x180A8
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98473  ; Escribir en 0x180A9
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98474  ; Escribir en 0x180AA
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98475  ; Escribir en 0x180AB
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98476  ; Escribir en 0x180AC
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98477  ; Escribir en 0x180AD
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98478  ; Escribir en 0x180AE
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98479  ; Escribir en 0x180AF
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98480  ; Escribir en 0x180B0
; __STR6 @ 0x180B1
  MOVV1 R01, 70  ; byte 0x46
  STORE1 R01, 98481  ; Escribir en 0x180B1
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98482  ; Escribir en 0x180B2
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98483  ; Escribir en 0x180B3
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98484  ; Escribir en 0x180B4
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98485  ; Escribir en 0x180B5
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98486  ; Escribir en 0x180B6
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98487  ; Escribir en 0x180B7
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98488  ; Escribir en 0x180B8
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98489  ; Escribir en 0x180B9
  MOVV1 R01, 76  ; byte 0x4C
  STORE1 R01, 98490  ; Escribir en 0x180BA
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98491  ; Escribir en 0x180BB
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98492  ; Escribir en 0x180BC
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98493  ; Escribir en 0x180BD
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98494  ; Escribir en 0x180BE
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98495  ; Escribir en 0x180BF
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98496  ; Escribir en 0x180C0
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98497  ; Escribir en 0x180C1
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98498  ; Escribir en 0x180C2
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98499  ; Escribir en 0x180C3
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98500  ; Escribir en 0x180C4
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98501  ; Escribir en 0x180C5
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98502  ; Escribir en 0x180C6
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98503  ; Escribir en 0x180C7
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98504  ; Escribir en 0x180C8
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98505  ; Escribir en 0x180C9
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98506  ; Escribir en 0x180CA
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98507  ; Escribir en 0x180CB
  MOVV1 R01, 173  ; byte 0xAD
  STORE1 R01, 98508  ; Escribir en 0x180CC
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98509  ; Escribir en 0x180CD
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98510  ; Escribir en 0x180CE
; __STR7 @ 0x180CF
  MOVV1 R01, 70  ; byte 0x46
  STORE1 R01, 98511  ; Escribir en 0x180CF
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98512  ; Escribir en 0x180D0
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98513  ; Escribir en 0x180D1
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98514  ; Escribir en 0x180D2
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98515  ; Escribir en 0x180D3
  MOVV1 R01, 173  ; byte 0xAD
  STORE1 R01, 98516  ; Escribir en 0x180D4
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98517  ; Escribir en 0x180D5
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98518  ; Escribir en 0x180D6
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98519  ; Escribir en 0x180D7
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98520  ; Escribir en 0x180D8
  MOVV1 R01, 85  ; byte 0x55
  STORE1 R01, 98521  ; Escribir en 0x180D9
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98522  ; Escribir en 0x180DA
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98523  ; Escribir en 0x180DB
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98524  ; Escribir en 0x180DC
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98525  ; Escribir en 0x180DD
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98526  ; Escribir en 0x180DE
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98527  ; Escribir en 0x180DF
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98528  ; Escribir en 0x180E0
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98529  ; Escribir en 0x180E1
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98530  ; Escribir en 0x180E2
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98531  ; Escribir en 0x180E3
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98532  ; Escribir en 0x180E4
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98533  ; Escribir en 0x180E5
; __STR8 @ 0x180E6
  MOVV1 R01, 77  ; byte 0x4D
  STORE1 R01, 98534  ; Escribir en 0x180E6
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98535  ; Escribir en 0x180E7
  MOVV1 R01, 121  ; byte 0x79
  STORE1 R01, 98536  ; Escribir en 0x180E8
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98537  ; Escribir en 0x180E9
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98538  ; Escribir en 0x180EA
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98539  ; Escribir en 0x180EB
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98540  ; Escribir en 0x180EC
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98541  ; Escribir en 0x180ED
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98542  ; Escribir en 0x180EE
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98543  ; Escribir en 0x180EF
  MOVV1 R01, 173  ; byte 0xAD
  STORE1 R01, 98544  ; Escribir en 0x180F0
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98545  ; Escribir en 0x180F1
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98546  ; Escribir en 0x180F2
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98547  ; Escribir en 0x180F3
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98548  ; Escribir en 0x180F4
  MOVV1 R01, 82  ; byte 0x52
  STORE1 R01, 98549  ; Escribir en 0x180F5
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98550  ; Escribir en 0x180F6
  MOVV1 R01, 112  ; byte 0x70
  STORE1 R01, 98551  ; Escribir en 0x180F7
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98552  ; Escribir en 0x180F8
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98553  ; Escribir en 0x180F9
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98554  ; Escribir en 0x180FA
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98555  ; Escribir en 0x180FB
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98556  ; Escribir en 0x180FC
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98557  ; Escribir en 0x180FD
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98558  ; Escribir en 0x180FE
  MOVV1 R01, 169  ; byte 0xA9
  STORE1 R01, 98559  ; Escribir en 0x180FF
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98560  ; Escribir en 0x18100
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98561  ; Escribir en 0x18101
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98562  ; Escribir en 0x18102
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98563  ; Escribir en 0x18103
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98564  ; Escribir en 0x18104
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98565  ; Escribir en 0x18105
; __STR9 @ 0x18106
  MOVV1 R01, 66  ; byte 0x42
  STORE1 R01, 98566  ; Escribir en 0x18106
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98567  ; Escribir en 0x18107
  MOVV1 R01, 106  ; byte 0x6A
  STORE1 R01, 98568  ; Escribir en 0x18108
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98569  ; Escribir en 0x18109
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98570  ; Escribir en 0x1810A
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98571  ; Escribir en 0x1810B
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98572  ; Escribir en 0x1810C
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98573  ; Escribir en 0x1810D
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98574  ; Escribir en 0x1810E
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98575  ; Escribir en 0x1810F
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98576  ; Escribir en 0x18110
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98577  ; Escribir en 0x18111
  MOVV1 R01, 80  ; byte 0x50
  STORE1 R01, 98578  ; Escribir en 0x18112
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98579  ; Escribir en 0x18113
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98580  ; Escribir en 0x18114
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98581  ; Escribir en 0x18115
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98582  ; Escribir en 0x18116
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98583  ; Escribir en 0x18117
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98584  ; Escribir en 0x18118
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98585  ; Escribir en 0x18119
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98586  ; Escribir en 0x1811A
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98587  ; Escribir en 0x1811B
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98588  ; Escribir en 0x1811C
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98589  ; Escribir en 0x1811D
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98590  ; Escribir en 0x1811E
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98591  ; Escribir en 0x1811F
  MOVV1 R01, 103  ; byte 0x67
  STORE1 R01, 98592  ; Escribir en 0x18120
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98593  ; Escribir en 0x18121
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98594  ; Escribir en 0x18122
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98595  ; Escribir en 0x18123
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98596  ; Escribir en 0x18124
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98597  ; Escribir en 0x18125
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98598  ; Escribir en 0x18126
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98599  ; Escribir en 0x18127
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98600  ; Escribir en 0x18128
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98601  ; Escribir en 0x18129
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98602  ; Escribir en 0x1812A
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98603  ; Escribir en 0x1812B
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98604  ; Escribir en 0x1812C
; __STR10 @ 0x1812D
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98605  ; Escribir en 0x1812D
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98606  ; Escribir en 0x1812E
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98607  ; Escribir en 0x1812F
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98608  ; Escribir en 0x18130
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98609  ; Escribir en 0x18131
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98610  ; Escribir en 0x18132
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98611  ; Escribir en 0x18133
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98612  ; Escribir en 0x18134
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98613  ; Escribir en 0x18135
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98614  ; Escribir en 0x18136
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98615  ; Escribir en 0x18137
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98616  ; Escribir en 0x18138
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98617  ; Escribir en 0x18139
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98618  ; Escribir en 0x1813A
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98619  ; Escribir en 0x1813B
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98620  ; Escribir en 0x1813C
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98621  ; Escribir en 0x1813D
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98622  ; Escribir en 0x1813E
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98623  ; Escribir en 0x1813F
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98624  ; Escribir en 0x18140
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98625  ; Escribir en 0x18141
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98626  ; Escribir en 0x18142
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98627  ; Escribir en 0x18143
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98628  ; Escribir en 0x18144
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98629  ; Escribir en 0x18145
  MOVV1 R01, 84  ; byte 0x54
  STORE1 R01, 98630  ; Escribir en 0x18146
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98631  ; Escribir en 0x18147
  MOVV1 R01, 109  ; byte 0x6D
  STORE1 R01, 98632  ; Escribir en 0x18148
  MOVV1 R01, 112  ; byte 0x70
  STORE1 R01, 98633  ; Escribir en 0x18149
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98634  ; Escribir en 0x1814A
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98635  ; Escribir en 0x1814B
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98636  ; Escribir en 0x1814C
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98637  ; Escribir en 0x1814D
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98638  ; Escribir en 0x1814E
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98639  ; Escribir en 0x1814F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98640  ; Escribir en 0x18150
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98641  ; Escribir en 0x18151
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98642  ; Escribir en 0x18152
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98643  ; Escribir en 0x18153
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98644  ; Escribir en 0x18154
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98645  ; Escribir en 0x18155
; __STR11 @ 0x18156
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98646  ; Escribir en 0x18156
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98647  ; Escribir en 0x18157
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98648  ; Escribir en 0x18158
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98649  ; Escribir en 0x18159
  MOVV1 R01, 65  ; byte 0x41
  STORE1 R01, 98650  ; Escribir en 0x1815A
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98651  ; Escribir en 0x1815B
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98652  ; Escribir en 0x1815C
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98653  ; Escribir en 0x1815D
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98654  ; Escribir en 0x1815E
  MOVV1 R01, 66  ; byte 0x42
  STORE1 R01, 98655  ; Escribir en 0x1815F
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98656  ; Escribir en 0x18160
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98657  ; Escribir en 0x18161
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98658  ; Escribir en 0x18162
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98659  ; Escribir en 0x18163
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98660  ; Escribir en 0x18164
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98661  ; Escribir en 0x18165
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98662  ; Escribir en 0x18166
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98663  ; Escribir en 0x18167
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98664  ; Escribir en 0x18168
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98665  ; Escribir en 0x18169
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98666  ; Escribir en 0x1816A
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98667  ; Escribir en 0x1816B
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98668  ; Escribir en 0x1816C
; __STR12 @ 0x1816D
  MOVV1 R01, 50  ; byte 0x32
  STORE1 R01, 98669  ; Escribir en 0x1816D
  MOVV1 R01, 48  ; byte 0x30
  STORE1 R01, 98670  ; Escribir en 0x1816E
  MOVV1 R01, 50  ; byte 0x32
  STORE1 R01, 98671  ; Escribir en 0x1816F
  MOVV1 R01, 52  ; byte 0x34
  STORE1 R01, 98672  ; Escribir en 0x18170
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98673  ; Escribir en 0x18171
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98674  ; Escribir en 0x18172
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98675  ; Escribir en 0x18173
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98676  ; Escribir en 0x18174
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98677  ; Escribir en 0x18175
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98678  ; Escribir en 0x18176
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98679  ; Escribir en 0x18177
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98680  ; Escribir en 0x18178
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98681  ; Escribir en 0x18179
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98682  ; Escribir en 0x1817A
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98683  ; Escribir en 0x1817B
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98684  ; Escribir en 0x1817C
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98685  ; Escribir en 0x1817D
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98686  ; Escribir en 0x1817E
; __STR13 @ 0x1817F
  MOVV1 R01, 50  ; byte 0x32
  STORE1 R01, 98687  ; Escribir en 0x1817F
  MOVV1 R01, 48  ; byte 0x30
  STORE1 R01, 98688  ; Escribir en 0x18180
  MOVV1 R01, 50  ; byte 0x32
  STORE1 R01, 98689  ; Escribir en 0x18181
  MOVV1 R01, 51  ; byte 0x33
  STORE1 R01, 98690  ; Escribir en 0x18182
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98691  ; Escribir en 0x18183
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98692  ; Escribir en 0x18184
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98693  ; Escribir en 0x18185
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98694  ; Escribir en 0x18186
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98695  ; Escribir en 0x18187
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98696  ; Escribir en 0x18188
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98697  ; Escribir en 0x18189
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98698  ; Escribir en 0x1818A
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98699  ; Escribir en 0x1818B
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98700  ; Escribir en 0x1818C
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98701  ; Escribir en 0x1818D
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98702  ; Escribir en 0x1818E
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98703  ; Escribir en 0x1818F
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98704  ; Escribir en 0x18190
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98705  ; Escribir en 0x18191
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98706  ; Escribir en 0x18192
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98707  ; Escribir en 0x18193
; __STR14 @ 0x18194
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98708  ; Escribir en 0x18194
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98709  ; Escribir en 0x18195
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98710  ; Escribir en 0x18196
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98711  ; Escribir en 0x18197
  MOVV1 R01, 68  ; byte 0x44
  STORE1 R01, 98712  ; Escribir en 0x18198
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98713  ; Escribir en 0x18199
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98714  ; Escribir en 0x1819A
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98715  ; Escribir en 0x1819B
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98716  ; Escribir en 0x1819C
  MOVV1 R01, 173  ; byte 0xAD
  STORE1 R01, 98717  ; Escribir en 0x1819D
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98718  ; Escribir en 0x1819E
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98719  ; Escribir en 0x1819F
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98720  ; Escribir en 0x181A0
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98721  ; Escribir en 0x181A1
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98722  ; Escribir en 0x181A2
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98723  ; Escribir en 0x181A3
  MOVV1 R01, 77  ; byte 0x4D
  STORE1 R01, 98724  ; Escribir en 0x181A4
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98725  ; Escribir en 0x181A5
  MOVV1 R01, 115  ; byte 0x73
  STORE1 R01, 98726  ; Escribir en 0x181A6
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98727  ; Escribir en 0x181A7
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98728  ; Escribir en 0x181A8
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98729  ; Escribir en 0x181A9
  MOVV1 R01, 61  ; byte 0x3D
  STORE1 R01, 98730  ; Escribir en 0x181AA
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98731  ; Escribir en 0x181AB

; Llamar a la función principal
CALL principal
JMP END_PROGRAM

; === FUNCIONES ===

clasificar_temperatura:  ; Función: clasificar_temperatura
  ; Prólogo de clasificar_temperatura
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ; Sin variables locales

  ; Cuerpo de clasificar_temperatura
  ; imprimir()
  MOVV8 R01, -20  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  LOADR4 R00, R01  ; Cargar temp
  CMPV R00, 2147483648
  JLT SSKIP0
  SUBV8 R00, 4294967296
SSKIP0:
  PUSH8 R00
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R03, -20  ; Offset desde BP
  ADD8 R03, R14  ; Dirección = BP + offset
  LOADR4 R02, R03  ; Cargar temp
  CMPV R02, 2147483648
  JLT SSKIP2
  SUBV8 R02, 4294967296
SSKIP2:
  MOVV8 R04, 45
  CMP R02, R04
  MOVV1 R05, 0  ; Asumir falso
  JGE CMP_TRUE3
  JMP CMP_END4
CMP_TRUE3:
  MOVV1 R05, 1  ; Verdadero
CMP_END4:
  CMPV R05, 0
  JEQ ELIF5
  ; imprimir()
  MOVV8 R06, 0x18000  ; __STR0
  PUSH8 R06
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF5:
  MOVV8 R08, -20  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  LOADR4 R07, R08  ; Cargar temp
  CMPV R07, 2147483648
  JLT SSKIP6
  SUBV8 R07, 4294967296
SSKIP6:
  MOVV8 R09, 40
  CMP R07, R09
  MOVV1 R10, 0  ; Asumir falso
  JGE CMP_TRUE7
  JMP CMP_END8
CMP_TRUE7:
  MOVV1 R10, 1  ; Verdadero
CMP_END8:
  CMPV R10, 0
  JEQ ELIF9
  ; imprimir()
  MOVV8 R11, 0x1802D  ; __STR1
  PUSH8 R11
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF9:
  MOVV8 R13, -20  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  LOADR4 R12, R13  ; Cargar temp
  CMPV R12, 2147483648
  JLT SSKIP10
  SUBV8 R12, 4294967296
SSKIP10:
  MOVV8 R00, 35
  CMP R12, R00
  MOVV1 R01, 0  ; Asumir falso
  JGE CMP_TRUE11
  JMP CMP_END12
CMP_TRUE11:
  MOVV1 R01, 1  ; Verdadero
CMP_END12:
  CMPV R01, 0
  JEQ ELIF13
  ; imprimir()
  MOVV8 R02, 0x18047  ; __STR2
  PUSH8 R02
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF13:
  MOVV8 R04, -20  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar temp
  CMPV R03, 2147483648
  JLT SSKIP14
  SUBV8 R03, 4294967296
SSKIP14:
  MOVV8 R05, 30
  CMP R03, R05
  MOVV1 R06, 0  ; Asumir falso
  JGE CMP_TRUE15
  JMP CMP_END16
CMP_TRUE15:
  MOVV1 R06, 1  ; Verdadero
CMP_END16:
  CMPV R06, 0
  JEQ ELIF17
  ; imprimir()
  MOVV8 R07, 0x18063  ; __STR3
  PUSH8 R07
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF17:
  MOVV8 R09, -20  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR4 R08, R09  ; Cargar temp
  CMPV R08, 2147483648
  JLT SSKIP18
  SUBV8 R08, 4294967296
SSKIP18:
  MOVV8 R10, 25
  CMP R08, R10
  MOVV1 R11, 0  ; Asumir falso
  JGE CMP_TRUE19
  JMP CMP_END20
CMP_TRUE19:
  MOVV1 R11, 1  ; Verdadero
CMP_END20:
  CMPV R11, 0
  JEQ ELIF21
  ; imprimir()
  MOVV8 R12, 0x18082  ; __STR4
  PUSH8 R12
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF21:
  MOVV8 R00, -20  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  LOADR4 R13, R00  ; Cargar temp
  CMPV R13, 2147483648
  JLT SSKIP22
  SUBV8 R13, 4294967296
SSKIP22:
  MOVV8 R01, 20
  CMP R13, R01
  MOVV1 R02, 0  ; Asumir falso
  JGE CMP_TRUE23
  JMP CMP_END24
CMP_TRUE23:
  MOVV1 R02, 1  ; Verdadero
CMP_END24:
  CMPV R02, 0
  JEQ ELIF25
  ; imprimir()
  MOVV8 R03, 0x18099  ; __STR5
  PUSH8 R03
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF25:
  MOVV8 R05, -20  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar temp
  CMPV R04, 2147483648
  JLT SSKIP26
  SUBV8 R04, 4294967296
SSKIP26:
  MOVV8 R06, 15
  CMP R04, R06
  MOVV1 R07, 0  ; Asumir falso
  JGE CMP_TRUE27
  JMP CMP_END28
CMP_TRUE27:
  MOVV1 R07, 1  ; Verdadero
CMP_END28:
  CMPV R07, 0
  JEQ ELIF29
  ; imprimir()
  MOVV8 R08, 0x180B1  ; __STR6
  PUSH8 R08
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF29:
  MOVV8 R10, -20  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar temp
  CMPV R09, 2147483648
  JLT SSKIP30
  SUBV8 R09, 4294967296
SSKIP30:
  MOVV8 R11, 10
  CMP R09, R11
  MOVV1 R12, 0  ; Asumir falso
  JGE CMP_TRUE31
  JMP CMP_END32
CMP_TRUE31:
  MOVV1 R12, 1  ; Verdadero
CMP_END32:
  CMPV R12, 0
  JEQ ELIF33
  ; imprimir()
  MOVV8 R13, 0x180CF  ; __STR7
  PUSH8 R13
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELIF33:
  MOVV8 R01, -20  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  LOADR4 R00, R01  ; Cargar temp
  CMPV R00, 2147483648
  JLT SSKIP34
  SUBV8 R00, 4294967296
SSKIP34:
  MOVV8 R02, 0
  CMP R00, R02
  MOVV1 R03, 0  ; Asumir falso
  JGE CMP_TRUE35
  JMP CMP_END36
CMP_TRUE35:
  MOVV1 R03, 1  ; Verdadero
CMP_END36:
  CMPV R03, 0
  JEQ ELSE37
  ; imprimir()
  MOVV8 R04, 0x180E6  ; __STR8
  PUSH8 R04
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF1
ELSE37:
  ; imprimir()
  MOVV8 R05, 0x18106  ; __STR9
  PUSH8 R05
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
ENDIF1:

clasificar_temperatura_epilogue:
  ; Epílogo de clasificar_temperatura
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

.LOCAL_REL -20 4 temp ; FUNC=clasificar_temperatura
es_ano_bisiesto:  ; Función: es_ano_bisiesto
  ; Prólogo de es_ano_bisiesto
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 1  ; Reservar 1 bytes para locales

  ; Cuerpo de es_ano_bisiesto
  ; Variable local: bisiesto (offset: 0)
  MOVV1 R00, 0
  MOV1 R01, R00  ; Guardar valor de R00
  MOVV8 R02, 0
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER1 R01, R02  ; bisiesto = valor_inicial
  MOVV8 R04, -20  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar ano
  CMPV R03, 2147483648
  JLT SSKIP39
  SUBV8 R03, 4294967296
SSKIP39:
  MOVV8 R05, 400
  MOV1 R06, R03
  MOD1 R06, R05
  MOVV8 R07, 0
  CMP R06, R07
  MOVV1 R08, 0  ; Asumir falso
  JEQ CMP_TRUE40
  JMP CMP_END41
CMP_TRUE40:
  MOVV1 R08, 1  ; Verdadero
CMP_END41:
  CMPV R08, 0
  JEQ ELIF42
  MOVV1 R09, 1
  MOVV8 R10, 0  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  STORER1 R09, R10  ; bisiesto = valor
  JMP ENDIF38
ELIF42:
  MOVV8 R12, -20  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR4 R11, R12  ; Cargar ano
  CMPV R11, 2147483648
  JLT SSKIP43
  SUBV8 R11, 4294967296
SSKIP43:
  MOVV8 R13, 100
  MOV1 R00, R11
  MOD1 R00, R13
  MOVV8 R01, 0
  CMP R00, R01
  MOVV1 R02, 0  ; Asumir falso
  JEQ CMP_TRUE44
  JMP CMP_END45
CMP_TRUE44:
  MOVV1 R02, 1  ; Verdadero
CMP_END45:
  CMPV R02, 0
  JEQ ELIF46
  MOVV1 R03, 0
  MOVV8 R04, 0  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  STORER1 R03, R04  ; bisiesto = valor
  JMP ENDIF38
ELIF46:
  MOVV8 R06, -20  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  LOADR4 R05, R06  ; Cargar ano
  CMPV R05, 2147483648
  JLT SSKIP47
  SUBV8 R05, 4294967296
SSKIP47:
  MOVV8 R07, 4
  MOV1 R08, R05
  MOD1 R08, R07
  MOVV8 R09, 0
  CMP R08, R09
  MOVV1 R10, 0  ; Asumir falso
  JEQ CMP_TRUE48
  JMP CMP_END49
CMP_TRUE48:
  MOVV1 R10, 1  ; Verdadero
CMP_END49:
  CMPV R10, 0
  JEQ ELSE50
  MOVV1 R11, 1
  MOVV8 R12, 0  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  STORER1 R11, R12  ; bisiesto = valor
  JMP ENDIF38
ELSE50:
  MOVV1 R13, 0
  MOVV8 R00, 0  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  STORER1 R13, R00  ; bisiesto = valor
ENDIF38:
  MOVV8 R02, 0  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  LOADR1 R01, R02  ; Cargar bisiesto
  MOV1 R00, R01  ; Valor de retorno en R00
  JMP es_ano_bisiesto_epilogue

es_ano_bisiesto_epilogue:
  ; Epílogo de es_ano_bisiesto
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

.LOCAL_REL -20 4 ano ; FUNC=es_ano_bisiesto
.LOCAL_REL 0 1 bisiesto ; FUNC=es_ano_bisiesto
dias_en_mes:  ; Función: dias_en_mes
  ; Prólogo de dias_en_mes
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 4  ; Reservar 4 bytes para locales

  ; Cuerpo de dias_en_mes
  ; Variable local: dias (offset: 0)
  MOVV8 R00, 0
  MOV4 R01, R00  ; Guardar valor de R00
  MOVV8 R02, 0
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER4 R01, R02  ; dias = valor_inicial
  MOVV8 R04, -20  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar mes
  CMPV R03, 2147483648
  JLT SSKIP52
  SUBV8 R03, 4294967296
SSKIP52:
  MOVV8 R05, 1
  CMP R03, R05
  MOVV1 R06, 0  ; Asumir falso
  JEQ CMP_TRUE53
  JMP CMP_END54
CMP_TRUE53:
  MOVV1 R06, 1  ; Verdadero
CMP_END54:
  MOVV8 R08, -20  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  LOADR4 R07, R08  ; Cargar mes
  CMPV R07, 2147483648
  JLT SSKIP55
  SUBV8 R07, 4294967296
SSKIP55:
  MOVV8 R09, 3
  CMP R07, R09
  MOVV1 R10, 0  ; Asumir falso
  JEQ CMP_TRUE56
  JMP CMP_END57
CMP_TRUE56:
  MOVV1 R10, 1  ; Verdadero
CMP_END57:
  MOV8 R11, R06
  OR8 R11, R10  ; OR lógico
  MOVV8 R13, -20  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  LOADR4 R12, R13  ; Cargar mes
  CMPV R12, 2147483648
  JLT SSKIP58
  SUBV8 R12, 4294967296
SSKIP58:
  MOVV8 R00, 5
  CMP R12, R00
  MOVV1 R01, 0  ; Asumir falso
  JEQ CMP_TRUE59
  JMP CMP_END60
CMP_TRUE59:
  MOVV1 R01, 1  ; Verdadero
CMP_END60:
  MOV8 R02, R11
  OR8 R02, R01  ; OR lógico
  MOVV8 R04, -20  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar mes
  CMPV R03, 2147483648
  JLT SSKIP61
  SUBV8 R03, 4294967296
SSKIP61:
  MOVV8 R05, 7
  CMP R03, R05
  MOVV1 R06, 0  ; Asumir falso
  JEQ CMP_TRUE62
  JMP CMP_END63
CMP_TRUE62:
  MOVV1 R06, 1  ; Verdadero
CMP_END63:
  MOV8 R07, R02
  OR8 R07, R06  ; OR lógico
  MOVV8 R09, -20  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR4 R08, R09  ; Cargar mes
  CMPV R08, 2147483648
  JLT SSKIP64
  SUBV8 R08, 4294967296
SSKIP64:
  MOVV8 R10, 8
  CMP R08, R10
  MOVV1 R11, 0  ; Asumir falso
  JEQ CMP_TRUE65
  JMP CMP_END66
CMP_TRUE65:
  MOVV1 R11, 1  ; Verdadero
CMP_END66:
  MOV8 R12, R07
  OR8 R12, R11  ; OR lógico
  MOVV8 R00, -20  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  LOADR4 R13, R00  ; Cargar mes
  CMPV R13, 2147483648
  JLT SSKIP67
  SUBV8 R13, 4294967296
SSKIP67:
  MOVV8 R01, 10
  CMP R13, R01
  MOVV1 R02, 0  ; Asumir falso
  JEQ CMP_TRUE68
  JMP CMP_END69
CMP_TRUE68:
  MOVV1 R02, 1  ; Verdadero
CMP_END69:
  MOV8 R03, R12
  OR8 R03, R02  ; OR lógico
  MOVV8 R05, -20  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar mes
  CMPV R04, 2147483648
  JLT SSKIP70
  SUBV8 R04, 4294967296
SSKIP70:
  MOVV8 R06, 12
  CMP R04, R06
  MOVV1 R07, 0  ; Asumir falso
  JEQ CMP_TRUE71
  JMP CMP_END72
CMP_TRUE71:
  MOVV1 R07, 1  ; Verdadero
CMP_END72:
  MOV8 R08, R03
  OR8 R08, R07  ; OR lógico
  CMPV R08, 0
  JEQ ELIF73
  MOVV8 R09, 31
  MOVV8 R10, 0  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  STORER4 R09, R10  ; dias = valor
  JMP ENDIF51
ELIF73:
  MOVV8 R12, -20  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR4 R11, R12  ; Cargar mes
  CMPV R11, 2147483648
  JLT SSKIP74
  SUBV8 R11, 4294967296
SSKIP74:
  MOVV8 R13, 4
  CMP R11, R13
  MOVV1 R00, 0  ; Asumir falso
  JEQ CMP_TRUE75
  JMP CMP_END76
CMP_TRUE75:
  MOVV1 R00, 1  ; Verdadero
CMP_END76:
  MOVV8 R02, -20  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  LOADR4 R01, R02  ; Cargar mes
  CMPV R01, 2147483648
  JLT SSKIP77
  SUBV8 R01, 4294967296
SSKIP77:
  MOVV8 R03, 6
  CMP R01, R03
  MOVV1 R04, 0  ; Asumir falso
  JEQ CMP_TRUE78
  JMP CMP_END79
CMP_TRUE78:
  MOVV1 R04, 1  ; Verdadero
CMP_END79:
  MOV8 R05, R00
  OR8 R05, R04  ; OR lógico
  MOVV8 R07, -20  ; Offset desde BP
  ADD8 R07, R14  ; Dirección = BP + offset
  LOADR4 R06, R07  ; Cargar mes
  CMPV R06, 2147483648
  JLT SSKIP80
  SUBV8 R06, 4294967296
SSKIP80:
  MOVV8 R08, 9
  CMP R06, R08
  MOVV1 R09, 0  ; Asumir falso
  JEQ CMP_TRUE81
  JMP CMP_END82
CMP_TRUE81:
  MOVV1 R09, 1  ; Verdadero
CMP_END82:
  MOV8 R10, R05
  OR8 R10, R09  ; OR lógico
  MOVV8 R12, -20  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR4 R11, R12  ; Cargar mes
  CMPV R11, 2147483648
  JLT SSKIP83
  SUBV8 R11, 4294967296
SSKIP83:
  MOVV8 R13, 11
  CMP R11, R13
  MOVV1 R00, 0  ; Asumir falso
  JEQ CMP_TRUE84
  JMP CMP_END85
CMP_TRUE84:
  MOVV1 R00, 1  ; Verdadero
CMP_END85:
  MOV8 R01, R10
  OR8 R01, R00  ; OR lógico
  CMPV R01, 0
  JEQ ELIF86
  MOVV8 R02, 30
  MOVV8 R03, 0  ; Offset desde BP
  ADD8 R03, R14  ; Dirección = BP + offset
  STORER4 R02, R03  ; dias = valor
  JMP ENDIF51
ELIF86:
  MOVV8 R05, -20  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar mes
  CMPV R04, 2147483648
  JLT SSKIP87
  SUBV8 R04, 4294967296
SSKIP87:
  MOVV8 R06, 2
  CMP R04, R06
  MOVV1 R07, 0  ; Asumir falso
  JEQ CMP_TRUE88
  JMP CMP_END89
CMP_TRUE88:
  MOVV1 R07, 1  ; Verdadero
CMP_END89:
  CMPV R07, 0
  JEQ ELSE90
  MOVV8 R09, -24  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR4 R08, R09  ; Cargar ano
  CMPV R08, 2147483648
  JLT SSKIP92
  SUBV8 R08, 4294967296
SSKIP92:
  PUSH4 R08  ; Push argumento (entero4)
  CALL es_ano_bisiesto  ; Llamar a es_ano_bisiesto
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  CMPV R00, 0
  JEQ ELSE93
  MOVV8 R10, 29
  MOVV8 R11, 0  ; Offset desde BP
  ADD8 R11, R14  ; Dirección = BP + offset
  STORER4 R10, R11  ; dias = valor
  JMP ENDIF91
ELSE93:
  MOVV8 R12, 28
  MOVV8 R13, 0  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  STORER4 R12, R13  ; dias = valor
ENDIF91:
  JMP ENDIF51
ELSE90:
  MOVV8 R00, 0
  MOVV8 R01, 0  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  STORER4 R00, R01  ; dias = valor
ENDIF51:
  MOVV8 R03, 0  ; Offset desde BP
  ADD8 R03, R14  ; Dirección = BP + offset
  LOADR4 R02, R03  ; Cargar dias
  CMPV R02, 2147483648
  JLT SSKIP94
  SUBV8 R02, 4294967296
SSKIP94:
  MOV4 R00, R02  ; Valor de retorno en R00
  JMP dias_en_mes_epilogue

dias_en_mes_epilogue:
  ; Epílogo de dias_en_mes
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

.LOCAL_REL -20 4 mes ; FUNC=dias_en_mes
.LOCAL_REL -24 4 ano ; FUNC=dias_en_mes
.LOCAL_REL 0 4 dias ; FUNC=dias_en_mes
principal:  ; Función: principal
  ; Prólogo de principal
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 8  ; Reservar 8 bytes para locales

  ; Cuerpo de principal
  ; imprimir()
  MOVV8 R00, 0x1812D  ; __STR10
  PUSH8 R00
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R01, 42
  PUSH4 R01  ; Push argumento (entero4)
  CALL clasificar_temperatura  ; Llamar a clasificar_temperatura
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  MOVV8 R02, 25
  PUSH4 R02  ; Push argumento (entero4)
  CALL clasificar_temperatura  ; Llamar a clasificar_temperatura
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  MOVV8 R03, 8
  PUSH4 R03  ; Push argumento (entero4)
  CALL clasificar_temperatura  ; Llamar a clasificar_temperatura
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  MOVV8 R04, 5
  MOVV8 R05, 0
  SUB4 R05, R04
  PUSH4 R05  ; Push argumento (entero4)
  CALL clasificar_temperatura  ; Llamar a clasificar_temperatura
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  ; imprimir()
  MOVV8 R06, 0x18156  ; __STR11
  PUSH8 R06
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  ; Variable local: ano_prueba (offset: 0)
  MOVV8 R07, 2024
  MOVV8 R08, 0
  ADD8 R08, R14  ; Dirección = BP + offset
  STORER4 R07, R08  ; ano_prueba = valor_inicial
  MOVV8 R10, 0  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar ano_prueba
  CMPV R09, 2147483648
  JLT SSKIP96
  SUBV8 R09, 4294967296
SSKIP96:
  PUSH4 R09  ; Push argumento (entero4)
  CALL es_ano_bisiesto  ; Llamar a es_ano_bisiesto
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  CMPV R00, 0
  JEQ ENDIF95
  ; imprimir()
  MOVV8 R11, 0x1816D  ; __STR12
  PUSH8 R11
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF95
ENDIF95:
  MOVV8 R12, 2023
  MOVV8 R13, 0  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  STORER4 R12, R13  ; ano_prueba = valor
  MOVV8 R01, 0  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  LOADR4 R00, R01  ; Cargar ano_prueba
  CMPV R00, 2147483648
  JLT SSKIP98
  SUBV8 R00, 4294967296
SSKIP98:
  PUSH4 R00  ; Push argumento (entero4)
  CALL es_ano_bisiesto  ; Llamar a es_ano_bisiesto
  ADDV8 R15, 4  ; Limpiar 1 argumentos del stack
  NOT R02
  CMPV R02, 0
  JEQ ENDIF97
  ; imprimir()
  MOVV8 R03, 0x1817F  ; __STR13
  PUSH8 R03
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF97
ENDIF97:
  ; imprimir()
  MOVV8 R04, 0x18194  ; __STR14
  PUSH8 R04
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  ; Variable local: dias (offset: 4)
  MOVV8 R05, 2
  MOVV8 R06, 2024
  PUSH4 R06  ; Push argumento (entero4)
  PUSH4 R05  ; Push argumento (entero4)
  CALL dias_en_mes  ; Llamar a dias_en_mes
  ADDV8 R15, 8  ; Limpiar 2 argumentos del stack
  MOV4 R07, R00  ; Guardar valor de R00
  MOVV8 R08, 4
  ADD8 R08, R14  ; Dirección = BP + offset
  STORER4 R07, R08  ; dias = valor_inicial
  ; imprimir()
  MOVV8 R10, 4  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar dias
  CMPV R09, 2147483648
  JLT SSKIP99
  SUBV8 R09, 4294967296
SSKIP99:
  PUSH8 R09
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R11, 2
  MOVV8 R12, 2023
  PUSH4 R12  ; Push argumento (entero4)
  PUSH4 R11  ; Push argumento (entero4)
  CALL dias_en_mes  ; Llamar a dias_en_mes
  ADDV8 R15, 8  ; Limpiar 2 argumentos del stack
  MOVV8 R13, 4  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  STORER4 R00, R13  ; dias = valor
  ; imprimir()
  MOVV8 R01, 4  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  LOADR4 R00, R01  ; Cargar dias
  CMPV R00, 2147483648
  JLT SSKIP100
  SUBV8 R00, 4294967296
SSKIP100:
  PUSH8 R00
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R02, 7
  MOVV8 R03, 2024
  PUSH4 R03  ; Push argumento (entero4)
  PUSH4 R02  ; Push argumento (entero4)
  CALL dias_en_mes  ; Llamar a dias_en_mes
  ADDV8 R15, 8  ; Limpiar 2 argumentos del stack
  MOVV8 R04, 4  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  STORER4 R00, R04  ; dias = valor
  ; imprimir()
  MOVV8 R06, 4  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  LOADR4 R05, R06  ; Cargar dias
  CMPV R05, 2147483648
  JLT SSKIP101
  SUBV8 R05, 4294967296
SSKIP101:
  PUSH8 R05
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline

principal_epilogue:
  ; Epílogo de principal
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

.LOCAL_REL 0 4 ano_prueba ; FUNC=principal
.LOCAL_REL 4 4 dias ; FUNC=principal

END_PROGRAM:
; Fin del código ejecutable

; Fin del programa
PARAR