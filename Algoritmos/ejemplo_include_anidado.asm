; ============================================
; EJEMPLO 5: Usando include anidado
; Usa lib_principal.asm que a su vez incluye otras
; ============================================

; Solo incluir la biblioteca principal
; Esta automáticamente incluye math.asm, io.asm y utils.asm
#include "lib/lib_principal.asm"

; Ahora tenemos acceso a todas las macros y defines

MAIN:
    ; Cargar un número
    LOADV R1, 5
    
    ; Imprimir el cuadrado (sin modificar R1)
    PRINT_SQUARE R1, IO_OUTPUT_1
    
    ; Imprimir el doble (sin modificar R1)
    PRINT_DOUBLE R1, IO_OUTPUT_2
    
    ; R1 todavía tiene el valor original
    PRINT_REG R1, 0x300
    
    PARAR
