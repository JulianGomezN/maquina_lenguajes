; ============================================
; BIBLIOTECA: STACK.ASM
; Operaciones de Pila
; ============================================

; Constantes de pila
#define STACK_SIZE 256
#define STACK_BASE 0x1000

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
