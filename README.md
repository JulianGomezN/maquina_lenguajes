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
- **137+ instrucciones implementadas** en 5 formatos diferentes (incluyendo ALU, FPU y Stack)
- **16 registros de propósito general** (R00-R15, donde R14=BP, R15=SP)
- **Sistema de flags** (Z, N, C, V) para control de flujo
- **Compilador de lenguaje de alto nivel** con sintaxis tipo C y keywords en español
- **Preprocesador** con soporte para macros, constantes y archivos de inclusión (#include, #define)
- **Interfaz gráfica intuitiva** con editor y visualizador de estado
- **Ejecución paso a paso** y automática con depuración visual
- **Assembler integrado** con soporte para etiquetas, directivas y comentarios
- **Sistema de E/S mapeada en memoria** con dispositivos de pantalla y teclado

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

### Documento Principal - Taller 2

| Documento | Descripción | Contenido |
|-----------|-------------|-----------||
| **[Taller 2 - Grupo D - Hexacore Atlas](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md)** | **Documento consolidado académico** | Marco teórico, descripción del problema, validación, diseño, manual técnico y especificaciones completas |

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

### Instalación y Ejecución

```bash
# 1. Clonar o descargar el repositorio
git clone <repository-url>
cd maquina_lenguajes

# 2. Instalar dependencias (si es necesario)
pip install -r requirements.txt

# 3. Ejecutar la interfaz gráfica
python src/main.py

# 4. ¡Listo para programar!
```

### Persistencia de RAM y visor de memoria

- La RAM del simulador se persiste automáticamente en un archivo de texto `memory_ram.txt` en el directorio de trabajo.
    - Al iniciar el programa, si existe `memory_ram.txt`, se carga su contenido en la RAM.
    - Al cerrar el programa, la RAM completa se guarda de nuevo en `memory_ram.txt` (formato legible, 8 bytes por línea, con dirección base).
- En la GUI, en la sección "Examinador de Memoria", hay un botón "👁 Ver RAM" que abre un visor en forma de tabla:
    - Cada fila representa 8 bytes contiguos (alineados a 8), consistente con el tamaño de palabra/instrucción de 64 bits del simulador.
    - Columnas: Dirección y los 8 bytes (B0..B7) en hexadecimal.
    - Incluye opción de auto-actualización (intervalo configurable) o actualización manual con botón.

Para cambiar la ruta del archivo de memoria, puede instanciar `Memory` con el parámetro `memory_file` en `main.py`.

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

### Lenguaje de Alto Nivel

El simulador incluye un **compilador completo** que soporta un lenguaje de alto nivel con sintaxis tipo C y keywords en español:

```c
// Ejemplo: Algoritmo de Euclides (MCD)
funcion entero euclides(entero a, entero b) {
    entero temp;
    
    mientras (b != 0) {
        temp = a % b;
        a = b;
        b = temp;
    }
    
    retornar a;
}

funcion entero principal() {
    entero resultado;
    resultado = euclides(1071, 462);
    retornar resultado;  // Retorna 21 (MCD de 1071 y 462)
}
```

**Características del lenguaje:**
- **Tipos de datos**: `entero` (64 bits), `flotante`, `cadena`, `caracter`, `booleano`
- **Estructuras de control**: `si`/`si_no`, `mientras`, `para`, `hacer_mientras`
- **Estructuras de datos**: `estructura` (structs), arreglos, punteros
- **Operadores**: Aritméticos (+, -, *, /, %), lógicos (&&, ||, !), comparación (==, !=, <, >, <=, >=)
- **Funciones**: Declaración, llamada, recursión, parámetros por valor
- **Gestión de memoria**: `nuevo`, `eliminar` (malloc/free)
- **Preprocesador**: `#include`, `#define`, `#ifdef`, `#ifndef`
- **Librerías**: Sistema de librerías estándar (math.asm, io.asm, utils.asm)

**Pipeline de compilación:**
1. **Preprocesador** → Expande macros y archivos de inclusión
2. **Análisis Léxico** → Tokenización del código fuente
3. **Análisis Sintáctico** → Construcción del AST (PLY yacc)
4. **Análisis Semántico** → Verificación de tipos y ámbitos
5. **Generación de Código** → Traducción a ensamblador Atlas
6. **Ensamblado** → Conversión a código binario
7. **Enlazado** → Resolución de símbolos externos
8. **Carga** → Ubicación en memoria y ejecución

> **Ejemplos completos**: Ver `Algoritmos/Ejemplos_alto_nivel/` para más programas validados

> **Gramática formal**: Ver `Documentacion/README_GRAMATICA.md` para especificación E-BNF completa

---

Para simplificar la implementación, se definen cinco formatos fijos de 64 bits:

## Arquitectura del Sistema
[Instrucciones de CPU y formatos](Documentacion/CPU/Instrucciones.md)

> **Referencia completa**: Ver [Documento Académico Principal](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas) para todas las instrucciones (originales + nuevas ALU/FPU)

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

> **Evidencias completas**: Ver [Documento Académico - Validación](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#3-validación-y-evidencias)

---

## Estructura del Proyecto

```
maquina_lenguajes/
├── Algoritmos/                      # Algoritmos de prueba y ejemplos validados
│   ├── Ejemplos_alto_nivel/         # Programas en lenguaje de alto nivel (.txt)
│   │   ├── 1.txt                    # Ejemplo con macros y operaciones matemáticas
│   │   ├── 2.txt                    # Ejemplo de bucle while con continue
│   │   ├── 3.txt                    # Ejemplo de estructuras y punteros
│   │   ├── euclides_resta.txt       # Algoritmo de Euclides con restas sucesivas
│   │   ├── euclides_modulo.txt      # Algoritmo de Euclides con operador módulo
│   │   └── README_EUCLIDES.md       # Documentación de algoritmos de Euclides
│   ├── Ejemplos_Librerias/          # Ejemplos de uso de librerías del sistema
│   ├── Euclides/                    # Implementación del algoritmo de Euclides
│   ├── Matrix/                      # Operaciones con matrices
│   ├── Modulo/                      # Algoritmo del módulo
│   ├── SumaEnteros/                 # Suma de enteros
│   └── ValorAbsoluto/               # Cálculo de valor absoluto
├── build/                           # Archivos generados por el compilador
│   ├── bin/                         # Binarios generados
│   └── obj/                         # Archivos objeto intermedios
├── Documentacion/                   # Documentación técnica y académica
│   ├── CPU/                         # Especificaciones de la CPU
│   │   ├── Instrucciones.md         # Set de instrucciones completo
│   │   └── SIA.md                   # Sistema de Instrucciones Atlas
│   ├── mdconverter/                 # Utilidad para convertir .md -> .pdf
│   ├── Taller1/                     # Documentación del Taller 1
│   ├── Taller2/                     # Documentación del Taller 2 (Gramática)
│   │   └── gramatica/               # Definición formal de la gramática E-BNF
│   ├── Tarea 14/                    # Documentación académica principal
│   ├── GUIA_VISUALIZACION.md        # Guía para visualización de memoria
│   ├── README_GRAMATICA.md          # Documentación de la gramática
│   └── verificacion_gramatica.md    # Pruebas de validación de gramática
├── lib/                             # Librerías del sistema en ensamblador
│   ├── io.asm                       # Rutinas de entrada/salida
│   ├── lib_principal.asm            # Librería principal del sistema
│   ├── math.asm                     # Funciones matemáticas
│   ├── math_utils.h                 # Header con macros matemáticas
│   ├── stack.asm                    # Operaciones de pila
│   ├── stdio.asm                    # Entrada/salida estándar
│   └── utils.asm                    # Utilidades generales
├── src/                             # Código fuente principal
│   ├── compiler/                    # Pipeline del compilador
│   │   ├── Lex_analizer.py          # Analizador léxico (tokenización)
│   │   ├── syntax_analizer.py       # Analizador sintáctico (parser PLY)
│   │   ├── semantic_analyzer.py     # Analizador semántico (tipos, ámbitos)
│   │   ├── code_generator.py        # Generador de código ensamblador
│   │   ├── ensamblador.py           # Ensamblador (ASM -> binario)
│   │   ├── Preprocessor.py          # Preprocesador (#include, #define)
│   │   ├── Linker.py                # Enlazador de módulos
│   │   ├── Loader.py                # Cargador de binarios en memoria
│   │   ├── ast_nodes.py             # Nodos del árbol sintáctico abstracto
│   │   ├── symbol_table.py          # Tabla de símbolos y ámbitos
│   │   ├── compiler.py              # Orquestador del pipeline completo
│   │   └── README_PARSER.md         # Documentación del parser
│   ├── GUI/                         # Interfaz gráfica de usuario
│   │   └── GUI.py                   # Aplicación Tkinter principal
│   ├── machine/                     # Simulador de hardware
│   │   ├── CPU/                     # Implementación de la CPU Atlas
│   │   ├── IO/                      # Sistema de entrada/salida
│   │   └── Memory/                  # Sistema de memoria
│   ├── tests/                       # Suite de pruebas unitarias
│   │   ├── test_lexer.py            # Pruebas del analizador léxico
│   │   ├── test_syntax_analizer.py  # Pruebas del parser
│   │   ├── test_semantic_analyzer.py # Pruebas del análisis semántico
│   │   ├── test_code_generator.py   # Pruebas del generador de código
│   │   ├── test_ensamblador.py      # Pruebas del ensamblador
│   │   ├── test_preprocessor.py     # Pruebas del preprocesador
│   │   └── test_integration.py      # Pruebas de integración completas
│   ├── main.py                      # Punto de entrada de la aplicación
│   └── memory_ram.txt               # Archivo de persistencia de memoria RAM
├── requirements.txt                 # Dependencias del proyecto (PLY)
└── README.md                        # Este archivo (guía del proyecto)
```


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

> **Más ejemplos**: Ver [Manual Técnico](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#5-manual-técnico-y-de-usuario) sección 5.2

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

### Pruebas del Compilador
```bash
# Navegar al directorio src
cd src

# Ejecutar pruebas del analizador léxico
python -m pytest tests/test_lexer.py -v

# Ejecutar pruebas del parser
python -m pytest tests/test_syntax_analizer.py -v

# Ejecutar pruebas del análisis semántico
python -m pytest tests/test_semantic_analyzer.py -v

# Ejecutar pruebas del generador de código
python -m pytest tests/test_code_generator.py -v

# Ejecutar pruebas del ensamblador
python -m pytest tests/test_ensamblador.py -v

# Ejecutar todas las pruebas
python -m pytest tests/ -v
```

### Validación de Algoritmos

**Ensamblador (bajo nivel):**
- **Euclides**: MCD(1071, 462) = 21 (verificado)
- **Módulo**: 17 % 5 = 2 (verificado)  
- **Valor Absoluto**: |-7| = 7, |15| = 15 (verificado)
- **Matrices**: Operaciones básicas validadas
- **Todas las instrucciones**: 137+/137+ validadas (verificado)

**Alto Nivel (compilador):**
- **Euclides (resta)**: MCD(1071, 462) = 21 (método de Peña)
- **Euclides (módulo)**: MCD(1071, 462) = 21 (método optimizado)
- **Macros y constantes**: Expansión correcta del preprocesador
- **Estructuras y punteros**: Gestión de memoria dinámica
- **Bucles y condicionales**: Control de flujo validado


---

### Recursos Adicionales
- **Documentación completa**: Archivo principal `Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md`
- **Ejemplos prácticos**: Carpeta `Algoritmos/` con casos reales
- **Especificaciones**: Ver [Especificaciones Técnicas](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas)

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

[![Documentación](https://img.shields.io/badge/Docs-Completa-blue.svg)](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md)
[![Algoritmos](https://img.shields.io/badge/Algoritmos-Validados-green.svg)](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#3-validación-y-evidencias)
[![Arquitectura](https://img.shields.io/badge/Arquitectura-64bit-orange.svg)](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#1-marco-teórico)
[![ISA](https://img.shields.io/badge/Instrucciones-137+-red.svg)](Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md#6-especificaciones-técnicas)

**Desarrollado por Grupo D - Universidad Nacional de Colombia**  
**Hexacore Technologies - Simulador Atlas CPU**

</div>

---

*README actualizado: Noviembre 2025 - Taller 2 Grupo D*

**Entrega Académica**: El documento consolidado **`Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md`** contiene toda la documentación requerida para la evaluación académica, incluyendo marco teórico, descripción del problema, validación completa, diseño de la aplicación, manual técnico y especificaciones del Simulador Atlas CPU desarrollado por Hexacore.

**Compilador y Lenguaje de Alto Nivel**: El proyecto incluye un compilador completo con preprocesador, análisis léxico/sintáctico/semántico, generador de código, ensamblador, enlazador y cargador. Ver gramática formal en `Documentacion/README_GRAMATICA.md` y ejemplos validados en `Algoritmos/Ejemplos_alto_nivel/`.