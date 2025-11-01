; ============================================
; EJEMPLO SIMPLE: Sin usar macros complejos
; Solo usa #include para constantes y #define
; ============================================

#include "lib/math.asm"
#include "lib/io.asm"

; Calcular cuadrado de 5 manualmente
LOADV R1, 5
MUL R1, R1
; R1 = 25
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Duplicar un número
LOADV R2, 7
ADD R2, R2
; R2 = 14
SVIO R2, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Usar constante PI
LOADV R3, PI
SVIO R3, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Usar constante E
LOADV R4, E
SVIO R4, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

PARAR
