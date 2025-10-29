; ============================================
; EJEMPLO 1: Uso básico de #include
; Demuestra cómo incluir una biblioteca simple
; ============================================

; Incluir biblioteca de IO
#include "lib/io.asm"

; Programa principal
INICIO:
    ; Cargar un valor
    LOADV R1, 42
    
    ; Usar macro de la biblioteca IO
    PRINT_REG R1, IO_OUTPUT_1
    
    ; Fin
    PARAR
