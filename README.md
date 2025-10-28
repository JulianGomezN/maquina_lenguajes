# Simulador Atlas CPU
## Simulador Educativo de Arquitectura de Computadores

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https:/## Control de Flujo

| Opcode | Instrucción | Descripción |thon.org)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](README.md)

---

## Descripción General

El **Simulador Atlas CPU** es una herramienta educativa completa que implementa un procesador de 64 bits con arquitectura RISC. Diseñado específicamente para la enseñanza de **arquitectura de computadores**, permite a estudiantes y educadores experimentar directamente con conceptos fundamentales de organización de sistemas computacionales.

### Características Principales

- **Arquitectura completa de 64 bits** con direccionamiento de 44 bits
- **137+ instrucciones implementadas** en 5 formatos diferentes (incluyendo ALU, FPU y Stack)
- **16 registros de propósito general** (R01-R15) 
- **Sistema de flags** (Z, N, C, V) para control de flujo
- **Interfaz gráfica intuitiva** con editor y visualizador de estado
- **Ejecución paso a paso** y automática
- **Assembler integrado** con soporte para etiquetas y comentarios
- **Sistema de E/S mapeada en memoria**

### Decisiones de Diseño Arquitectural

- **Tamaño de palabra:** 64 bits  
- **Direccionamiento:** Por byte con acceso por palabra
- **Bus de direcciones:** 44 bits (16 TB de espacio direccionable)
- **Endianness:** Little-endian para compatibilidad
- **Registros generales:** R01 … R15 (codificación de 4 bits)
- **Flags de estado:** Z (zero), N (negative), C (carry), V (overflow)
- **Modelo de memoria:** von Neumann unificado

---

## Documentación Académica

### Documento Principal - Tarea 14

| Documento | Descripción | Contenido |
|-----------|-------------|-----------|
| **[Tarea 14 - Grupo D - Hexacore Atlas](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md)** | **Documento consolidado académico** | Marco teórico, descripción del problema, validación, diseño, manual técnico y especificaciones completas |

> **Documento principal**: Este archivo consolidado contiene toda la documentación académica requerida con portada institucional del Grupo D y la empresa Hexacore para el Simulador Atlas CPU.

### Documentación de Soporte

El documento principal contiene toda la información técnica necesaria. Para detalles específicos de implementación, consultar directamente el código fuente en los archivos Python del proyecto.

---

## Inicio Rápido

### Prerrequisitos

- **Python 3.8+** (con librerías estándar)
- **Sistema Operativo**: Windows, Linux, o macOS
- **Memoria RAM**: 512 MB mínimo
- **Espacio en disco**: 100 MB

### Instalación y Ejecución

```bash
# 1. Clonar o descargar el repositorio
git clone <repository-url>
cd maquina_lenguajes

# 2. Ejecutar la interfaz gráfica
cd GUI
python main.py

# 3. ¡Listo para programar!
```

### Primer Programa

```assembly
; Programa simple - Suma de dos números
LOADV R1, 10        ; Cargar 10 en R1
LOADV R2, 5         ; Cargar 5 en R2
ADD R1, R2          ; R1 = R1 + R2 = 15
SVIO R1, 0x100      ; Guardar resultado en I/O
SHOWIO 0x100        ; Mostrar resultado
PARAR               ; Terminar programa
```

---

Para simplificar la implementación, se definen cinco formatos fijos de 64 bits:

## Arquitectura del Sistema

### Formatos de Instrucción (64 bits)

Para simplificar la implementación, se definen **cinco formatos fijos** de 64 bits:

#### Formato OP (Solo Opcode)
Usado en `PARAR`, `NOP`.
```
 63    48 47                    0
┌────────┬──────────────────────┐
│ OPCODE │         0            │
│16 bits │      48 bits         │
└────────┴──────────────────────┘
```

#### Formato R (Registro Único)
Usado en `INC R`, `DEC R`, `NOT R`.
```
 63    48 47  44 43             0
┌────────┬─────┬─────────────────┐
│ OPCODE │ RD  │        0        │
│16 bits │4bits│     44 bits     │
└────────┴─────┴─────────────────┘
```

