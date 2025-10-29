; ============================================
; EJEMPLO 3: Include con macros y defines
; Demuestra el uso combinado de #define, macros e #include
; ============================================

; Incluir bibliotecas
#include "lib/math.asm"
#include "lib/io.asm"

; Definir constantes propias del programa
#define NUM1 15
#define NUM2 8
#define TEMP_ADDR 0x400

; Programa: Operaciones matemáticas
PROGRAMA:
    ; Cargar primer número
    LOADV R1, NUM1
    
    ; Cargar segundo número
    LOADV R2, NUM2
    
    ; Sumar
    ADD R1, R2         ; R1 = 23
    
    ; Duplicar resultado
    DOUBLE R1          ; R1 = 46
    
    ; Mostrar en salida
    PRINT_REG R1, TEMP_ADDR
    
    ; Calcular cuadrado del segundo número
    LOADV R3, NUM2
    SQUARE R3          ; R3 = 64
    
    ; Mostrar cuadrado
    PRINT_REG R3, IO_OUTPUT_2
    
    ; Finalizar
    PARAR
