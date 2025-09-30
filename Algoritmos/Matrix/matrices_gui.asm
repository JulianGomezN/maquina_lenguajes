; Multiplicación de Matrices 3x2 × 2x4 para GUI
; Especificaciones DEL PROFESOR (obligatorias):
; - Matrices almacenadas a partir de posición 1028
; - Resultado en posición 20455
; - Programa en posición 3700

; Cargar datos de prueba primero
LOADV R1, 1
STOREV R1, 1028     ; A[0][0] = 1
LOADV R1, 2
STOREV R1, 1029     ; A[0][1] = 2
LOADV R1, 3
STOREV R1, 1030     ; A[1][0] = 3
LOADV R1, 4
STOREV R1, 1031     ; A[1][1] = 4
LOADV R1, 5
STOREV R1, 1032     ; A[2][0] = 5
LOADV R1, 6
STOREV R1, 1033     ; A[2][1] = 6

LOADV R1, 7
STOREV R1, 1040     ; B[0][0] = 7
LOADV R1, 8
STOREV R1, 1041     ; B[0][1] = 8
LOADV R1, 9
STOREV R1, 1042     ; B[0][2] = 9
LOADV R1, 10
STOREV R1, 1043     ; B[0][3] = 10
LOADV R1, 11
STOREV R1, 1044     ; B[1][0] = 11
LOADV R1, 12
STOREV R1, 1045     ; B[1][1] = 12
LOADV R1, 13
STOREV R1, 1046     ; B[1][2] = 13
LOADV R1, 14
STOREV R1, 1047     ; B[1][3] = 14

; Calcular primera fila de C (solo como demostración)
; C[0][0] = A[0][0]*B[0][0] + A[0][1]*B[1][0] = 1*7 + 2*11 = 29
LOAD R1, 1028       ; A[0][0] = 1
LOAD R2, 1040       ; B[0][0] = 7
MUL R1, R2          ; R1 = 1*7 = 7
CLEAR R4
ADD R4, R1          ; R4 = 7

LOAD R1, 1029       ; A[0][1] = 2
LOAD R2, 1044       ; B[1][0] = 11
MUL R1, R2          ; R1 = 2*11 = 22
ADD R4, R1          ; R4 = 7+22 = 29
STOREV R4, 20455     ; C[0][0] = 29

; C[0][1] = A[0][0]*B[0][1] + A[0][1]*B[1][1] = 1*8 + 2*12 = 32
LOAD R1, 1028       ; A[0][0] = 1
LOAD R2, 1041       ; B[0][1] = 8
MUL R1, R2          ; R1 = 1*8 = 8
CLEAR R4
ADD R4, R1          ; R4 = 8

LOAD R1, 1029       ; A[0][1] = 2
LOAD R2, 1045       ; B[1][1] = 12
MUL R1, R2          ; R1 = 2*12 = 24
ADD R4, R1          ; R4 = 8+24 = 32
STOREV R4, 20456     ; C[0][1] = 32

; C[0][2] = A[0][0]*B[0][2] + A[0][1]*B[1][2] = 1*9 + 2*13 = 35
LOAD R1, 1028       ; A[0][0] = 1
LOAD R2, 1042       ; B[0][2] = 9
MUL R1, R2          ; R1 = 1*9 = 9
CLEAR R4
ADD R4, R1          ; R4 = 9

LOAD R1, 1029       ; A[0][1] = 2
LOAD R2, 1046       ; B[1][2] = 13
MUL R1, R2          ; R1 = 2*13 = 26
ADD R4, R1          ; R4 = 9+26 = 35
STOREV R4, 20457     ; C[0][2] = 35

; C[0][3] = A[0][0]*B[0][3] + A[0][1]*B[1][3] = 1*10 + 2*14 = 38
LOAD R1, 1028       ; A[0][0] = 1
LOAD R2, 1043       ; B[0][3] = 10
MUL R1, R2          ; R1 = 1*10 = 10
CLEAR R4
ADD R4, R1          ; R4 = 10

LOAD R1, 1029       ; A[0][1] = 2
LOAD R2, 1047       ; B[1][3] = 14
MUL R1, R2          ; R1 = 2*14 = 28
ADD R4, R1          ; R4 = 10+28 = 38
STOREV R4, 20458     ; C[0][3] = 38

; ===== SEGUNDA FILA =====
; C[1][0] = A[1][0]*B[0][0] + A[1][1]*B[1][0] = 3*7 + 4*11 = 65
LOAD R1, 1030       ; A[1][0] = 3
LOAD R2, 1040       ; B[0][0] = 7
MUL R1, R2          ; R1 = 3*7 = 21
CLEAR R4
ADD R4, R1          ; R4 = 21

LOAD R1, 1031       ; A[1][1] = 4
LOAD R2, 1044       ; B[1][0] = 11
MUL R1, R2          ; R1 = 4*11 = 44
ADD R4, R1          ; R4 = 21+44 = 65
STOREV R4, 20459     ; C[1][0] = 65

; C[1][1] = A[1][0]*B[0][1] + A[1][1]*B[1][1] = 3*8 + 4*12 = 72
LOAD R1, 1030       ; A[1][0] = 3
LOAD R2, 1041       ; B[0][1] = 8
MUL R1, R2          ; R1 = 3*8 = 24
CLEAR R4
ADD R4, R1          ; R4 = 24

LOAD R1, 1031       ; A[1][1] = 4
LOAD R2, 1045       ; B[1][1] = 12
MUL R1, R2          ; R1 = 4*12 = 48
ADD R4, R1          ; R4 = 24+48 = 72
STOREV R4, 20460     ; C[1][1] = 72