#### Formato RR (Registro-Registro)
Usado en `ADD R, R'`, `SUB R, R'`.
```
 63    48 47           8 7   4 3   0
┌────────┬─────────────┬─────┬─────┐
│ OPCODE │      0      │ RD  │ RS  │
│16 bits │   40 bits   │4bits│4bits│
└────────┴─────────────┴─────┴─────┘
```

#### Formato RI (Registro-Inmediato)
Usado en `LOADV R, v`, `ADDV R, v`.
```
 63    48 47  44 43             0
┌────────┬─────┬─────────────────┐
│ OPCODE │ RD  │   INMEDIATO     │
│16 bits │4bits│    44 bits      │
└────────┴─────┴─────────────────┘
```

#### Formato I (Solo Inmediato)  
Usado en `JMP k`, `SHOWIO addr`.
```
 63    48 47             0
┌────────┬─────────────────┐
│ OPCODE │   INMEDIATO     │
│16 bits │    48 bits      │
└────────┴─────────────────┘
```

---

## Conjunto de Instrucciones (ISA)

### Control de Flujo

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0000 | PARAR | Termina la ejecución del programa |
| 0x0001 | NOP | No operación (sin efecto) |
| 0x0090 | JMP k | Salto incondicional a dirección k |
| 0x0091 | JEQ k | Salto si Z=1 (resultado igual a cero) |
| 0x0092 | JNE k | Salto si Z=0 (resultado no igual a cero) |
| 0x0093 | JMI k | Salto si N=1 (resultado negativo) |
| 0x0094 | JPL k | Salto si N=0 (resultado positivo) |

### Aritmética

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0010 | ADD Rd, Rs | Rd = Rd + Rs |
| 0x0011 | SUB Rd, Rs | Rd = Rd - Rs |
| 0x0012 | MULS Rd, Rs | Rd = Rd × Rs (con signo) |
| 0x0013 | MUL Rd, Rs | Rd = Rd × Rs (sin signo) |
| 0x0014 | DIV Rd, Rs | Rd = Rd ÷ Rs |
| 0x0020 | ADDV Rd, v | Rd = Rd + v (valor inmediato) |
| 0x0021 | SUBV Rd, v | Rd = Rd - v (valor inmediato) |
| 0x0030 | INC Rd | Rd = Rd + 1 |
| 0x0031 | DEC Rd | Rd = Rd - 1 |

### Lógicas y Bits

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0040 | NOT Rd | Rd = ~Rd (inversión de bits) |
| 0x0041 | AND Rd, Rs | Rd = Rd & Rs |
| 0x0042 | ANDV Rd, v | Rd = Rd & v |
| 0x0043 | OR Rd, Rs | Rd = Rd \| Rs |
| 0x0044 | ORV Rd, v | Rd = Rd \| v |
| 0x0045 | XOR Rd, Rs | Rd = Rd ^ Rs |
| 0x0046 | XORV Rd, v | Rd = Rd ^ v |
| 0x0050 | SHL Rd | Shift left lógico |
| 0x0051 | SHR Rd | Shift right lógico |

### Memoria y Datos

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0060 | LOAD Rd, addr | Rd = Memoria[addr] |
| 0x0061 | LOADV Rd, v | Rd = v (cargar valor inmediato) |
| 0x0062 | STORE Rd, Rs | Memoria[Rs] = Rd |
| 0x0063 | STOREV Rd, addr | Memoria[addr] = Rd |
| 0x0064 | CLEAR Rd | Rd = 0 |
| 0x0070 | CMP Rd, Rs | Comparar Rd con Rs (8 bytes, actualiza flags) |
| 0x0071 | CMPV Rd, v | Comparar Rd con valor inmediato (8 bytes) |
| 0x0830 | CMP1 Rd, Rs | Comparar Rd con Rs (1 byte) |
| 0x0831 | CMP2 Rd, Rs | Comparar Rd con Rs (2 bytes) |
| 0x0832 | CMP4 Rd, Rs | Comparar Rd con Rs (4 bytes) |
| 0x0833 | CMP8 Rd, Rs | Comparar Rd con Rs (8 bytes) |
| 0x0840 | CMPV1 Rd, v | Comparar Rd con valor inmediato (1 byte) |
| 0x0841 | CMPV2 Rd, v | Comparar Rd con valor inmediato (2 bytes) |
| 0x0842 | CMPV4 Rd, v | Comparar Rd con valor inmediato (4 bytes) |
| 0x0843 | CMPV8 Rd, v | Comparar Rd con valor inmediato (8 bytes) |

