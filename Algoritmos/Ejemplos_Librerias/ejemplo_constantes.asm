; ============================================
; EJEMPLO: Probando constantes de bibliotecas
; ============================================

#include "lib/math.asm"
#include "lib/io.asm"

; Probar constantes matemáticas
LOADV R1, PI
SVIO R1, 0x100
SHOWIO 0x100

LOADV R2, E
SVIO R2, 0x200
SHOWIO 0x200

; Probar constantes IO
LOADV R3, 42
SVIO R3, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

LOADV R4, 99
SVIO R4, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

PARAR
