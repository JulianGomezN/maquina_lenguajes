# Simulador Atlas CPU
## Simulador Educativo de Arquitectura de Computadores

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](README.md)

---

## Descripción General

El **Simulador Atlas CPU** es una herramienta educativa completa que implementa un procesador de 64 bits con arquitectura RISC. Diseñado específicamente para la enseñanza de **arquitectura de computadores**, permite a estudiantes y educadores experimentar directamente con conceptos fundamentales de organización de sistemas computacionales.

### Características Principales

- **Arquitectura completa de 64 bits** con direccionamiento de 44 bits
- **47 instrucciones implementadas** en 5 formatos diferentes
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

Herramienta de conversión (mdconverter)
--------------------------------------
En la carpeta `Documentacion/mdconverter` hay una pequeña utilidad para convertir archivos Markdown (.md) a PDF con Pandoc y una configuración LaTeX mínima.

- `convertir.bat` — lanzador para Windows que abre un diálogo de archivos.
- `convertir_dialogo.py` — script Python que pide el .md mediante un filedialog, limpia caracteres Unicode problemáticos, genera el PDF con Pandoc (pdflatex + --toc) y elimina el archivo .md temporal.
- `limpiar_unicode.py` — limpiador de caracteres Unicode y líneas separadoras (`---`).

Antes de convertir, revise el documento Markdown y retire cualquier índice manual o contenido de portada hasta la primera aparición de `\newpage` justo antes de la primera sección (por ejemplo, antes de `# 1. Marco Teórico`). El convertidor genera su propia tabla de contenidos automáticamente.

---

## Inicio Rápido

### Prerrequisitos

- **Python 3.8+** (con librerías estándar)
- **Sistema Operativo**: Windows, Linux, o macOS
- **Memoria RAM**: 512 MB mínimo
- **Espacio en disco**: 100 MB
- **Pandoc** (opcional, para convertir `Documentacion/*.md` a PDF)
- **Distribución LaTeX** (MiKTeX/TeX Live) si desea generar PDFs con Pandoc
- **Tkinter** (incluido en la mayoría de distribuciones de Python; requerido por el diálogo en `mdconverter`)

### Instalación y Ejecución

```bash
# 1. Clonar o descargar el repositorio
git clone <repository-url>
cd maquina_lenguajes

# 2. Ejecutar la interfaz gráfica
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
| 0x0070 | CMP Rd, Rs | Comparar Rd con Rs (actualiza flags) |
| 0x0071 | CMPV Rd, v | Comparar Rd con valor inmediato |

### Entrada/Salida

| Opcode | Instrucción | Descripción |
|--------|-------------|-------------|
| 0x00A0 | SVIO Rd, addr | IO[addr] = Rd |
| 0x00A1 | LOADIO Rd, addr | Rd = IO[addr] |
| 0x00A2 | SHOWIO addr | Mostrar valor en IO[addr] |
| 0x00A3 | CLRIO | Limpiar dispositivos de entrada |
| 0x00A4 | RESETIO | Resetear sistema de E/S |

> **Referencia completa**: Ver [Documento Académico Principal](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas) para todas las 47 instrucciones

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
├── Algoritmos/              # Algoritmos de prueba y ejemplos (Euclides, Módulo, Matrix, ...)
├── GUI/                     # Interfaz gráfica de usuario (código Tkinter)
│   └── GUI.py               # Entrada y widgets principales
├── Documentacion/           # Archivos de documentación técnica
│   └── mdconverter/         # Utilidad para convertir .md -> .pdf (gui + scripts)
├── compiler/                # Herramientas del compilador / ensamblador
│   └── assembler.py         # Ensamblador (parsing y generación binaria)
├── logic/                   # Núcleo del simulador (CPU, Memory, Loader)
│   ├── CPU.py
│   ├── Memory.py
│   └── Loader.py
├── main.py                  # Launcher de la GUI
├── test_integration.py      # Pruebas de integración y ejemplos de uso
└── README.md                # Este archivo (guía del proyecto)
```

> **Nota**: El documento `Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md` contiene la documentación académica consolidada (Tarea 14).

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
- **Todas las instrucciones**: 47/47 validadas (verificado)


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
[![ISA](https://img.shields.io/badge/Instrucciones-47-red.svg)](Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas)

**Desarrollado por Grupo D - Universidad Nacional de Colombia**  
**Hexacore Technologies - Simulador Atlas CPU**

</div>

---

*README actualizado: Septiembre 2025 - Tarea 14 Grupo D*

**Entrega Académica**: El documento consolidado **`Documentacion/Tarea14_GrupoD_Hexacore_Atlas.md`** contiene toda la documentación requerida para la evaluación académica, incluyendo marco teórico, descripción del problema, validación completa, diseño de la aplicación, manual técnico y especificaciones del Simulador Atlas CPU desarrollado por Hexacore.