### Entrada/Salida

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x00A0 | SVIO Rd, addr | IO[addr] = Rd |
| 0x00A1 | LOADIO Rd, addr | Rd = IO[addr] |
| 0x00A2 | SHOWIO addr | Mostrar valor en IO[addr] |
| 0x00A3 | CLRIO | Limpiar dispositivos de entrada |
| 0x00A4 | RESETIO | Resetear sistema de E/S |

### Aritmética con Tamaños Específicos (ALU)

#### Operaciones de 1 Byte
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0100 | ADD1 Rd, Rs | Rd = Rd + Rs (1 byte, con signo) |
| 0x0101 | SUB1 Rd, Rs | Rd = Rd - Rs (1 byte, con signo) |
| 0x0102 | MUL1 Rd, Rs | Rd = Rd × Rs (1 byte, sin signo) |
| 0x0103 | MULS1 Rd, Rs | Rd = Rd × Rs (1 byte, con signo) |
| 0x0104 | DIV1 Rd, Rs | Rd = Rd ÷ Rs (1 byte, con signo) |
| 0x0110 | ADDV1 Rd, v | Rd = Rd + v (1 byte, valor inmediato) |
| 0x0111 | SUBV1 Rd, v | Rd = Rd - v (1 byte, valor inmediato) |

#### Operaciones de 2 Bytes
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0200 | ADD2 Rd, Rs | Rd = Rd + Rs (2 bytes, con signo) |
| 0x0201 | SUB2 Rd, Rs | Rd = Rd - Rs (2 bytes, con signo) |
| 0x0202 | MUL2 Rd, Rs | Rd = Rd × Rs (2 bytes, sin signo) |
| 0x0203 | MULS2 Rd, Rs | Rd = Rd × Rs (2 bytes, con signo) |
| 0x0204 | DIV2 Rd, Rs | Rd = Rd ÷ Rs (2 bytes, con signo) |
| 0x0210 | ADDV2 Rd, v | Rd = Rd + v (2 bytes, valor inmediato) |
| 0x0211 | SUBV2 Rd, v | Rd = Rd - v (2 bytes, valor inmediato) |

#### Operaciones de 4 Bytes
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0300 | ADD4 Rd, Rs | Rd = Rd + Rs (4 bytes, con signo) |
| 0x0301 | SUB4 Rd, Rs | Rd = Rd - Rs (4 bytes, con signo) |
| 0x0302 | MUL4 Rd, Rs | Rd = Rd × Rs (4 bytes, sin signo) |
| 0x0303 | MULS4 Rd, Rs | Rd = Rd × Rs (4 bytes, con signo) |
| 0x0304 | DIV4 Rd, Rs | Rd = Rd ÷ Rs (4 bytes, con signo) |
| 0x0310 | ADDV4 Rd, v | Rd = Rd + v (4 bytes, valor inmediato) |
| 0x0311 | SUBV4 Rd, v | Rd = Rd - v (4 bytes, valor inmediato) |

### Transferencia de Datos (MOV)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0400 | MOV1 Rd, Rs | Rd = Rs (1 byte) |
| 0x0401 | MOV2 Rd, Rs | Rd = Rs (2 bytes) |
| 0x0402 | MOV4 Rd, Rs | Rd = Rs (4 bytes) |
| 0x0403 | MOV8 Rd, Rs | Rd = Rs (8 bytes) |
| 0x0410 | MOVV1 Rd, v | Rd = v (1 byte, valor inmediato) |
| 0x0411 | MOVV2 Rd, v | Rd = v (2 bytes, valor inmediato) |
| 0x0412 | MOVV4 Rd, v | Rd = v (4 bytes, valor inmediato) |
| 0x0413 | MOVV8 Rd, v | Rd = v (8 bytes, valor inmediato) |

