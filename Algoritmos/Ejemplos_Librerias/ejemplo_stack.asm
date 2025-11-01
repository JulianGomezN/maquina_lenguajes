; ============================================
; EJEMPLO: Uso de operaciones de pila
; Demuestra PUSH y POP con diferentes tamaños
; ============================================

#include "lib/stack.asm"

; Configurar puntero de pila (R15 es el registro de pila)
LOADV R15, STACK_BASE

; === EJEMPLO 1: PUSH y POP con 8 bytes ===
LOADV R1, 100
PUSH8 R1

LOADV R2, 200
PUSH8 R2

LOADV R3, 300
PUSH8 R3

; Recuperar valores en orden inverso (LIFO)
POP8 R4
; R4 = 300
SVIO R4, 0x100
SHOWIO 0x100

POP8 R5
; R5 = 200
SVIO R5, 0x200
SHOWIO 0x200

POP8 R6
; R6 = 100
SVIO R6, 0x100
SHOWIO 0x100

; === EJEMPLO 2: PUSH y POP con 4 bytes ===
LOADV R7, 50
PUSH4 R7

LOADV R8, 75
PUSH4 R8

POP4 R9
; R9 = 75
SVIO R9, 0x200
SHOWIO 0x200

POP4 R10
; R10 = 50
SVIO R10, 0x100
SHOWIO 0x100

; === EJEMPLO 3: Guardar y restaurar múltiples registros ===
LOADV R1, 1
LOADV R2, 2
LOADV R3, 3
LOADV R4, 4

; Guardar en pila
PUSH8 R1
PUSH8 R2
PUSH8 R3
PUSH8 R4

; Modificar registros
CLEAR R1
CLEAR R2
CLEAR R3
CLEAR R4

; Mostrar que están en 0
SVIO R1, 0x100
SHOWIO 0x100

; Restaurar en orden inverso
POP8 R4
POP8 R3
POP8 R2
POP8 R1

; R1=1, R2=2, R3=3, R4=4 nuevamente
SVIO R1, 0x100
SHOWIO 0x100
SVIO R2, 0x200
SHOWIO 0x200
SVIO R3, 0x100
SHOWIO 0x100
SVIO R4, 0x200
SHOWIO 0x200

PARAR
