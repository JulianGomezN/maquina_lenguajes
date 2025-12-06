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
;   __STR0: 'CalificaciÃ³n: A - Excelente'
;   __STR1: 'CalificaciÃ³n: B - Muy bueno'
;   __STR2: 'CalificaciÃ³n: C - Bueno'
;   __STR3: 'CalificaciÃ³n: D - Suficiente'
;   __STR4: 'CalificaciÃ³n: F - Reprobado'
; Inicializar string literals en memoria (área 0x18000+)
; __STR0 = "CalificaciÃ³n: A - Excelente" @ 0x18000
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98304  ; Escribir en 0x18000
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98305  ; Escribir en 0x18001
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98306  ; Escribir en 0x18002
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98307  ; Escribir en 0x18003
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98308  ; Escribir en 0x18004
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98309  ; Escribir en 0x18005
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98310  ; Escribir en 0x18006
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98311  ; Escribir en 0x18007
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98312  ; Escribir en 0x18008
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98313  ; Escribir en 0x18009
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98314  ; Escribir en 0x1800A
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98315  ; Escribir en 0x1800B
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98316  ; Escribir en 0x1800C
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98317  ; Escribir en 0x1800D
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98318  ; Escribir en 0x1800E
  MOVV1 R01, 58  ; byte 0x3A
  STORE1 R01, 98319  ; Escribir en 0x1800F
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98320  ; Escribir en 0x18010
  MOVV1 R01, 65  ; byte 0x41
  STORE1 R01, 98321  ; Escribir en 0x18011
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98322  ; Escribir en 0x18012
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98323  ; Escribir en 0x18013
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98324  ; Escribir en 0x18014
  MOVV1 R01, 69  ; byte 0x45
  STORE1 R01, 98325  ; Escribir en 0x18015
  MOVV1 R01, 120  ; byte 0x78
  STORE1 R01, 98326  ; Escribir en 0x18016
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98327  ; Escribir en 0x18017
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98328  ; Escribir en 0x18018
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98329  ; Escribir en 0x18019
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98330  ; Escribir en 0x1801A
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98331  ; Escribir en 0x1801B
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98332  ; Escribir en 0x1801C
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98333  ; Escribir en 0x1801D
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98334  ; Escribir en 0x1801E
; __STR1 = "CalificaciÃ³n: B - Muy bueno" @ 0x1801F
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98335  ; Escribir en 0x1801F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98336  ; Escribir en 0x18020
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98337  ; Escribir en 0x18021
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98338  ; Escribir en 0x18022
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98339  ; Escribir en 0x18023
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98340  ; Escribir en 0x18024
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98341  ; Escribir en 0x18025
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98342  ; Escribir en 0x18026
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98343  ; Escribir en 0x18027
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98344  ; Escribir en 0x18028
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98345  ; Escribir en 0x18029
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98346  ; Escribir en 0x1802A
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98347  ; Escribir en 0x1802B
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98348  ; Escribir en 0x1802C
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98349  ; Escribir en 0x1802D
  MOVV1 R01, 58  ; byte 0x3A
  STORE1 R01, 98350  ; Escribir en 0x1802E
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98351  ; Escribir en 0x1802F
  MOVV1 R01, 66  ; byte 0x42
  STORE1 R01, 98352  ; Escribir en 0x18030
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98353  ; Escribir en 0x18031
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98354  ; Escribir en 0x18032
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98355  ; Escribir en 0x18033
  MOVV1 R01, 77  ; byte 0x4D
  STORE1 R01, 98356  ; Escribir en 0x18034
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98357  ; Escribir en 0x18035
  MOVV1 R01, 121  ; byte 0x79
  STORE1 R01, 98358  ; Escribir en 0x18036
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98359  ; Escribir en 0x18037
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98360  ; Escribir en 0x18038
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98361  ; Escribir en 0x18039
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98362  ; Escribir en 0x1803A
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98363  ; Escribir en 0x1803B
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98364  ; Escribir en 0x1803C
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98365  ; Escribir en 0x1803D
; __STR2 = "CalificaciÃ³n: C - Bueno" @ 0x1803E
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98366  ; Escribir en 0x1803E
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98367  ; Escribir en 0x1803F
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98368  ; Escribir en 0x18040
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98369  ; Escribir en 0x18041
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98370  ; Escribir en 0x18042
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98371  ; Escribir en 0x18043
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98372  ; Escribir en 0x18044
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98373  ; Escribir en 0x18045
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98374  ; Escribir en 0x18046
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98375  ; Escribir en 0x18047
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98376  ; Escribir en 0x18048
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98377  ; Escribir en 0x18049
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98378  ; Escribir en 0x1804A
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98379  ; Escribir en 0x1804B
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98380  ; Escribir en 0x1804C
  MOVV1 R01, 58  ; byte 0x3A
  STORE1 R01, 98381  ; Escribir en 0x1804D
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98382  ; Escribir en 0x1804E
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98383  ; Escribir en 0x1804F
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98384  ; Escribir en 0x18050
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98385  ; Escribir en 0x18051
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98386  ; Escribir en 0x18052
  MOVV1 R01, 66  ; byte 0x42
  STORE1 R01, 98387  ; Escribir en 0x18053
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98388  ; Escribir en 0x18054
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98389  ; Escribir en 0x18055
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98390  ; Escribir en 0x18056
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98391  ; Escribir en 0x18057
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98392  ; Escribir en 0x18058
; __STR3 = "CalificaciÃ³n: D - Suficiente" @ 0x18059
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98393  ; Escribir en 0x18059
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98394  ; Escribir en 0x1805A
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98395  ; Escribir en 0x1805B
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98396  ; Escribir en 0x1805C
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98397  ; Escribir en 0x1805D
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98398  ; Escribir en 0x1805E
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98399  ; Escribir en 0x1805F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98400  ; Escribir en 0x18060
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98401  ; Escribir en 0x18061
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98402  ; Escribir en 0x18062
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98403  ; Escribir en 0x18063
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98404  ; Escribir en 0x18064
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98405  ; Escribir en 0x18065
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98406  ; Escribir en 0x18066
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98407  ; Escribir en 0x18067
  MOVV1 R01, 58  ; byte 0x3A
  STORE1 R01, 98408  ; Escribir en 0x18068
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98409  ; Escribir en 0x18069
  MOVV1 R01, 68  ; byte 0x44
  STORE1 R01, 98410  ; Escribir en 0x1806A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98411  ; Escribir en 0x1806B
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98412  ; Escribir en 0x1806C
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98413  ; Escribir en 0x1806D
  MOVV1 R01, 83  ; byte 0x53
  STORE1 R01, 98414  ; Escribir en 0x1806E
  MOVV1 R01, 117  ; byte 0x75
  STORE1 R01, 98415  ; Escribir en 0x1806F
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98416  ; Escribir en 0x18070
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98417  ; Escribir en 0x18071
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98418  ; Escribir en 0x18072
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98419  ; Escribir en 0x18073
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98420  ; Escribir en 0x18074
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98421  ; Escribir en 0x18075
  MOVV1 R01, 116  ; byte 0x74
  STORE1 R01, 98422  ; Escribir en 0x18076
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98423  ; Escribir en 0x18077
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98424  ; Escribir en 0x18078
; __STR4 = "CalificaciÃ³n: F - Reprobado" @ 0x18079
  MOVV1 R01, 67  ; byte 0x43
  STORE1 R01, 98425  ; Escribir en 0x18079
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98426  ; Escribir en 0x1807A
  MOVV1 R01, 108  ; byte 0x6C
  STORE1 R01, 98427  ; Escribir en 0x1807B
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98428  ; Escribir en 0x1807C
  MOVV1 R01, 102  ; byte 0x66
  STORE1 R01, 98429  ; Escribir en 0x1807D
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98430  ; Escribir en 0x1807E
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98431  ; Escribir en 0x1807F
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98432  ; Escribir en 0x18080
  MOVV1 R01, 99  ; byte 0x63
  STORE1 R01, 98433  ; Escribir en 0x18081
  MOVV1 R01, 105  ; byte 0x69
  STORE1 R01, 98434  ; Escribir en 0x18082
  MOVV1 R01, 195  ; byte 0xC3
  STORE1 R01, 98435  ; Escribir en 0x18083
  MOVV1 R01, 131  ; byte 0x83
  STORE1 R01, 98436  ; Escribir en 0x18084
  MOVV1 R01, 194  ; byte 0xC2
  STORE1 R01, 98437  ; Escribir en 0x18085
  MOVV1 R01, 179  ; byte 0xB3
  STORE1 R01, 98438  ; Escribir en 0x18086
  MOVV1 R01, 110  ; byte 0x6E
  STORE1 R01, 98439  ; Escribir en 0x18087
  MOVV1 R01, 58  ; byte 0x3A
  STORE1 R01, 98440  ; Escribir en 0x18088
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98441  ; Escribir en 0x18089
  MOVV1 R01, 70  ; byte 0x46
  STORE1 R01, 98442  ; Escribir en 0x1808A
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98443  ; Escribir en 0x1808B
  MOVV1 R01, 45  ; byte 0x2D
  STORE1 R01, 98444  ; Escribir en 0x1808C
  MOVV1 R01, 32  ; byte 0x20
  STORE1 R01, 98445  ; Escribir en 0x1808D
  MOVV1 R01, 82  ; byte 0x52
  STORE1 R01, 98446  ; Escribir en 0x1808E
  MOVV1 R01, 101  ; byte 0x65
  STORE1 R01, 98447  ; Escribir en 0x1808F
  MOVV1 R01, 112  ; byte 0x70
  STORE1 R01, 98448  ; Escribir en 0x18090
  MOVV1 R01, 114  ; byte 0x72
  STORE1 R01, 98449  ; Escribir en 0x18091
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98450  ; Escribir en 0x18092
  MOVV1 R01, 98  ; byte 0x62
  STORE1 R01, 98451  ; Escribir en 0x18093
  MOVV1 R01, 97  ; byte 0x61
  STORE1 R01, 98452  ; Escribir en 0x18094
  MOVV1 R01, 100  ; byte 0x64
  STORE1 R01, 98453  ; Escribir en 0x18095
  MOVV1 R01, 111  ; byte 0x6F
  STORE1 R01, 98454  ; Escribir en 0x18096
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 98455  ; Escribir en 0x18097

