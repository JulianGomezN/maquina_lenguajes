; ============================================================================
; BIBLIOTECA STDIO - Entrada/Salida Estándar
; ============================================================================

; INPUT ----------------------------------------------------------------------------
;
; leer cadena y ponerla en memoria
; R2 apunta a donde empieza la cadena
; termina hasta encontrar 0 (NULL)
INPUT_STRING:
    PUSH8 R01
    PUSH8 R02
    PUSH8 R03

WAIT_INPUT:
    LOADIO R03, 0x200
    CMPV R03, 0xFF
    JEQ WAIT_INPUT    ; esperar carácter valido

    CMPV R03, 0
    JEQ FIN_INPUT_LINE     ; caracter null

    STORER1 R03, R02         ; buffer[i] = char
    ADDV8 R02, 1
    JMP WAIT_INPUT

FIN_INPUT_LINE:
    MOVV8 R03, 0
    STORER1 R03, R02          ; terminar cadena
    POP8 R03
    POP8 R02
    POP8 R01
    RET

; ----------------------------------------------------
; INPUT_INT: Leer una cadena numérica y convertirla a entero
; Entrada:
;   R2 = puntero al buffer donde guardar la entrada
; Salida:
;   R1 = entero leído
; ----------------------------------------------------

INPUT_INT:
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04
    PUSH8 R05
    PUSH8 R06      ; R06 será el flag de signo

    ; Leer texto a buffer[R02]
    CALL INPUT_STRING

    MOVV8 R01, 0       ; acumulador
    MOVV8 R06, 1       ; signo = +1

    ; Revisar primer carácter
    LOADR1 R03, R02
    CMPV R03, 45       ; '-' ?
    JNE CHECK_PLUS

    ; es negativo
    MOVV8 R06, -1
    ADDV8 R02, 1        ; avanzar al siguiente carácter
    JMP START_PARSE

CHECK_PLUS:
    CMPV R03, 43       ; '+' ?
    JNE START_PARSE
    ADDV8 R02, 1        ; saltar '+' si existe

START_PARSE:
CONVERT_LOOP:
    LOADR1 R03, R02
    CMPV R03, 0
    JEQ APPLY_SIGN

    ; ASCII → dígito
    SUBV8 R03, 48

    ; R01 = R01 * 10
    MOV8 R04, R01
    MOVV8 R05, 10
    MUL8 R04, R05
    MOV8 R01, R04

    ; R01 += dígito
    ADD8 R01, R03

    ADDV8 R02, 1
    JMP CONVERT_LOOP

APPLY_SIGN:
    ; si R06 == -1, entonces R01 = -R01
    CMPV R06, -1
    JNE END_INPUT_INT

    ; R01 = -R01
    MOVV8 R04, 0
    SUB8 R04, R01
    MOV8 R01, R04

END_INPUT_INT:
    POP8 R06
    POP8 R05
    POP8 R04
    POP8 R03
    POP8 R02
    RET

; OUTPUT -----------------------------------------------------------------------------

; PRINT_STRING: Imprime una cadena terminada en NULL
; Entrada: R2 = puntero a la cadena
; Salida: imprime por SVIO 0x100
PRINT_STRING:
    PUSH8 R01
    PUSH8 R02

PRINT_NEXT_CHAR:
    LOADR1 R01, R02 ; R01 = mem[R02]
    CMPV R01, 0
    JEQ FIN_PRINT_STRING
    SVIO R01, 0x100
    SHOWIO 0x100
    ADDV8 R02, 1
    JMP PRINT_NEXT_CHAR

FIN_PRINT_STRING:
    POP8 R02
    POP8 R01
    RET

; PRINT_INT: Imprime un entero decimal positivo
; Entrada: R1 = entero sin signo
; Salida: imprime dígitos por SVIO 0x100
PRINT_INT:
    PUSH8 R01             ; Guardar argumento
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04

    ; Caso especial: si R01 == 0, imprimir '0' directamente
    CMPV R01, 0
    JNE PRINT_INT_DIGITS
    MOVV1 R03, 48        ; ASCII '0'
    SVIO R03, 0x100
    SHOWIO 0x100
    JMP PRINT_INT_END

