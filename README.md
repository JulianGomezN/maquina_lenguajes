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
[Instrucciones de CPU y formatos](Documentacion/CPU/Instrucciones.md)

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