; Llamar a la función principal
CALL principal
JMP END_PROGRAM

; === FUNCIONES ===

clasificar_calificacion:  ; Función: clasificar_calificacion
  ; Prólogo de clasificar_calificacion
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 4  ; Reservar 4 bytes para locales

  ; Cuerpo de clasificar_calificacion
  ; Variable local: nota (offset: 0)
  MOVV4 R00, 85
  MOV4 R01, R00  ; Guardar valor de R00
  MOVV8 R02, 0
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER4 R01, R02  ; nota = valor_inicial
  MOVV8 R04, 0  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar nota
  MOVV1 R05, 90
  CMP R03, R05
  MOVV1 R06, 0  ; Asumir falso
  JGE CMP_TRUE1
  JMP CMP_END2
CMP_TRUE1:
  MOVV1 R06, 1  ; Verdadero
CMP_END2:
  CMPV R06, 0
  JEQ ELIF3
  ; imprimir()
  MOVV8 R07, 0x18000  ; __STR0
  PUSH8 R07
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF3:
  MOVV8 R09, 0  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR4 R08, R09  ; Cargar nota
  MOVV1 R10, 80
  CMP R08, R10
  MOVV1 R11, 0  ; Asumir falso
  JGE CMP_TRUE4
  JMP CMP_END5