PRINT_INT_DIGITS:
    MOVV1 R02, 0
    PUSH1 R02            ; Terminador en pila

NEXT_DIGIT:
    MOVV8 R04, 10        ; Divisor = 10
    MOV8 R03, R01         ; R03 = copia de R01
    MOD8 R03, R04         ; R03 = R01 % 10
    ADDV8 R03, 48        ; Convertir a ASCII '0'..'9'
    PUSH1 R03            ; Guardar en pila
    DIV8 R01, R04         ; R01 = R01 / 10
    CMPV R01, 0
    JNE NEXT_DIGIT      ; Repetir si R01 != 0

FIN_PRINT_INT:
    POP1 R03             ; Obtener carácter
    CMPV R03, 0          ; ¿Era terminador?
    JEQ PRINT_INT_END   ; Si es terminador, terminar
    SVIO R03, 0x100      ; Imprimir
    SHOWIO 0x100
    JMP FIN_PRINT_INT   ; Repetir

PRINT_INT_END:
    POP8 R04
    POP8 R03
    POP8 R02
    POP8 R01              ; Restaurar argumento
    RET

; ============================================================================
; FUNCIONES DE SOPORTE PARA imprimir()
; ============================================================================

; __print_int8: Imprime un entero de 64 bits (con signo)
; Entrada: valor en el tope de la pila
; Salida: imprime el valor y un espacio
__print_int8:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP
    
    ; CRÍTICO: Cargar argumento ANTES de guardar registros
    ; Stack: [argumento] [ret_addr 8B] [BP_old 8B] <- BP apunta después de todo
    ; Argumento está 24 bytes debajo de BP (8B por BP_old + 8B por ret_addr + 8B del argumento mismo)
    MOV8 R03, R14       ; R03 = BP
    SUBV8 R03, 24       ; R03 = BP - 24 para llegar al inicio del argumento
    LOADR8 R01, R03     ; R01 = argumento
    
    PUSH8 R01           ; Ahora guardar registros
    PUSH8 R02
    PUSH8 R03
    
    ; Verificar si es negativo
    CMPV R01, 0
    JGE __print_int8_positive
    
    ; Es negativo: imprimir '-' y convertir a positivo
    MOVV1 R02, 45       ; ASCII '-'
    SVIO R02, 0x100
    SHOWIO 0x100
    ; Negar: R01 = 0 - R01
    PUSH8 R04
    MOVV8 R04, 0
    SUB8 R04, R01
    MOV8 R01, R04
    POP8 R04
    
__print_int8_positive:
    CALL PRINT_INT      ; Imprimir el número

    ; Imprimir espacio
    MOVV1 R02, 32       ; ASCII ' '
    SVIO R02, 0x100
    SHOWIO 0x100

    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_string: Imprime una cadena (puntero)
; Entrada: puntero en el tope de la pila
; Salida: imprime la cadena y un espacio
__print_string:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP
    
    ; Cargar argumento ANTES de guardar registros
    ; Stack: [arg, ret_addr, old_BP] <- BP después de PUSH8 R14
    ; arg está en BP - 24
    MOV8 R03, R14       ; R03 = BP
    SUBV8 R03, 24       ; R03 = BP - 24
    LOADR8 R02, R03     ; R02 = puntero al string
    
    ; Guardar registros
    PUSH8 R02
    PUSH8 R03
    
    ; Llamar PRINT_STRING con R02 = puntero
    CALL PRINT_STRING
    
    ; Imprimir espacio
    MOVV1 R02, 32       ; ASCII ' '
    SVIO R02, 0x100
    SHOWIO 0x100

    ; Restaurar registros
    POP8 R03
    POP8 R02
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_char: Imprime un carácter
; Entrada: carácter en el tope de la pila
; Salida: imprime el carácter y un espacio
__print_char:
    PUSH8 R14           ; Guardar BP
    MOV8 R14, R15       ; BP = SP
    
    ; CRÍTICO: Cargar carácter ANTES de guardar registros
    ; Argumento en BP-24
    MOV8 R02, R14       ; R02 = BP
    SUBV8 R02, 24       ; R02 = BP - 24
    LOADR8 R01, R02     ; R01 = carácter
    
    PUSH8 R01           ; Ahora guardar registros
    PUSH8 R02    SVIO R01, 0x100     ; Imprimir
    SHOWIO 0x100        ; Imprimir espacio

    MOVV1 R01, 32       ; ASCII ' '
    SVIO R01, 0x100
    SHOWIO 0x100
    
    POP8 R02
    POP8 R01
    MOV8 R15, R14       ; SP = BP
    POP8 R14            ; Restaurar BP
    RET

