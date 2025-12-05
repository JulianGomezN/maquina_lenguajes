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
; Memoria layout:
;   0x0000-0x0FFF: Código (4KB)
;   0x1000-0x2FFF: Globales (8KB)
;   0x3000-0x7FFF: Strings (20KB)
;   0x8000-0xBFFF: Heap (16KB) <- Usado por malloc/free
;   0xC000-0xFFFF: Stack (16KB)
; ============================================================================

; Constantes (usadas como valores inmediatos en el código)
; HEAP_START:     0xA000      ; Inicio del heap (40KB desde inicio)
; HEAP_END:       0xE000      ; Fin del heap (56KB desde inicio)
; HEAP_SIZE:      0x4000      ; 16KB de heap
; BLOCK_HEADER:   16          ; Tamaño del header (8B size + 8B next)
; FREE_LIST_PTR:  0x1000      ; Variable global: puntero al primer bloque libre

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
    MOVV8 R01, 0xA000           ; R01 = dirección del primer bloque (HEAP_START)

    ; Escribir tamaño del bloque (0x4000 - 16)
    MOVV8 R02, 0x4000           ; HEAP_SIZE
    SUBV8 R02, 16               ; Restar BLOCK_HEADER
    STORER8 R02, R01            ; mem[HEAP_START] = tamaño

    ; Escribir puntero al siguiente bloque (NULL = 0)
    ADDV8 R01, 8                ; R01 = HEAP_START + 8
    MOVV8 R02, 0
    STORER8 R02, R01            ; mem[HEAP_START+8] = NULL

    ; Guardar puntero inicial en FREE_LIST_PTR
    MOVV8 R01, 0xA000           ; HEAP_START
    MOVV8 R03, 0x1000           ; FREE_LIST_PTR
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
    MOVV8 R06, 0x1000           ; FREE_LIST_PTR
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
    MOVV8 R06, 0x1000           ; FREE_LIST_PTR
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
    MOVV8 R03, 0x1000           ; FREE_LIST_PTR
    LOADR8 R02, R03             ; R02 = FREE_LIST_PTR
    MOV8 R03, R01
    ADDV8 R03, 8                ; R03 = bloque + 8
    STORER8 R02, R03            ; bloque->next = FREE_LIST_PTR

    ; FREE_LIST_PTR = bloque
    MOVV8 R03, 0x1000           ; FREE_LIST_PTR
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
MOVV8 R15, 0xC000        ; SP en 48KB (deja espacio para heap)
MOV8 R14, R15            ; BP = SP (frame inicial)

