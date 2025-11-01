; ============================================
; EJEMPLO: Uso de la biblioteca UTILS.ASM
; Demuestra utilidades y constantes comunes
; Usa solo constantes #define
; ============================================

#include "lib/utils.asm"
#include "lib/io.asm"

; Usar constantes booleanas
LOADV R1, TRUE
STOREV R1, 100
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

LOADV R2, FALSE
SVIO R2, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Limpiar registros
LOADV R3, 12345
CLEAR R3
; R3 = 0
SVIO R3, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Setear registro a 1
LOADV R4, 1
; R4 = 1
SVIO R4, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Incrementar N veces manualmente
CLEAR R5
ADDV R5, 10
; R5 = 10
SVIO R5, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

ADDV R5, 5
; R5 = 15
SVIO R5, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2

; Decrementar N veces manualmente
SUBV R5, 7
; R5 = 8
SVIO R5, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1

; Copiar valores entre registros usando MOV8
LOADV R6, 777
MOV8 R7, R6
; R7 = 777
SVIO R7, 0x200
SHOWIO 0x200

; Usar constantes de tamaño
LOADV R1, BYTE_SIZE
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1
; R1 = 1

LOADV R1, WORD_SIZE
SVIO R1, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2
; R1 = 2

LOADV R1, DWORD_SIZE
SVIO R1, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1
; R1 = 4

LOADV R1, QWORD_SIZE
SVIO R1, IO_OUTPUT_2
SHOWIO IO_OUTPUT_2
; R1 = 8

; Usar NULL
LOADV R2, NULL
SVIO R2, IO_OUTPUT_1
SHOWIO IO_OUTPUT_1
; R2 = 0

; Esperar (NOP)
NOP
NOP
NOP
NOP
NOP

PARAR
