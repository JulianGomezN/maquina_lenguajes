; Algoritmo del Módulo para GUI
; Calcula a % b = a - (a/b)*b
; Entrada: posición 500 (a), posición 501 (b)
; Salida: posición 502 (a % b)

; Cargar datos de prueba
LOADV R1, 17
STOREV R1, 500      ; a = 17
LOADV R1, 5
STOREV R1, 501      ; b = 5

; Algoritmo del módulo
LOAD R1, 500        ; Cargar dividendo (a)
LOAD R2, 501        ; Cargar divisor (b)

CLEAR R3
ADD R3, R1          ; R3 = dividendo

DIV R3, R2          ; R3 = a / b (cociente entero)
MUL R3, R2          ; R3 = (a/b) * b
SUB R1, R3          ; R1 = a - (a/b)*b = a % b

STOREV R1, 502      ; Guardar resultado

; Verificar datos cargados
LOAD R1, 500        ; Mostrar dividendo
SVIO R1, 0x500
SHOWIO 0x500

LOAD R1, 501        ; Mostrar divisor
SVIO R1, 0x501
SHOWIO 0x501

LOAD R1, 502        ; Mostrar resultado
SVIO R1, 0x502
SHOWIO 0x502

PARAR