; Inicializar string literals en memoria (área 0x5000+)
; __STR0 = "Suma:" @ 0x5000
  MOVV1 R01, 83  ; 'S'
  STORE1 R01, 20480  ; Escribir en 0x5000
  MOVV1 R01, 117  ; 'u'
  STORE1 R01, 20481  ; Escribir en 0x5001
  MOVV1 R01, 109  ; 'm'
  STORE1 R01, 20482  ; Escribir en 0x5002
  MOVV1 R01, 97  ; 'a'
  STORE1 R01, 20483  ; Escribir en 0x5003
  MOVV1 R01, 58  ; ':'
  STORE1 R01, 20484  ; Escribir en 0x5004
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 20485  ; Escribir en 0x5005
; __STR1 = "OperaciÃ³n no reconocida " @ 0x5006
  MOVV1 R01, 79  ; 'O'
  STORE1 R01, 20486  ; Escribir en 0x5006
  MOVV1 R01, 112  ; 'p'
  STORE1 R01, 20487  ; Escribir en 0x5007
  MOVV1 R01, 101  ; 'e'
  STORE1 R01, 20488  ; Escribir en 0x5008
  MOVV1 R01, 114  ; 'r'
  STORE1 R01, 20489  ; Escribir en 0x5009
  MOVV1 R01, 97  ; 'a'
  STORE1 R01, 20490  ; Escribir en 0x500A
  MOVV1 R01, 99  ; 'c'
  STORE1 R01, 20491  ; Escribir en 0x500B
  MOVV1 R01, 105  ; 'i'
  STORE1 R01, 20492  ; Escribir en 0x500C
  MOVV1 R01, 195  ; 'Ã'
  STORE1 R01, 20493  ; Escribir en 0x500D
  MOVV1 R01, 179  ; '³'
  STORE1 R01, 20494  ; Escribir en 0x500E
  MOVV1 R01, 110  ; 'n'
  STORE1 R01, 20495  ; Escribir en 0x500F
  MOVV1 R01, 32  ; ' '
  STORE1 R01, 20496  ; Escribir en 0x5010
  MOVV1 R01, 110  ; 'n'
  STORE1 R01, 20497  ; Escribir en 0x5011
  MOVV1 R01, 111  ; 'o'
  STORE1 R01, 20498  ; Escribir en 0x5012
  MOVV1 R01, 32  ; ' '
  STORE1 R01, 20499  ; Escribir en 0x5013
  MOVV1 R01, 114  ; 'r'
  STORE1 R01, 20500  ; Escribir en 0x5014
  MOVV1 R01, 101  ; 'e'
  STORE1 R01, 20501  ; Escribir en 0x5015
  MOVV1 R01, 99  ; 'c'
  STORE1 R01, 20502  ; Escribir en 0x5016
  MOVV1 R01, 111  ; 'o'
  STORE1 R01, 20503  ; Escribir en 0x5017
  MOVV1 R01, 110  ; 'n'
  STORE1 R01, 20504  ; Escribir en 0x5018
  MOVV1 R01, 111  ; 'o'
  STORE1 R01, 20505  ; Escribir en 0x5019
  MOVV1 R01, 99  ; 'c'
  STORE1 R01, 20506  ; Escribir en 0x501A
  MOVV1 R01, 105  ; 'i'
  STORE1 R01, 20507  ; Escribir en 0x501B
  MOVV1 R01, 100  ; 'd'
  STORE1 R01, 20508  ; Escribir en 0x501C
  MOVV1 R01, 97  ; 'a'
  STORE1 R01, 20509  ; Escribir en 0x501D
  MOVV1 R01, 32  ; ' '
  STORE1 R01, 20510  ; Escribir en 0x501E
  MOVV1 R01, 0  ; NULL
  STORE1 R01, 20511  ; Escribir en 0x501F

; Llamar a la función principal
; ADVERTENCIA: No se encontró la función 'principal'
PARAR

; === FUNCIONES ===

calculadora:  ; Función: calculadora
  ; Prólogo de calculadora
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 4  ; Reservar 4 bytes para locales

  ; Cuerpo de calculadora
  ; Variable local: resultado (offset: 0)
  MOVV4 R00, 0
  MOV4 R01, R00  ; Guardar valor de R00
  MOVV8 R02, 0
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER4 R01, R02  ; resultado = valor_inicial
  MOVV8 R04, -25  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR1 R03, R04  ; Cargar operacion
  MOVV1 R05, 43
  CMP R03, R05
  MOVV1 R06, 0  ; Asumir falso
  JEQ CMP_TRUE1
  JMP CMP_END2
CMP_TRUE1:
  MOVV1 R06, 1  ; Verdadero
CMP_END2:
  CMPV R06, 0
  JEQ ELIF3
  MOVV8 R08, -20  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  LOADR4 R07, R08  ; Cargar a
  MOVV8 R10, -24  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar b
  MOV4 R11, R07
  ADD4 R11, R09
  MOVV8 R12, 0  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  STORER4 R11, R12  ; resultado = valor
  ; imprimir()
  MOVV8 R13, 0x5000  ; __STR0
  PUSH8 R13
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF3:
  MOVV8 R01, -25  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  LOADR1 R00, R01  ; Cargar operacion
  MOVV1 R02, 45
  CMP R00, R02
  MOVV1 R03, 0  ; Asumir falso
  JEQ CMP_TRUE4
  JMP CMP_END5
