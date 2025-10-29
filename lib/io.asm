; ============================================
; BIBLIOTECA: IO.ASM
; Funciones de Entrada/Salida
; ============================================

; Macro para imprimir un registro en una dirección de memoria
.macro PRINT_REG reg, addr
    SVIO reg, addr
    SHOWIO addr
.endmacro

; Macro para limpiar el IO
.macro CLEAR_OUTPUT addr
    CLRIO addr
.endmacro

; Constantes de direcciones IO
#define IO_BASE 0x100
#define IO_OUTPUT_1 0x100
#define IO_OUTPUT_2 0x200
#define IO_INPUT_1 0x300
