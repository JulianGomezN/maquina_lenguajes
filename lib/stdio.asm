; EJEMPLO DE USO lee cadena y la imprime 
EJEMPLO_STDIO
MOVV8 R2, 1000
CALL INPUT_STRING
CALL PRINT_STRING
PARAR

; INPUT ----------------------------------------------------------------------------
;
; leer cadena y ponerla en memoria
; R2 apunta a donde empieza la cadena
; termina hasta encontrar 0 (NULL)
INPUT_STRING:
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

; ----------------------------------------------------
; INPUT_INT: Leer una cadena numérica y convertirla a entero
; Entrada:
;   R2 = puntero al buffer donde guardar la entrada
; Salida:
;   R1 = entero leído
; ----------------------------------------------------

INPUT_INT:
    PUSH8 R2
    PUSH8 R3
    PUSH8 R4
    PUSH8 R5
    PUSH8 R6      ; R6 será el flag de signo

    ; Leer texto a buffer[R2]
    CALL INPUT_STRING

    LOADV R1, 0       ; acumulador
    LOADV R6, 1       ; signo = +1

    ; Revisar primer carácter
    LOADR1 R3, R2
    CMPV R3, 45       ; '-' ?
    JNE CHECK_PLUS

    ; es negativo
    LOADV R6, -1
    ADDV R2, 1        ; avanzar al siguiente carácter
    JMP START_PARSE

CHECK_PLUS:
    CMPV R3, 43       ; '+' ?
    JNE START_PARSE
    ADDV R2, 1        ; saltar '+' si existe

START_PARSE:
CONVERT_LOOP:
    LOADR1 R3, R2
    CMPV R3, 0
    JEQ APPLY_SIGN

    ; ASCII → dígito
    SUBV R3, 48

    ; R1 = R1 * 10
    MOV8 R4, R1
    MOVV8 R5, 10
    MUL R4, R5
    MOV8 R1, R4

    ; R1 += dígito
    ADD R1, R3

    ADDV R2, 1
    JMP CONVERT_LOOP

APPLY_SIGN:
    ; si R6 == -1, entonces R1 = -R1
    CMPV R6, -1
    JNE END_INPUT_INT

    ; R1 = -R1
    MOVV8 R4, 0
    SUB R4, R1
    MOV8 R1, R4

END_INPUT_INT:
    POP8 R6
    POP8 R5
    POP8 R4
    POP8 R3
    POP8 R2
    RET

; OUTPUT -----------------------------------------------------------------------------
; imprimir cadena
; R1 apunta a donde empieza
; termina hasta encontrar 0 (NULL)

PRINT_STRING:
    PUSH8 R1
    PUSH8 R2

PRINT_NEXT_CHAR:
    LOADR1 R1 R2 ; R1 = mem[R2]
    CMPV R1 0
    JEQ FIN_PRINT_STRING
    SVIO R1 0x100
    ADDV R2, 1
    JMP PRINT_NEXT_CHAR

FIN_PRINT_STRING:
    POP8 R2
    POP8 R1
    RET



; PRINT_INT: imprime un entero decimal positivo
; Entrada: entero en R1
; Salida: imprime ascii por SVIO 0x100

PRINT_INT:
    PUSH R1 ; guardad argumento

    ; poner terminador en la pila
    MOVV1 R2 0
    PUSH1 R2

NEXT_DIGIT:
    MOVV8 R4 10      ; divisor = 10

    MOV8 R3 R1       ; R3 = copia de R1
    MOD R3 R4        ; R3 = R1 % 10
    ADDV R3 48       ; convertir a ascii '0'..'9'
    PUSH1 R3         ; guardar ascii en la pila

    DIV R1 R4        ; R1 = R1 / 10

    CMPV R1 0
    JNE NEXT_DIGIT

FIN_PRINT_INT:
    POP1 R3          ; obtener un caracter
    SVIO R3 0x100    ; imprimirlo
    CMPV R3 0        ; era el terminador?
    JNE FIN_PRINT_INT
    POP1 R3          ;quitar terminador de pila
    POP R1           ;restaurar argumento
    RET