; C[1][2] = A[1][0]*B[0][2] + A[1][1]*B[1][2] = 3*9 + 4*13 = 79
LOAD R1, 1030       ; A[1][0] = 3
LOAD R2, 1042       ; B[0][2] = 9
MUL R1, R2          ; R1 = 3*9 = 27
CLEAR R4
ADD R4, R1          ; R4 = 27

LOAD R1, 1031       ; A[1][1] = 4
LOAD R2, 1046       ; B[1][2] = 13
MUL R1, R2          ; R1 = 4*13 = 52
ADD R4, R1          ; R4 = 27+52 = 79
STOREV R4, 20461     ; C[1][2] = 79

; C[1][3] = A[1][0]*B[0][3] + A[1][1]*B[1][3] = 3*10 + 4*14 = 86
LOAD R1, 1030       ; A[1][0] = 3
LOAD R2, 1043       ; B[0][3] = 10
MUL R1, R2          ; R1 = 3*10 = 30
CLEAR R4
ADD R4, R1          ; R4 = 30

LOAD R1, 1031       ; A[1][1] = 4
LOAD R2, 1047       ; B[1][3] = 14
MUL R1, R2          ; R1 = 4*14 = 56
ADD R4, R1          ; R4 = 30+56 = 86
STOREV R4, 20462     ; C[1][3] = 86

; ===== TERCERA FILA =====
; C[2][0] = A[2][0]*B[0][0] + A[2][1]*B[1][0] = 5*7 + 6*11 = 101
LOAD R1, 1032       ; A[2][0] = 5
LOAD R2, 1040       ; B[0][0] = 7
MUL R1, R2          ; R1 = 5*7 = 35
CLEAR R4
ADD R4, R1          ; R4 = 35

LOAD R1, 1033       ; A[2][1] = 6
LOAD R2, 1044       ; B[1][0] = 11
MUL R1, R2          ; R1 = 6*11 = 66
ADD R4, R1          ; R4 = 35+66 = 101
STOREV R4, 20463     ; C[2][0] = 101

; C[2][1] = A[2][0]*B[0][1] + A[2][1]*B[1][1] = 5*8 + 6*12 = 112
LOAD R1, 1032       ; A[2][0] = 5
LOAD R2, 1041       ; B[0][1] = 8
MUL R1, R2          ; R1 = 5*8 = 40
CLEAR R4
ADD R4, R1          ; R4 = 40

LOAD R1, 1033       ; A[2][1] = 6
LOAD R2, 1045       ; B[1][1] = 12
MUL R1, R2          ; R1 = 6*12 = 72
ADD R4, R1          ; R4 = 40+72 = 112
STOREV R4, 20464     ; C[2][1] = 112

; C[2][2] = A[2][0]*B[0][2] + A[2][1]*B[1][2] = 5*9 + 6*13 = 123
LOAD R1, 1032       ; A[2][0] = 5
LOAD R2, 1042       ; B[0][2] = 9
MUL R1, R2          ; R1 = 5*9 = 45
CLEAR R4
ADD R4, R1          ; R4 = 45

LOAD R1, 1033       ; A[2][1] = 6
LOAD R2, 1046       ; B[1][2] = 13
MUL R1, R2          ; R1 = 6*13 = 78
ADD R4, R1          ; R4 = 45+78 = 123
STOREV R4, 20465     ; C[2][2] = 123

; C[2][3] = A[2][0]*B[0][3] + A[2][1]*B[1][3] = 5*10 + 6*14 = 134
LOAD R1, 1032       ; A[2][0] = 5
LOAD R2, 1043       ; B[0][3] = 10
MUL R1, R2          ; R1 = 5*10 = 50
CLEAR R4
ADD R4, R1          ; R4 = 50

LOAD R1, 1033       ; A[2][1] = 6
LOAD R2, 1047       ; B[1][3] = 14
MUL R1, R2          ; R1 = 6*14 = 84
ADD R4, R1          ; R4 = 50+84 = 134
STOREV R4, 20466     ; C[2][3] = 134

; Verificar carga de datos en posiciones requeridas
LOAD R1, 1028       ; Verificar matriz A
SVIO R1, 1028       ; Mostrar en I/O usando dirección donde está almacenada
SHOWIO 1028

LOAD R1, 1040       ; Verificar matriz B
SVIO R1, 1040       ; Mostrar en I/O usando dirección donde está almacenada
SHOWIO 1040

; Mostrar resultados de C - FILA 0
LOAD R1, 20455       ; C[0][0]
SVIO R1, 20455       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20455

LOAD R1, 20456       ; C[0][1]
SVIO R1, 20456       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20456

LOAD R1, 20457       ; C[0][2]
SVIO R1, 20457       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20457

LOAD R1, 20458       ; C[0][3]
SVIO R1, 20458       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20458

; Mostrar resultados de C - FILA 1
LOAD R1, 20459       ; C[1][0]
SVIO R1, 20459       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20459

LOAD R1, 20460       ; C[1][1]
SVIO R1, 20460       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20460

LOAD R1, 20461       ; C[1][2]
SVIO R1, 20461       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20461

LOAD R1, 20462       ; C[1][3]
SVIO R1, 20462       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20462

; Mostrar resultados de C - FILA 2
LOAD R1, 20463       ; C[2][0]
SVIO R1, 20463       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20463

LOAD R1, 20464       ; C[2][1]
SVIO R1, 20464       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20464

LOAD R1, 20465       ; C[2][2]
SVIO R1, 20465       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20465

LOAD R1, 20466       ; C[2][3]
SVIO R1, 20466       ; Mostrar en I/O usando dirección donde está almacenado
SHOWIO 20466

PARAR