CMP_TRUE4:
  MOVV1 R11, 1  ; Verdadero
CMP_END5:
  CMPV R11, 0
  JEQ ELIF6
  ; imprimir()
  MOVV8 R12, 0x1801F  ; __STR1
  PUSH8 R12
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF6:
  MOVV8 R00, 0  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  LOADR4 R13, R00  ; Cargar nota
  MOVV1 R01, 70
  CMP R13, R01
  MOVV1 R02, 0  ; Asumir falso
  JGE CMP_TRUE7
  JMP CMP_END8
CMP_TRUE7:
  MOVV1 R02, 1  ; Verdadero
CMP_END8:
  CMPV R02, 0
  JEQ ELIF9
  ; imprimir()
  MOVV8 R03, 0x1803E  ; __STR2
  PUSH8 R03
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF9:
  MOVV8 R05, 0  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar nota
  MOVV1 R06, 60
  CMP R04, R06
  MOVV1 R07, 0  ; Asumir falso
  JGE CMP_TRUE10
  JMP CMP_END11
CMP_TRUE10:
  MOVV1 R07, 1  ; Verdadero
CMP_END11:
  CMPV R07, 0
  JEQ ELSE12
  ; imprimir()
  MOVV8 R08, 0x18059  ; __STR3
  PUSH8 R08
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELSE12:
  ; imprimir()
  MOVV8 R09, 0x18079  ; __STR4
  PUSH8 R09
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
ENDIF0:

clasificar_calificacion_epilogue:
  ; Epílogo de clasificar_calificacion
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

.LOCAL_REL 0 4 nota ; FUNC=clasificar_calificacion
principal:  ; Función: principal
  ; Prólogo de principal
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ; Sin variables locales

  ; Cuerpo de principal
  CALL clasificar_calificacion  ; Llamar a clasificar_calificacion

principal_epilogue:
  ; Epílogo de principal
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller


END_PROGRAM:
; Fin del código ejecutable

; Fin del programa
PARAR