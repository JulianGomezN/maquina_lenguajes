; ============================================
; EJEMPLO 4: Include anidado
; lib_principal.asm incluye otras bibliotecas
; ============================================

; Esta biblioteca incluye otras bibliotecas
#include "lib/math.asm"
#include "lib/io.asm"
#include "lib/utils.asm"
#include "lib/stack.asm"

; Definir macros adicionales que usan las otras bibliotecas
.macro PRINT_SQUARE reg, output_addr
    ; Guardar valor original
    PUSH_QWORD reg
    
    ; Calcular cuadrado
    SQUARE reg
    
    ; Imprimir
    PRINT_REG reg, output_addr
    
    ; Restaurar valor original
    POP_QWORD reg
.endmacro

.macro PRINT_DOUBLE reg, output_addr
    ; Guardar valor original
    PUSH_QWORD reg
    
    ; Duplicar
    DOUBLE reg
    
    ; Imprimir
    PRINT_REG reg, output_addr
    
    ; Restaurar valor original
    POP_QWORD reg
.endmacro
