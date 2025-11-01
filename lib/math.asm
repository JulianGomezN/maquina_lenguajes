; ============================================
; BIBLIOTECA: MATH.ASM
; Funciones Matemáticas Básicas
; ============================================

; Constantes matemáticas
#define PI 314159
#define E 271828
#define ZERO 0
#define ONE 1

; Macro para calcular el cuadrado de un número
.macro SQUARE reg
    MUL reg, reg
.endmacro

; Macro para duplicar un número
.macro DOUBLE reg
    ADD reg, reg
.endmacro

; Macro para valor absoluto simple
.macro ABS reg, temp_reg
    CMPV reg, 0
    JPL skip_abs
    CLEAR temp_reg
    SUB temp_reg, reg
    LOADV reg, temp_reg
skip_abs:
.endmacro

; Macro para swap de dos registros
.macro SWAP reg1, reg2, temp
    MOV8 temp, reg1
    MOV8 reg1, reg2
    MOV8 reg2, temp
.endmacro