CMP_TRUE4:
  MOVV1 R03, 1  ; Verdadero
CMP_END5:
  CMPV R03, 0
  JEQ ELIF6
  MOVV8 R05, -20  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar a
  MOVV8 R07, -24  ; Offset desde BP
  ADD8 R07, R14  ; Dirección = BP + offset
  LOADR4 R06, R07  ; Cargar b
  MOV4 R08, R04
  SUB4 R08, R06
  MOVV8 R09, 0  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  STORER4 R08, R09  ; resultado = valor
  ; imprimir()
  MOVV8 R10, 0  ; ERROR: String no inicializado
  PUSH8 R10
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF6:
  MOVV8 R12, -25  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR1 R11, R12  ; Cargar operacion
  MOVV1 R13, 42
  CMP R11, R13
  MOVV1 R00, 0  ; Asumir falso
  JEQ CMP_TRUE7
  JMP CMP_END8
CMP_TRUE7:
  MOVV1 R00, 1  ; Verdadero
CMP_END8:
  CMPV R00, 0
  JEQ ELIF9
  MOVV8 R02, -20  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  LOADR4 R01, R02  ; Cargar a
  MOVV8 R04, -24  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar b
  MOV4 R05, R01
  MUL4 R05, R03
  MOVV8 R06, 0  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  STORER4 R05, R06  ; resultado = valor
  ; imprimir()
  MOVV8 R07, 0  ; ERROR: String no inicializado
  PUSH8 R07
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF0
ELIF9:
  MOVV8 R09, -25  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR1 R08, R09  ; Cargar operacion
  MOVV1 R10, 47
  CMP R08, R10
  MOVV1 R11, 0  ; Asumir falso
  JEQ CMP_TRUE10
  JMP CMP_END11
CMP_TRUE10:
  MOVV1 R11, 1  ; Verdadero
CMP_END11:
  CMPV R11, 0
  JEQ ELIF12
  MOVV8 R13, -24  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  LOADR4 R12, R13  ; Cargar b
  MOVV1 R00, 0
  CMP R12, R00
  MOVV1 R01, 0  ; Asumir falso
  JNE CMP_TRUE14
  JMP CMP_END15
CMP_TRUE14:
  MOVV1 R01, 1  ; Verdadero
CMP_END15:
  CMPV R01, 0
  JEQ ELSE16
  MOVV8 R03, -20  ; Offset desde BP
  ADD8 R03, R14  ; Dirección = BP + offset
  LOADR4 R02, R03  ; Cargar a
  MOVV8 R05, -24  ; Offset desde BP
  ADD8 R05, R14  ; Dirección = BP + offset
  LOADR4 R04, R05  ; Cargar b
  MOV4 R06, R02
  DIV4 R06, R04
  MOVV8 R07, 0  ; Offset desde BP
  ADD8 R07, R14  ; Dirección = BP + offset
  STORER4 R06, R07  ; resultado = valor
  ; imprimir()
  MOVV8 R08, 0  ; ERROR: String no inicializado
  PUSH8 R08
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF13
ELSE16:
  ; imprimir()
  MOVV8 R09, 0  ; ERROR: String no inicializado
  PUSH8 R09
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV4 R10, 0
  MOVV8 R11, 0  ; Offset desde BP
  ADD8 R11, R14  ; Dirección = BP + offset
  STORER4 R10, R11  ; resultado = valor
ENDIF13:
  JMP ENDIF0
ELIF12:
  MOVV8 R13, -25  ; Offset desde BP
  ADD8 R13, R14  ; Dirección = BP + offset
  LOADR1 R12, R13  ; Cargar operacion
  MOVV1 R00, 37
  CMP R12, R00
  MOVV1 R01, 0  ; Asumir falso
  JEQ CMP_TRUE17
  JMP CMP_END18
