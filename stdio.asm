MOVV8 R2, 1000
CALL READ_CHAR_LINE
CALL PRINT_CHAR_LINE
PARAR

; leer cadena y ponerla en memoria

READ_CHAR_LINE:
    PUSH8 R1
    PUSH8 R2
    PUSH8 R3

WAIT_INPUT:
    LOADIO R3 0x200
    CMPV R3 0xFF
    JEQ WAIT_INPUT    ; esperar carácter valido

    CMPV R3 0
    JEQ FIN_INPUT_LINE     ; caracter null

    STORER1 R3, R2         ; buffer[i] = char
    ADDV R2 1
    JMP WAIT_INPUT

FIN_INPUT_LINE:
    LOADV R3, 0
    STORER1 R3, R2          ; terminar cadena
    POP8 R3
    POP8 R2
    POP8 R1
    RET


; imprimir cadena
; R1 apunta a donde empieza

PRINT_CHAR_LINE:
    PUSH8 R1
    PUSH8 R2

PRINT_NEXT_CHAR:
    LOADR1 R1 R2 ; R1 = mem[R2]
    CMPV R1 0
    JEQ FIN_PRINT_CHAR_LINE
    SVIO R1 0x100
    ADDV R2, 1
    JMP PRINT_NEXT_CHAR

FIN_PRINT_CHAR_LINE:
    POP8 R2
    POP8 R1
    RET