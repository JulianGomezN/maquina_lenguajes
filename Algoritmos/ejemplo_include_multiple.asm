; ============================================
; EJEMPLO 2: Múltiples includes
; Demuestra el uso de múltiples bibliotecas
; ============================================

; Incluir múltiples bibliotecas
#include "lib/math.asm"
#include "lib/io.asm"
#include "lib/utils.asm"

; Programa: Calcula el cuadrado de un número y lo muestra
MAIN:
    ; Cargar número a elevar al cuadrado
    LOADV R1, 7
    
    ; Duplicar el número (usando macro de math.asm)
    DOUBLE R1          ; R1 = 14
    
    ; Mostrar resultado (usando macro de io.asm)
    PRINT_REG R1, IO_OUTPUT_1
    
    ; Limpiar salida
    CLEAR_OUTPUT IO_OUTPUT_1
    
    ; Fin
    PARAR
