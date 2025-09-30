; Algoritmo de Euclides del profesor Peña (versión iterativa exacta)
; Libro: "De Euclides a Java"
; Especificaciones del profesor:
; - Operando A en posición 375
; - Operando B en posición 1535  
; - Resultado en posición 7478
; - Programa en posición 2500

; Cargar operandos a₀ y b₀
LOADV R1, 1071      ; a₀ = 1071
STOREV R1, 375      ; Guardar en posición 375

LOADV R2, 462       ; b₀ = 462
STOREV R2, 1535     ; Guardar en posición 1535

; Inicializar variables: a := a₀; b := b₀
LOAD R1, 375        ; R1 = a = a₀
LOAD R2, 1535       ; R2 = b = b₀

; mientras a ≠ b hacer
MIENTRAS:
CMP R1, R2          ; Comparar a con b
JEQ FIN_MIENTRAS    ; Si a = b, salir del bucle

; caso a > b → a := a - b
CMP R1, R2          ; Comparar a con b
JLT CASO_B_MAYOR    ; Si a < b, ir a caso b > a
SUB R1, R2          ; a := a - b (caso a > b)
JMP MIENTRAS        ; Volver al inicio del bucle

; [] a < b → b := b - a  
CASO_B_MAYOR:
SUB R2, R1          ; b := b - a
JMP MIENTRAS        ; Volver al inicio del bucle

; fmientras
FIN_MIENTRAS:
; dev a (el resultado está en R1)
STOREV R1, 7478     ; Guardar resultado en posición 7478

; Mostrar resultado por dispositivo de salida
LOAD R15, 7478
SVIO R15, 7478
SHOWIO 7478

PARAR