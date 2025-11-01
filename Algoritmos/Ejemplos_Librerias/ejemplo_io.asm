; ============================================
; EJEMPLO: Uso de la biblioteca IO.ASM
; Demuestra operaciones de entrada/salida
; Usa solo constantes #define
; ============================================

#include "lib/io.asm"
#include "lib/utils.asm"

; Imprimir un valor simple
LOADV R1, 42
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Imprimir múltiples valores
LOADV R2, 100
SVIO R2, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Limpiar salida
CLRIO IO_OUTPUT_1

; Imprimir nuevo valor después de limpiar
LOADV R3, 255
SVIO R3, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Imprimir resultado de operación
LOADV R4, 10
LOADV R5, 20
ADD R4, R5
; R4 = 30
SVIO R4, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Usar las direcciones definidas
LOADV R6, 999
SVIO R6, IO_BASE
SHOWIO IO_BASE

; Secuencia de impresión usando constantes
LOADV R1, FALSE
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

LOADV R1, TRUE
SVIO R1, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Operaciones simples
CLEAR R1
; R1 = 0
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

LOADV R1, 1
SVIO R1, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Incrementar manualmente
ADDV R1, 5
; R1 = 6
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Decrementar manualmente
SUBV R1, 3
; R1 = 3
SVIO R1, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

PARAR
