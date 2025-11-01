; ============================================
; EJEMPLO: Uso de la biblioteca MATH.ASM
; Demuestra operaciones matemáticas básicas
; Usa constantes #define de las bibliotecas
; ============================================

#include "lib/math.asm"
#include "lib/io.asm"

; === OPERACIÓN 1: CUADRADO ===
; Calcular 5 * 5 = 25
LOADV R1, 5
MUL R1, R1
STOREV R1, 100
SVIO R1, 0x100
SHOWIO 0x100

; === OPERACIÓN 2: DOBLE ===
; Calcular 7 + 7 = 14
LOADV R2, 7
ADD R2, R2
STOREV R2, 200
SVIO R2, 0x200
SHOWIO 0x200

; === OPERACIÓN 3: INTERCAMBIO ===
; Intercambiar R5 y R6 usando MOV8
LOADV R5, 100
LOADV R6, 200
MOV8 R7, R5
MOV8 R5, R6
MOV8 R6, R7
SVIO R5, 0x100
SHOWIO 0x100
SVIO R6, 0x200
SHOWIO 0x200

; === OPERACIÓN 4: USAR CONSTANTES ===
; Mostrar PI
LOADV R1, PI
SVIO R1, 0x100
SHOWIO 0x100

; Mostrar E
LOADV R2, E
SVIO R2, 0x200
SHOWIO 0x200

; Mostrar ZERO
LOADV R3, ZERO
SVIO R3, 0x100
SHOWIO 0x100

; Mostrar ONE
LOADV R4, ONE
SVIO R4, 0x200
SHOWIO 0x200

PARAR
