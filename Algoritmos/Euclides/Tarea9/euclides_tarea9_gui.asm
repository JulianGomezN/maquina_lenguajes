; Algoritmo de Euclides Detallado para GUI
; Calcula MCD usando bucle iterativo
; Entrada: posición 700 (A), posición 701 (B)
; Salida: posición 702 (MCD)

; Cargar datos de prueba
LOADV R1, 1071
STOREV R1, 700      ; A = 1071
LOADV R1, 462
STOREV R1, 701      ; B = 462

; Algoritmo de Euclides
LOAD R1, 700        ; Cargar A
LOAD R2, 701        ; Cargar B

EUCLIDES:
CLEAR R0            ; R0 = 0
CMP R2, R0          ; Comparar B con 0
JEQ FIN_GCD         ; Si B == 0, terminar

; Calcular A % B
CLEAR R3
ADD R3, R1          ; R3 = A
DIV R3, R2          ; R3 = A / B
MUL R3, R2          ; R3 = (A/B) * B
SUB R1, R3          ; R1 = A % B

; Intercambiar: A = B, B = resto
CLEAR R3
ADD R3, R1          ; R3 = resto
CLEAR R1
ADD R1, R2          ; R1 = B (nuevo A)
CLEAR R2
ADD R2, R3          ; R2 = resto (nuevo B)

JMP EUCLIDES

FIN_GCD:
STOREV R1, 702      ; Guardar MCD

; Verificar datos
LOAD R1, 700        ; Mostrar A original
SVIO R1, 0x700
SHOWIO 0x700

LOAD R1, 701        ; Mostrar B original
SVIO R1, 0x701
SHOWIO 0x701

LOAD R1, 702        ; Mostrar MCD
SVIO R1, 0x702
SHOWIO 0x702

PARAR