; DEMOSTRACIÓN: Algoritmo de Valor Absoluto
; Muestra cómo se ve un número negativo en representación sin signo
; y cómo el algoritmo calcula el valor absoluto correctamente

; ===== INFORMACIÓN PARA EL USUARIO =====
; Los números se muestran en la GUI como valores sin signo de 64 bits
; Un número negativo como -7 se ve como: 18446744073709551609
; Esto es normal en representación complemento a 2

; ===== EJEMPLO 1: NÚMERO NEGATIVO (-7) =====
; Construir -7 usando complemento a 2
LOADV R1, 7         ; Cargar 7
NOT R1              ; Invertir todos los bits
INC R1              ; Sumar 1 para completar el complemento a 2
STOREV R1, 600      ; Guardar -7 en posición 600

; Mostrar el número negativo (se verá como número muy grande)
LOAD R1, 600        
SVIO R1, 2000       ; I/O[2000] = número original (-7)
SHOWIO 2000         ; Mostrar: 18446744073709551609 (esto es -7 en uint64)

; Calcular valor absoluto
LOAD R1, 600        ; Cargar el número
CLEAR R0            ; R0 = 0
CMP R1, R0          ; Comparar con 0 (establece flags)
JMI ES_NEGATIVO1    ; Si N=1, es negativo
JMP GUARDAR1        ; Si no es negativo, ya está listo

ES_NEGATIVO1:
NOT R1              ; Invertir bits
INC R1              ; Sumar 1 (complemento a 2)

GUARDAR1:
STOREV R1, 601      ; Guardar resultado
SVIO R1, 2001       ; I/O[2001] = valor absoluto
SHOWIO 2001         ; Mostrar: 7

; ===== EJEMPLO 2: NÚMERO POSITIVO (25) =====
LOADV R1, 25        ; Cargar número positivo
STOREV R1, 602      ; Guardar en posición 602

; Mostrar el número positivo
LOAD R1, 602        
SVIO R1, 2002       ; I/O[2002] = número original (25)
SHOWIO 2002         ; Mostrar: 25

; Calcular valor absoluto
LOAD R1, 602        ; Cargar el número
CLEAR R0            ; R0 = 0
CMP R1, R0          ; Comparar con 0
JMI ES_NEGATIVO2    ; Si N=1, es negativo
JMP GUARDAR2        ; Si no es negativo, ya está listo

ES_NEGATIVO2:
NOT R1              ; Invertir bits
INC R1              ; Sumar 1

GUARDAR2:
STOREV R1, 603      ; Guardar resultado
SVIO R1, 2003       ; I/O[2003] = valor absoluto
SHOWIO 2003         ; Mostrar: 25 (sin cambios)

; ===== EJEMPLO 3: NÚMERO MÁS NEGATIVO (-100) =====
; Construir -100 usando complemento a 2
LOADV R1, 100       ; Cargar 100
NOT R1              ; Invertir bits
INC R1              ; Completar complemento a 2
STOREV R1, 604      ; Guardar -100

; Mostrar el número negativo
LOAD R1, 604        
SVIO R1, 2004       ; I/O[2004] = -100 (se verá como número grande)
SHOWIO 2004         

; Calcular valor absoluto
LOAD R1, 604        
CLEAR R0            
CMP R1, R0          
JMI ES_NEGATIVO3    
JMP GUARDAR3        

ES_NEGATIVO3:
NOT R1              
INC R1              

GUARDAR3:
STOREV R1, 605      
SVIO R1, 2005       ; I/O[2005] = 100
SHOWIO 2005         

PARAR

; ===== EXPLICACIÓN DE LOS RESULTADOS =====
; I/O[2000]: Número muy grande → Esto es -7 en complemento a 2
; I/O[2001]: 7 → Valor absoluto de -7
; I/O[2002]: 25 → Número positivo (sin cambios)
; I/O[2003]: 25 → Valor absoluto de 25 (igual al original)
; I/O[2004]: Número muy grande → Esto es -100 en complemento a 2
; I/O[2005]: 100 → Valor absoluto de -100