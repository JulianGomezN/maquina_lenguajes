; ============================================
; BIBLIOTECA: STACK.ASM
; Operaciones de Pila
; ============================================

; Constantes de pila
#define STACK_SIZE 16384    ; 16KB stack (0x4000)
#define STACK_BASE 0x1C000  ; Stack base for layout where code ends at 0xFFFF

; Macros de pila para diferentes tamaños
.macro PUSH_BYTE reg
    PUSH1 reg
.endmacro

.macro POP_BYTE reg
    POP1 reg
.endmacro

.macro PUSH_WORD reg
    PUSH2 reg
.endmacro

.macro POP_WORD reg
    POP2 reg
.endmacro

.macro PUSH_DWORD reg
    PUSH4 reg
.endmacro

.macro POP_DWORD reg
    POP4 reg
.endmacro

.macro PUSH_QWORD reg
    PUSH8 reg
.endmacro

.macro POP_QWORD reg
    POP8 reg
.endmacro