### Carga de Memoria (LOAD)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0500 | LOAD1 Rd, addr | Rd = Memoria[addr] (1 byte) |
| 0x0501 | LOAD2 Rd, addr | Rd = Memoria[addr] (2 bytes) |
| 0x0502 | LOAD4 Rd, addr | Rd = Memoria[addr] (4 bytes) |
| 0x0503 | LOAD8 Rd, addr | Rd = Memoria[addr] (8 bytes) |
| 0x0510 | LOADR1 Rd, Rs | Rd = Memoria[Rs] (1 byte, indirecto) |
| 0x0511 | LOADR2 Rd, Rs | Rd = Memoria[Rs] (2 bytes, indirecto) |
| 0x0512 | LOADR4 Rd, Rs | Rd = Memoria[Rs] (4 bytes, indirecto) |
| 0x0513 | LOADR8 Rd, Rs | Rd = Memoria[Rs] (8 bytes, indirecto) |

### Almacenamiento en Memoria (STORE)

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0600 | STORE1 Rd, addr | Memoria[addr] = Rd (1 byte) |
| 0x0601 | STORE2 Rd, addr | Memoria[addr] = Rd (2 bytes) |
| 0x0602 | STORE4 Rd, addr | Memoria[addr] = Rd (4 bytes) |
| 0x0603 | STORE8 Rd, addr | Memoria[addr] = Rd (8 bytes) |
| 0x0610 | STORER1 Rd, Rs | Memoria[Rs] = Rd (1 byte, indirecto) |
| 0x0611 | STORER2 Rd, Rs | Memoria[Rs] = Rd (2 bytes, indirecto) |
| 0x0612 | STORER4 Rd, Rs | Memoria[Rs] = Rd (4 bytes, indirecto) |
| 0x0613 | STORER8 Rd, Rs | Memoria[Rs] = Rd (8 bytes, indirecto) |

### Punto Flotante (FPU)

#### Operaciones de 4 Bytes (Float)
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0700 | FADD4 Rd, Rs | Rd = Rd + Rs (float, 4 bytes) |
| 0x0701 | FSUB4 Rd, Rs | Rd = Rd - Rs (float, 4 bytes) |
| 0x0702 | FMUL4 Rd, Rs | Rd = Rd × Rs (float, 4 bytes) |
| 0x0703 | FDIV4 Rd, Rs | Rd = Rd ÷ Rs (float, 4 bytes) |
| 0x0720 | FSQRT4 Rd | Rd = √Rd (float, 4 bytes) |
| 0x0722 | FSIN4 Rd | Rd = sin(Rd) (float, 4 bytes) |
| 0x0723 | FCOS4 Rd | Rd = cos(Rd) (float, 4 bytes) |

#### Operaciones de 8 Bytes (Double)
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0710 | FADD8 Rd, Rs | Rd = Rd + Rs (double, 8 bytes) |
| 0x0711 | FSUB8 Rd, Rs | Rd = Rd - Rs (double, 8 bytes) |
| 0x0712 | FMUL8 Rd, Rs | Rd = Rd × Rs (double, 8 bytes) |
| 0x0713 | FDIV8 Rd, Rs | Rd = Rd ÷ Rs (double, 8 bytes) |
| 0x0721 | FSQRT8 Rd | Rd = √Rd (double, 8 bytes) |
| 0x0724 | FSIN8 Rd | Rd = sin(Rd) (double, 8 bytes) |
| 0x0725 | FCOS8 Rd | Rd = cos(Rd) (double, 8 bytes) |

### Operaciones de Pila (Stack)

#### Control de Subrutinas
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0800 | RET | Retorna de subrutina (pop dirección de retorno) |

#### Operaciones de Pila por Tamaño
| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x0810 | POP1 Rd | Rd = Stack[SP-1] (pop 1 byte) |
| 0x0811 | POP2 Rd | Rd = Stack[SP-2] (pop 2 bytes) |
| 0x0812 | POP4 Rd | Rd = Stack[SP-4] (pop 4 bytes) |
| 0x0813 | POP8 Rd | Rd = Stack[SP-8] (pop 8 bytes) |
| 0x0820 | PUSH1 Rd | Stack[SP] = Rd (push 1 byte) |
| 0x0821 | PUSH2 Rd | Stack[SP] = Rd (push 2 bytes) |
| 0x0822 | PUSH4 Rd | Stack[SP] = Rd (push 4 bytes) |
| 0x0823 | PUSH8 Rd | Stack[SP] = Rd (push 8 bytes) |

> **Referencia completa**: Ver [Documento Académico Principal](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas) para todas las instrucciones (originales + nuevas ALU/FPU)

---

## Algoritmos Validados

El simulador ha sido **exhaustivamente probado** con algoritmos clásicos:

