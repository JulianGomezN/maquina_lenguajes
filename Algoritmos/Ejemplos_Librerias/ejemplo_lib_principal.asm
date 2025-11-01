; ============================================
; EJEMPLO: Uso combinado de todas las bibliotecas
; Demuestra el uso de múltiples bibliotecas juntas
; ============================================

#include "lib/math.asm"
#include "lib/io.asm"
#include "lib/utils.asm"
#include "lib/stack.asm"

; Todas las bibliotecas están incluidas

; === OPERACIÓN 1: Usar constantes matemáticas ===
LOADV R1, PI
SVIO R1, 0x100
SHOWIO 0x100

LOADV R2, E
SVIO R2, 0x200
SHOWIO 0x200

; === OPERACIÓN 2: Operaciones matemáticas ===
; Calcular cuadrado de 7: 7*7 = 49
LOADV R3, 7
MUL R3, R3
SVIO R3, 0x100
SHOWIO 0x100

; Calcular doble de 8: 8+8 = 16
LOADV R4, 8
ADD R4, R4
SVIO R4, 0x200
SHOWIO 0x200

; === OPERACIÓN 3: Usar pila ===
; Configurar puntero de pila
LOADV R15, STACK_BASE

; Guardar valores en la pila
LOADV R5, 100
PUSH8 R5

LOADV R6, 200
PUSH8 R6

LOADV R7, 300
PUSH8 R7

; Recuperar valores en orden inverso
POP8 R8
SVIO R8, 0x100
SHOWIO 0x100
; R8 = 300

POP8 R9
SVIO R9, 0x200
SHOWIO 0x200
; R9 = 200

POP8 R10
SVIO R10, 0x100
SHOWIO 0x100
; R10 = 100

; === OPERACIÓN 4: Copiar entre registros ===
LOADV R11, 777
MOV8 R12, R11
SVIO R12, 0x200
SHOWIO 0x200

; === OPERACIÓN 5: Usar constantes de utils ===
LOADV R1, TRUE
SVIO R1, 0x100
SHOWIO 0x100

LOADV R2, FALSE
SVIO R2, 0x200
SHOWIO 0x200

; === OPERACIÓN 6: Ejemplo complejo (a^2 + b^2) ===
; Calcular 3^2 + 4^2 = 9 + 16 = 25
LOADV R1, 3
LOADV R2, 4

; Guardar originales en pila
PUSH8 R1
PUSH8 R2

; Calcular cuadrados
MUL R1, R1
; R1 = 9
MUL R2, R2
; R2 = 16

; Sumar
ADD R1, R2
; R1 = 25
SVIO R1, 0x100
SHOWIO 0x100

; Restaurar valores originales
POP8 R2
POP8 R1
SVIO R1, 0x200
SHOWIO 0x200
SVIO R2, 0x100
SHOWIO 0x100

PARAR
