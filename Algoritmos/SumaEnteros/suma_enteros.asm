; Programa de ejemplo - suma de los primeros 5 enteros

LOADV R1, 5      ; n = 5
CLEAR R2         ; acumulador = 0

LOOP:
ADD R2, R1       ; acumulador += n
DEC R1           ; n--
CMPV R1, 0       ; comparar n con 0
JNE LOOP         ; si n != 0, saltar al loop

; Mostrar resultado
SVIO R2, 0x30    ; guardar resultado en IO[0x30]  
SHOWIO 0x30      ; mostrar resultado
PARAR            ; terminar programa