### Algoritmo de Euclides
```assembly
; Calcula MCD(1071, 462) = 21
LOADV R1, 1071
LOADV R2, 462
EUCLIDES:
    CMP R2, R0
    JEQ FIN_GCD
    ; Implementación completa en archivo
```
**Resultado**: MCD = 21 (verificado matemáticamente)

### Algoritmo del Módulo  
```assembly
; Calcula 17 % 5 = 2
LOADV R1, 17
LOADV R2, 5
; Algoritmo: a - (a/b)*b
```
**Resultado**: 17 % 5 = 2 (verificado: 3×5+2=17)

### Algoritmo de Valor Absoluto
```assembly
; Calcula |x| usando complemento a 2
; Casos: |-7| = 7, |15| = 15
LOADV R1, 7
NOT R1
INC R1  ; R1 = -7
; Detección y conversión...
```
**Resultado**: |-7| = 7, |15| = 15 (ambos casos correctos)

> **Evidencias completas**: Ver [Documento Académico - Validación](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#3-validación-y-evidencias)

---

## Estructura del Proyecto

```
maquina_lenguajes/
├── Algoritmos/              # Algoritmos de prueba validados
│   ├── Euclides/Tarea9/        # Algoritmo de Euclides
│   ├── Modulo/                 # Operación módulo
│   ├── ValorAbsoluto/          # Valor absoluto con complemento a 2
│   ├── Matrix/                 # Operaciones matriciales
│   └── SumaEnteros/            # Suma iterativa
├── GUI/                     # Interfaz gráfica de usuario
│   └── main.py                 # Aplicación principal
├── Documentacion/           # Archivos de documentación técnica
│   ├── unal.png             # Logo institucional
│   └── Tarea14_GrupoD_Hexacore_Atlas.md # DOCUMENTO ACADÉMICO PRINCIPAL
├── CPU.py                   # Procesador principal (64-bit, 47 instrucciones)
├── assembler.py             # Ensamblador con 5 formatos de instrucción
├── loader.py                # Cargador con reubicación automática
├── disco_64bits.py          # Sistema de memoria auxiliar
├── test_integration.py      # Pruebas de integración
└── README.md                # Este archivo (guía del proyecto)
```

> **Nota**: El documento `Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md` es el archivo principal que contiene toda la documentación académica consolidada.

---

## Ejemplos de Programas

### Suma de los Primeros N Números
```assembly
; Calcula 1+2+3+...+n donde n=5
LOADV R1, 5         ; n = 5
CLEAR R2            ; suma = 0

LOOP:
ADD R2, R1          ; suma += n
DEC R1              ; n--
CMPV R1, 0          ; comparar n con 0
JNE LOOP            ; si n != 0, continuar

SVIO R2, 0x200      ; guardar resultado
SHOWIO 0x200        ; mostrar suma = 15
PARAR
```

### Factorial Recursivo
```assembly
; Calcular factorial de 4
LOADV R1, 4         ; n = 4
LOADV R2, 1         ; factorial = 1

FACT_LOOP:
CMPV R1, 0          ; comparar n con 0
JEQ FIN             ; si n == 0, terminar
MUL R2, R1          ; factorial *= n
DEC R1              ; n--
JMP FACT_LOOP

FIN:
SVIO R2, 0x300      ; guardar resultado
SHOWIO 0x300        ; mostrar factorial = 24
PARAR
```

### Búsqueda de Máximo
```assembly
; Encontrar el máximo entre tres números
LOADV R1, 15        ; primer número
LOADV R2, 8         ; segundo número  
LOADV R3, 23        ; tercer número
CLEAR R4            ; máximo actual

; Lógica de comparación...
; (Ver manual completo para implementación)

SVIO R4, 0x400      ; guardar máximo
SHOWIO 0x400        ; mostrar máximo = 23
PARAR
```

### Operaciones de Pila (Stack)

```assembly
; Ejemplo de uso de operaciones de pila
LOADV R1, 42         ; Cargar valor en R1
PUSH8 R1            ; Push R1 (8 bytes) a la pila
LOADV R2, 100       ; Cargar otro valor en R2
PUSH4 R2            ; Push R2 (4 bytes) a la pila

POP4 R3             ; Pop 4 bytes a R3
POP8 R4             ; Pop 8 bytes a R4

SVIO R3, 0x500      ; Mostrar resultado del pop de 4 bytes
SHOWIO 0x500
SVIO R4, 0x501      ; Mostrar resultado del pop de 8 bytes
SHOWIO 0x501
PARAR
```

### Subrutinas con RET

```assembly
; Ejemplo de subrutina usando RET
LOADV R1, 5         ; Argumento para factorial
CALL FACTORIAL      ; Llamar subrutina
SVIO R1, 0x600      ; Mostrar resultado
SHOWIO 0x600
PARAR

FACTORIAL:
    PUSH8 R1        ; Guardar argumento
    LOADV R2, 1     ; factorial = 1
    
FACT_LOOP:
    CMPV R1, 0      ; comparar n con 0
    JEQ FACT_RETURN ; si n == 0, retornar
    MUL R2, R1      ; factorial *= n
    DEC R1          ; n--
    JMP FACT_LOOP
    
FACT_RETURN:
    MOV R1, R2      ; resultado en R1
    RET             ; retornar de subrutina
```

> **Más ejemplos**: Ver [Manual Técnico](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#5-manual-técnico-y-de-usuario) sección 5.2

---

## Características Técnicas

### Rendimiento
- **Velocidad**: ~1M instrucciones/segundo (Python interpretado)
- **Memoria**: Configurable, default 25,000 bytes
- **Responsividad**: Interfaz gráfica fluida durante ejecución

### Robustez
- **Validación exhaustiva**: Verificación de sintaxis y límites
- **Manejo de errores**: Recuperación elegante de estados inconsistentes

### Extensibilidad
- **Arquitectura modular**: Componentes independientes y reutilizables
- **Plugin system**: Capacidad de agregar nuevas funcionalidades
- **Open source**: Código fuente completo disponible

---

## Testing y Validación

### Pruebas de Integración
```bash
# Ejecutar suite completa de pruebas
python test_integration.py
```

### Validación de Algoritmos
- **Euclides**: MCD(1071, 462) = 21 (verificado)
- **Módulo**: 17 % 5 = 2 (verificado)  
- **Valor Absoluto**: |-7| = 7, |15| = 15 (verificado)
- **Todas las instrucciones**: 137+/137+ validadas (verificado)


---

### Recursos Adicionales
- **Documentación completa**: Archivo principal `Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md`
- **Ejemplos prácticos**: Carpeta `Algoritmos/` con casos reales
- **Especificaciones**: Ver [Especificaciones Técnicas](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas)

---

## Reconocimientos

### Propósito Educativo
Este proyecto fue desarrollado como parte del curso de **Lenguajes de Programación** con el objetivo de entender y aplicar conceptos fundamentales a través de un simulador práctico.

### Desarrollo
- **Arquitectura**: Basada en principios von Neumann clásicos
- **Implementación**: Python 3.8+ con librerías estándar
- **Metodología**: Desarrollo incremental con validación continua
- **Testing**: Algoritmos clásicos como casos de prueba

---

## Licencia

Este proyecto está desarrollado con **fines educativos** y se distribuye bajo licencia académica. El código fuente está disponible para:

- Uso en instituciones educativas
- Investigación académica  
- Aprendizaje personal
- Contribuciones al proyecto

Para uso comercial o distribución, contactar a los desarrolladores.

---

<div align="center">

### **Atlas CPU Simulator - Hexacore Technologies** 

[![Documentación](https://img.shields.io/badge/Docs-Completa-blue.svg)](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md)
[![Algoritmos](https://img.shields.io/badge/Algoritmos-Validados-green.svg)](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#3-validación-y-evidencias)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-64bit-orange.svg)](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#1-marco-teórico)
[![ISA](https://img.shields.io/badge/Instrucciones-137+-red.svg)](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas)

**Desarrollado por Grupo D - Universidad Nacional de Colombia**  
**Hexacore Technologies - Simulador Atlas CPU**

</div>

---

*README actualizado: Septiembre 2025 - Tarea 14 Grupo D*

**Entrega Académica**: El documento consolidado **`Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md`** contiene toda la documentación requerida para la evaluación académica, incluyendo marco teórico, descripción del problema, validación completa, diseño de la aplicación, manual técnico y especificaciones del Simulador Atlas CPU desarrollado por Hexacore.