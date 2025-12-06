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
