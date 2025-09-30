# Simulador de Computador - Atlas

Este proyecto simula un computador completo con CPU, memoria y controlador de disco, junto con una interfaz gráfica para interactuar con el sistema.

## Arquitectura del Sistema

### Componentes principales:

1. **CPU.py** - Procesador principal que:
   - Ejecuta instrucciones de 64 bits
   - Maneja 16 registros de propósito general (R00-R15)
   - Implementa flags de estado (Z, N, C, V)
   - Soporta operaciones aritméticas, lógicas, de memoria y saltos
   - Incluye sistema de I/O mapeado

2. **disco_64bits.py** - Sistema de memoria que:
   - Maneja 16 registros de 4 bits
   - Proporciona 65536 celdas de memoria de 64 bits cada una
   - Permite lectura/escritura con formato de string binario

3. **assembler.py** - Ensamblador que:
   - Traduce código assembly a instrucciones binarias de 64 bits
   - Soporta etiquetas y comentarios
   - Maneja múltiples formatos de instrucción (OP, R, RR, RI, I)

4. **GUI/main.py** - Interfaz gráfica que:
   - Permite cargar y ejecutar programas
   - Muestra el estado de registros y flags en tiempo real
   - Visualiza la traducción assembly-binario
   - Permite ejecución automática o paso a paso

## Instrucciones Soportadas

### Control

- `PARAR` - Termina la ejecución
- `NOP` - No operación

### Aritmética

- `ADD Rd, Rs` - Suma Rd = Rd + Rs
- `SUB Rd, Rs` - Resta Rd = Rd - Rs
- `MUL Rd, Rs` - Multiplicación sin signo
- `MULS Rd, Rs` - Multiplicación con signo
- `DIV Rd, Rs` - División
- `ADDV Rd, imm` - Suma con valor inmediato
- `SUBV Rd, imm` - Resta con valor inmediato
- `INC Rd` - Incrementa registro
- `DEC Rd` - Decrementa registro

### Lógicas

- `AND Rd, Rs` - AND lógico
- `OR Rd, Rs` - OR lógico
- `XOR Rd, Rs` - XOR lógico
- `NOT Rd` - NOT lógico
- `ANDV Rd, imm` - AND con valor inmediato
- `ORV Rd, imm` - OR con valor inmediato
- `XORV Rd, imm` - XOR con valor inmediato

### Desplazamientos

- `SHL Rd` - Shift left lógico
- `SHR Rd` - Shift right lógico
- `SAL Rd` - Shift left aritmético
- `SAR Rd` - Shift right aritmético

### Memoria

- `LOAD Rd, Rs` - Cargar desde memoria
- `LOADV Rd, imm` - Cargar valor inmediato
- `STORE Rd, Rs` - Almacenar en memoria
- `STOREV Rd, imm` - Almacenar en dirección inmediata
- `CLEAR Rd` - Limpiar registro

### Comparación

- `CMP Rd, Rs` - Comparar registros
- `CMPV Rd, imm` - Comparar con valor inmediato

### Saltos

- `JMP addr` - Salto incondicional
- `JEQ addr` - Salto si igual (Z=1)
- `JNE addr` - Salto si no igual (Z=0)
- `JLT addr` - Salto si menor (N=1)
- `JGE addr` - Salto si mayor o igual (N=0)

### I/O

- `SVIO Rd, addr` - Guardar registro en I/O
- `LOADIO Rd, addr` - Cargar desde I/O
- `SHOWIO addr` - Mostrar valor de I/O
- `CLRIO` - Limpiar I/O
- `RESETIO` - Resetear I/O

## Cómo Usar el Simulador

### Opción 1: Interfaz Gráfica

```bash
cd GUI
python main.py
```

La interfaz tiene las siguientes secciones:

- **Cargar programa**: Área de texto para escribir código assembly
- **Traducción**: Muestra el código ensamblado en binario
- **Banderas y Contador**: Estado actual del CPU
- **Registros**: Valores de R00-R15
- **Salida**: Resultados de la ejecución

### Opción 2: Modo Consola

```python
from CPU import CPU
from assembler import Assembler

cpu = CPU()
assembler = Assembler()

# Código de ejemplo
programa = """
LOADV R1, 5
CLEAR R2
LOOP:
ADD R2, R1
DEC R1
CMPV R1, 0
JNE LOOP
SVIO R2, 0x30
SHOWIO 0x30
PARAR
"""

# Ensamblar y ejecutar
codigo = assembler.assemble(programa)
cpu.load_program(codigo)
cpu.run()
```

## Ejemplos de Programas

### Ejemplo 1: Suma de los primeros N números

```assembly
; Suma de los primeros 5 números
LOADV R1, 5      ; n = 5
CLEAR R2         ; acumulador = 0

LOOP:
ADD R2, R1       ; acumulador += n
DEC R1           ; n--
CMPV R1, 0       ; comparar n con 0
JNE LOOP         ; si n != 0, repetir

SVIO R2, 0x30    ; guardar resultado
SHOWIO 0x30      ; mostrar resultado
PARAR
```

### Ejemplo 2: Factorial

```assembly
; Factorial de 4
LOADV R1, 4      ; n = 4
LOADV R2, 1      ; factorial = 1

FACTORIAL_LOOP:
CMPV R1, 0       ; comparar n con 0
JEQ FIN          ; si n == 0, terminar

MUL R2, R1       ; factorial *= n
DEC R1           ; n--
JMP FACTORIAL_LOOP

FIN:
SVIO R2, 0x100   ; guardar resultado
SHOWIO 0x100     ; mostrar resultado
PARAR
```

## Arquitectura de Instrucciones

Las instrucciones tienen 64 bits con los siguientes formatos:

- **OP**: Solo opcode (16 bits altos)
- **R**: Opcode + registro (Rd en bits 44-47)
- **RR**: Opcode + dos registros (Rd en bits 4-7, Rs en bits 0-3)
- **RI**: Opcode + registro + inmediato (Rd en bits 44-47, imm en bits 0-43)
- **I**: Opcode + inmediato (imm en bits 0-43)

## Integración de Componentes

El sistema está completamente integrado:

1. **assembler.py** traduce código assembly a binario
2. **CPU.py** ejecuta las instrucciones binarias
3. **disco_64bits.py** proporciona almacenamiento adicional
4. **GUI/main.py** conecta todo en una interfaz visual

La GUI actualiza automáticamente:

- Estado de registros después de cada operación
- Flags del procesador
- Contador de programa (PC)
- Salida del programa en tiempo real

## Testing

Ejecuta el script de pruebas para verificar la integración:

```bash
python test_integration.py
```

## Requisitos

- Python 3.6+
- tkinter (incluido con Python)
- typing (incluido con Python 3.5+)

## Notas Técnicas

- Las instrucciones son de 64 bits en formato little-endian
- Los registros pueden almacenar valores de 64 bits
- El sistema de flags incluye Zero, Negative, Carry y Overflow
- El I/O está mapeado en memoria con direcciones específicas
- El contador de programa (PC) se incrementa automáticamente por instrucciones de 8 bytes