CMP_TRUE17:
  MOVV1 R01, 1  ; Verdadero
CMP_END18:
  CMPV R01, 0
  JEQ ELSE19
  MOVV8 R03, -24  ; Offset desde BP
  ADD8 R03, R14  ; Dirección = BP + offset
  LOADR4 R02, R03  ; Cargar b
  MOVV1 R04, 0
  CMP R02, R04
  MOVV1 R05, 0  ; Asumir falso
  JNE CMP_TRUE21
  JMP CMP_END22
CMP_TRUE21:
  MOVV1 R05, 1  ; Verdadero
CMP_END22:
  CMPV R05, 0
  JEQ ELSE23
  MOVV8 R07, -20  ; Offset desde BP
  ADD8 R07, R14  ; Dirección = BP + offset
  LOADR4 R06, R07  ; Cargar a
  MOVV8 R09, -24  ; Offset desde BP
  ADD8 R09, R14  ; Dirección = BP + offset
  LOADR4 R08, R09  ; Cargar b
  MOV4 R10, R06
  MOD4 R10, R08
  MOVV8 R11, 0  ; Offset desde BP
  ADD8 R11, R14  ; Dirección = BP + offset
  STORER4 R10, R11  ; resultado = valor
  ; imprimir()
  MOVV8 R12, 0  ; ERROR: String no inicializado
  PUSH8 R12
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  JMP ENDIF20
ELSE23:
  ; imprimir()
  MOVV8 R13, 0  ; ERROR: String no inicializado
  PUSH8 R13
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV4 R00, 0
  MOVV8 R01, 0  ; Offset desde BP
  ADD8 R01, R14  ; Dirección = BP + offset
  STORER4 R00, R01  ; resultado = valor
ENDIF20:
  JMP ENDIF0
ELSE19:
  ; imprimir()
  MOVV8 R02, 0x5006  ; __STR1
  PUSH8 R02
  CALL __print_string
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV4 R03, 0
  MOVV8 R04, 0  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  STORER4 R03, R04  ; resultado = valor
ENDIF0:
  MOVV8 R06, 0  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  LOADR4 R05, R06  ; Cargar resultado
  MOV4 R00, R05  ; Valor de retorno en R00
  JMP calculadora_epilogue

calculadora_epilogue:
  ; Epílogo de calculadora
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller

main:  ; Función: main
  ; Prólogo de main
  PUSH8 R14          ; Guardar BP del caller en stack
  MOV8 R14, R15      ; BP = SP (inicio del frame actual)
  ADDV8 R15, 12  ; Reservar 12 bytes para locales

  ; Cuerpo de main
  ; Variable local: x (offset: 0)
  MOVV4 R00, 20
  MOV4 R01, R00  ; Guardar valor de R00
  MOVV8 R02, 0
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER4 R01, R02  ; x = valor_inicial
  ; Variable local: y (offset: 4)
  MOVV4 R03, 5
  MOVV8 R04, 4
  ADD8 R04, R14  ; Dirección = BP + offset
  STORER4 R03, R04  ; y = valor_inicial
  ; Variable local: res (offset: 8)
  MOVV4 R05, 0
  MOVV8 R06, 8
  ADD8 R06, R14  ; Dirección = BP + offset
  STORER4 R05, R06  ; res = valor_inicial
  MOVV8 R08, 0  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  LOADR4 R07, R08  ; Cargar x
  MOVV8 R10, 4  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar y
  MOVV1 R11, 43
  PUSH1 R11  ; Push argumento (caracter)
  PUSH4 R09  ; Push argumento (entero4)
  PUSH4 R07  ; Push argumento (entero4)
  CALL calculadora  ; Llamar a calculadora
  ADDV8 R15, 9  ; Limpiar 3 argumentos del stack
  MOVV8 R12, 8  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  STORER4 R00, R12  ; res = valor
  ; imprimir()
  MOVV8 R00, 8  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  LOADR4 R13, R00  ; Cargar res
  PUSH8 R13
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R02, 0  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  LOADR4 R01, R02  ; Cargar x
  MOVV8 R04, 4  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar y
  MOVV1 R05, 45
  PUSH1 R05  ; Push argumento (caracter)
  PUSH4 R03  ; Push argumento (entero4)
  PUSH4 R01  ; Push argumento (entero4)
  CALL calculadora  ; Llamar a calculadora
  ADDV8 R15, 9  ; Limpiar 3 argumentos del stack
  MOVV8 R06, 8  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  STORER4 R00, R06  ; res = valor
  ; imprimir()
  MOVV8 R08, 8  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  LOADR4 R07, R08  ; Cargar res
  PUSH8 R07
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R10, 0  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar x
  MOVV8 R12, 4  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR4 R11, R12  ; Cargar y
  MOVV1 R13, 42
  PUSH1 R13  ; Push argumento (caracter)
  PUSH4 R11  ; Push argumento (entero4)
  PUSH4 R09  ; Push argumento (entero4)
  CALL calculadora  ; Llamar a calculadora
  ADDV8 R15, 9  ; Limpiar 3 argumentos del stack
  MOVV8 R00, 8  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  STORER4 R00, R00  ; res = valor
  ; imprimir()
  MOVV8 R02, 8  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  LOADR4 R01, R02  ; Cargar res
  PUSH8 R01
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R04, 0  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar x
  MOVV8 R06, 4  ; Offset desde BP
  ADD8 R06, R14  ; Dirección = BP + offset
  LOADR4 R05, R06  ; Cargar y
  MOVV1 R07, 47
  PUSH1 R07  ; Push argumento (caracter)
  PUSH4 R05  ; Push argumento (entero4)
  PUSH4 R03  ; Push argumento (entero4)
  CALL calculadora  ; Llamar a calculadora
  ADDV8 R15, 9  ; Limpiar 3 argumentos del stack
  MOVV8 R08, 8  ; Offset desde BP
  ADD8 R08, R14  ; Dirección = BP + offset
  STORER4 R00, R08  ; res = valor
  ; imprimir()
  MOVV8 R10, 8  ; Offset desde BP
  ADD8 R10, R14  ; Dirección = BP + offset
  LOADR4 R09, R10  ; Cargar res
  PUSH8 R09
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline
  MOVV8 R12, 0  ; Offset desde BP
  ADD8 R12, R14  ; Dirección = BP + offset
  LOADR4 R11, R12  ; Cargar x
  MOVV8 R00, 4  ; Offset desde BP
  ADD8 R00, R14  ; Dirección = BP + offset
  LOADR4 R13, R00  ; Cargar y
  MOVV1 R01, 37
  PUSH1 R01  ; Push argumento (caracter)
  PUSH4 R13  ; Push argumento (entero4)
  PUSH4 R11  ; Push argumento (entero4)
  CALL calculadora  ; Llamar a calculadora
  ADDV8 R15, 9  ; Limpiar 3 argumentos del stack
  MOVV8 R02, 8  ; Offset desde BP
  ADD8 R02, R14  ; Dirección = BP + offset
  STORER4 R00, R02  ; res = valor
  ; imprimir()
  MOVV8 R04, 8  ; Offset desde BP
  ADD8 R04, R14  ; Dirección = BP + offset
  LOADR4 R03, R04  ; Cargar res
  PUSH8 R03
  CALL __print_int8
  ADDV8 R15, 8  ; Limpiar stack
  CALL __print_newline

main_epilogue:
  ; Epílogo de main
  MOV8 R15, R14      ; SP = BP (liberar locales)
  POP8 R14           ; Restaurar BP del caller
  RET                ; Retornar al caller


END_PROGRAM:
; Fin del código ejecutable

; Fin del programa
PARAR