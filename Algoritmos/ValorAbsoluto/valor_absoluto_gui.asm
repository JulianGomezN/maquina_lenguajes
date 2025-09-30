; Algoritmo de Valor Absoluto para GUI - Versión Extendida
; Calcula |x| usando comparación y complemento a 2
; Prueba tanto números negativos como positivos
; Entrada: posición 600 (x)
; Salida: posición 601 (|x|)

; ===== CASO 1: NÚMERO NEGATIVO (-7) =====
; Construir -7 = NOT(7) + 1 (complemento a 2 de 7)
LOADV R1, 7         ; Cargar 7
NOT R1              ; Invertir bits
INC R1              ; Incrementar para obtener -7
STOREV R1, 600      ; x = -7

; Mostrar el número original (antes del valor absoluto)
LOAD R1, 600        ; Cargar el número negativo
SVIO R1, 1500       ; Guardar en I/O para mostrar
SHOWIO 1500         ; Mostrar número original (-7)

; Algoritmo de valor absoluto
LOAD R1, 600        ; Cargar número
CLEAR R0            ; R0 = 0  
CMP R1, R0          ; Comparar R1 con 0, esto establece flag N si R1 < 0

JMI NEGATIVE1       ; Si es negativo (N=1), ir a NEGATIVE1
JMP END1            ; Si es positivo o cero, saltar al final

NEGATIVE1:
; Si es negativo, hacer complemento a 2
NOT R1              ; Invertir bits
INC R1              ; Incrementar en 1

END1:
STOREV R1, 601      ; Guardar resultado
SVIO R1, 1501       ; Mostrar resultado del valor absoluto
SHOWIO 1501         ; Mostrar |-7| = 7

; ===== CASO 2: NÚMERO POSITIVO (15) =====
LOADV R1, 15        ; Cargar número positivo 15
STOREV R1, 602      ; x = 15

; Mostrar el número original
LOAD R1, 602        ; Cargar el número positivo
SVIO R1, 1502       ; Guardar en I/O para mostrar
SHOWIO 1502         ; Mostrar número original (15)

; Algoritmo de valor absoluto
LOAD R1, 602        ; Cargar número
CLEAR R0            ; R0 = 0  
CMP R1, R0          ; Comparar R1 con 0

JMI NEGATIVE2       ; Si es negativo, ir a NEGATIVE2
JMP END2            ; Si es positivo o cero, saltar al final

NEGATIVE2:
; Si es negativo, hacer complemento a 2
NOT R1              ; Invertir bits
INC R1              ; Incrementar en 1

END2:
STOREV R1, 603      ; Guardar resultado
SVIO R1, 1503       ; Mostrar resultado del valor absoluto
SHOWIO 1503         ; Mostrar |15| = 15

; ===== CASO 3: CERO =====
LOADV R1, 0         ; Cargar cero
STOREV R1, 604      ; x = 0

; Mostrar el número original
LOAD R1, 604        ; Cargar cero
SVIO R1, 1504       ; Guardar en I/O para mostrar
SHOWIO 1504         ; Mostrar número original (0)

; Algoritmo de valor absoluto
LOAD R1, 604        ; Cargar número
CLEAR R0            ; R0 = 0  
CMP R1, R0          ; Comparar R1 con 0

JMI NEGATIVE3       ; Si es negativo, ir a NEGATIVE3
JMP END3            ; Si es positivo o cero, saltar al final

NEGATIVE3:
; Si es negativo, hacer complemento a 2
NOT R1              ; Invertir bits
INC R1              ; Incrementar en 1

END3:
STOREV R1, 605      ; Guardar resultado
SVIO R1, 1505       ; Mostrar resultado del valor absoluto
SHOWIO 1505         ; Mostrar |0| = 0

PARAR