; __print_float: Imprime un valor flotante con 2 decimales
; Argumento en stack: flotante de 32 bits (4 bytes)
__print_float:
    PUSH8 R14
    MOV8 R14, R15

    ; Cargar el flotante desde el stack (argumento en BP-20: 8B ret + 8B BP + 4B arg)
    MOV8 R03, R14
    SUBV8 R03, 20
    LOADR4 R01, R03     ; R01 = valor flotante (4 bytes)    PUSH8 R01
    PUSH8 R02
    PUSH8 R03
    PUSH8 R04
    PUSH8 R05

    ; Convertir flotante a entero (parte entera)
    CVTF2I4 R02, R01    ; R02 = int(R01)    ; Guardar signo
    MOVV4 R05, 0
    CMP4 R02, R05
    JGE __print_float_positive_int

    ; Si es negativo, imprimir '-' y convertir a positivo
    MOVV1 R04, 45       ; ASCII '-'
    SVIO R04, 0x100
    SHOWIO 0x100

    ; Negar el entero
    MOVV4 R04, 0
    SUB4 R04, R02
    MOV4 R02, R04

    ; También negar el flotante original para decimales
    MOVV4 R04, 0
    CVTI2F4 R04, R04    ; Convertir 0 a flotante
    FSUB4 R04, R01      ; R04 = 0.0 - R01
    MOV4 R01, R04

__print_float_positive_int:
    ; Guardar el flotante original en R06 antes de imprimir el entero
    PUSH8 R06
    MOV4 R06, R01       ; R06 = flotante original
    
    ; Imprimir parte entera
    MOV8 R01, R02
    CALL PRINT_INT
    
    ; Imprimir punto decimal
    MOVV1 R01, 46       ; ASCII '.'
    SVIO R01, 0x100
    SHOWIO 0x100
    
    ; Restaurar el flotante original desde R06
    MOV4 R01, R06
    POP8 R06
    
    ; Obtener parte decimal: (float - int(float)) * 100
    CVTF2I4 R02, R01    ; R02 = int(R01)
    CVTI2F4 R03, R02    ; R03 = float(int(R01))
    FSUB4 R01, R03      ; R01 = R01 - R03 (parte decimal)

    ; Multiplicar por 100
    MOVV4 R02, 100
    CVTI2F4 R02, R02    ; Convertir 100 a flotante
    FMUL4 R01, R02      ; R01 = parte_decimal * 100

    ; Convertir a entero
    CVTF2I4 R01, R01    ; R01 = int(parte_decimal * 100)    ; Asegurar que sea positivo
    MOVV4 R03, 0
    CMP4 R01, R03
    JGE __print_float_decimal_positive
    MOVV4 R03, 0
    SUB4 R03, R01
    MOV4 R01, R03
    
__print_float_decimal_positive:
    ; Imprimir primer dígito
    MOV4 R02, R01
    MOVV4 R03, 10
    DIV4 R02, R03
    ADDV4 R02, 48       ; Convertir a ASCII
    SVIO R02, 0x100
    SHOWIO 0x100

    ; Imprimir segundo dígito
    MOVV4 R03, 10
    MOD4 R01, R03
    ADDV4 R01, 48       ; Convertir a ASCII
    SVIO R01, 0x100
    SHOWIO 0x100
    
    ; Imprimir espacio
    MOVV1 R01, 32
    SVIO R01, 0x100
    SHOWIO 0x100
    
    POP8 R04
    POP8 R03
    POP8 R02
    POP8 R01
    MOV8 R15, R14
    POP8 R14
    RET

; __print_newline: Imprime un salto de línea
; Sin argumentos
__print_newline:
    PUSH8 R01
    MOVV1 R01, 10       ; ASCII '\n'
    SVIO R01, 0x100
    SHOWIO 0x100
    POP8 R01
    RET