; ============================================
; BIBLIOTECA: UTILS.ASM
; Utilidades y Constantes Comunes
; ============================================

; Constantes generales
#define TRUE 1
#define FALSE 0
#define NULL 0

; Tamaños de datos
#define BYTE_SIZE 1
#define WORD_SIZE 2
#define DWORD_SIZE 4
#define QWORD_SIZE 8

; Macro para limpiar un registro
.macro ZERO_REG reg
    CLEAR reg
.endmacro

; Macro para setear un registro a 1
.macro SET_ONE reg
    LOADV reg, 1
.endmacro

; Macro para incrementar N veces
.macro INC_N reg, n
    ADDV reg, n
.endmacro

; Macro para decrementar N veces
.macro DEC_N reg, n
    SUBV reg, n
.endmacro

; Macro para copiar registro
.macro COPY src, dst
    MOV8 dst, src
.endmacro

; Macro NOP extendido (para timing)
.macro WAIT cycles
    ; Placeholder - ejecutar NOP 'cycles' veces
    NOP
.endmacro
