# GUÍA DE SUSTENTACIÓN - TALLER 2
## Grupo D - Hexacore - Atlas CPU

**Fecha**: 02 o 03 de Diciembre de 2025  
**Duración**: 60 minutos  
**Profesor**: Jorge Eduardo Ortiz

---

## ✅ CHECKLIST DE PREPARACIÓN PREVIA

### Antes de la sustentación:

- [ ] Tener abierto VS Code en la carpeta del proyecto
- [ ] Tener ejecutado `python src/main.py` con la GUI abierta
- [ ] Tener los 3 archivos de algoritmos listos para abrir
- [ ] Tener el archivo `Taller2_GrupoD_Hexacore_Atlas.md` abierto en el navegador o editor
- [ ] Tener la sección de gramática (2.4) lista para mostrar
- [ ] Tener los diagramas de sintaxis (2.5) accesibles
- [ ] Tener la sección de semántica (2.6) marcada
- [ ] Probar que todos los algoritmos compilan y ejecutan correctamente

---

## 📋 ESTRUCTURA DE LA SUSTENTACIÓN (60 MINUTOS)

### PARTE 1: FUNCIONAMIENTO DEL LENGUAJE (10 minutos)

#### Objetivo: Demostrar el funcionamiento completo del sistema

#### 1.1 Algoritmo de Euclides - Versión Iterativa (3-4 min)

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/euclides_con_preprocesador.txt`

**Puntos clave a mencionar**:
- ✅ Versión iterativa usando `mientras (b != 0)`
- ✅ Usa `#include` para incluir biblioteca (`lib/math_utils.h`)
- ✅ Usa `#define` para constantes (`VALOR_A`, `VALOR_B`, `MAX_ITERACIONES`)
- ✅ Demuestra preprocesador completo

**Demostración paso a paso**:
1. Abrir el archivo en la GUI
2. Hacer clic en "Compilar Completo"
3. **MOSTRAR EL PROCESO COMPLETO**:
   ```
   Preprocesador → Expansión de #define y #include
   ↓
   Lexer → Tokens generados
   ↓
   Parser → AST (Abstract Syntax Tree)
   ↓
   Análisis Semántico → Validación de tipos
   ↓
   Generador de Código → Código ensamblador
   ↓
   Ensamblador → Código binario
   ↓
   Linker → Resolución de símbolos
   ↓
   Loader → Carga en memoria
   ```
4. Mostrar el código ensamblador generado
5. Ejecutar paso a paso mostrando:
   - Valores en registros
   - Cambios en flags
   - Stack pointer y base pointer
6. Mostrar resultado: MCD(1071, 462) = 21

**Explicar**:
- "El preprocesador expande las constantes VALOR_A → 1071 antes de compilar"
- "La directiva #include inserta el contenido de math_utils.h"
- "El algoritmo itera hasta que b sea cero, usando el operador módulo"

#### 1.2 Multiplicación de Matrices (3-4 min)

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/multiplicacion_matrices_3d.txt`

**Puntos clave**:
- ✅ Arreglos bidimensionales `entero4[3][3]`
- ✅ Acceso a elementos con índices dobles `matrizA[i][j]`
- ✅ Algoritmo completo de multiplicación de matrices 3×3
- ✅ Uso de variables locales para optimización

**Demostración**:
1. Cargar el archivo
2. Compilar (proceso más rápido, ya se mostró detallado)
3. Ejecutar y mostrar:
   - Matriz A (1,2,3; 4,5,6; 7,8,9)
   - Matriz B (9,8,7; 6,5,4; 3,2,1)
   - Resultado de A × B
4. Explicar el acceso a memoria para arreglos multidimensionales

**Explicar**:
- "Los arreglos 2D se almacenan en row-major order en memoria"
- "El compilador calcula offsets: base + (i × cols + j) × size"

#### 1.3 Ordenamiento Burbuja (2-3 min)

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/bubble_sort.txt`

**Puntos clave**:
- ✅ Arreglo unidimensional `entero4[10]`
- ✅ Bucles anidados con `mientras`
- ✅ Comparación e intercambio de elementos
- ✅ Variable temporal para swap

**Demostración**:
1. Cargar archivo
2. Compilar y ejecutar
3. Mostrar:
   - Arreglo original: [64, 34, 25, 12, 22, 11, 90, 88, 45, 50]
   - Arreglo ordenado: [11, 12, 22, 25, 34, 45, 50, 64, 88, 90]

**Explicar**:
- "Bubble sort compara elementos adyacentes y los intercambia si están en orden incorrecto"
- "Demuestra estructuras de control anidadas y acceso a arreglos"

---

### PARTE 2: GRAMÁTICA LIBRE DE CONTEXTO (10 minutos)

#### Objetivo: Explicar la gramática EBNF y su diseño

#### 2.1 Visión General (2 min)

**Abrir**: `Documentacion/Taller2/Taller2_GrupoD_Hexacore_Atlas.md` - Sección 2.4

**Puntos clave**:
- Gramática completa en notación E-BNF
- Compatible con Railroad Diagram Generator de BottleCaps
- **66 producciones** organizadas en categorías
- **25 palabras reservadas**

**Estructura de la gramática**:
```
1. Estructura del Programa (program, declaration_list, declaration)
2. Declaraciones de Función (function_decl, extern_function_decl)
3. Declaraciones de Estructura (struct_decl, member_list)
4. Declaraciones de Variable (var_decl, array_dims)
5. Sistema de Tipos (type, type_base)
6. Sentencias (statement, block, if_stmt, while_stmt, for_stmt, etc.)
7. Expresiones con Precedencia (14 niveles)
8. Reglas Léxicas (ID, ENTERO, FLOT, CADENA, etc.)
```

#### 2.2 Explicación Detallada de Secciones (6 min)

**A. Estructura del Programa** (1 min)
```ebnf
program ::= declaration_list
declaration_list ::= declaration+
declaration ::= function_decl | struct_decl | var_decl_stmt
```
- "Un programa SPL es una lista de declaraciones globales"
- "Puede tener funciones, estructuras y variables globales"
- "Requiere función 'principal()' como punto de entrada"

**B. Declaraciones de Función** (1 min)
```ebnf
normal_function_decl ::= 'funcion' type ID '(' param_list? ')' block
extern_function_decl ::= 'externo' 'funcion' type ID '(' param_list? ')' ';'
```
- "Funciones normales tienen cuerpo (block)"
- "Funciones externas son declaraciones sin implementación (para linking)"

**C. Declaraciones de Variable y Arrays** (1.5 min)
```ebnf
var_decl ::= type ID ('=' expression)?
           | type_base array_dims ID ('=' expression)?
           | 'constante' type ID '=' expression

array_dims ::= '[' ENTERO ']'
             | array_dims '[' ENTERO ']'
```
- **IMPORTANTE**: "array_dims es recursiva para soportar arreglos multidimensionales"
- "Ejemplo: `entero4[3][4]` → type_base=entero4, array_dims=[3][4]"
- "Las constantes requieren inicialización obligatoria"

**D. Expresiones con Precedencia** (2 min)
```
expression (nivel más alto)
  ↓
assignment (=, +=, -=, etc.)
  ↓
logical (||, &&)
  ↓
bitwise (|, ^, &)
  ↓
equality (==, !=)
  ↓
relational (<, <=, >, >=)
  ↓
additive (+, -)
  ↓
multiplicative (*, /, %)
  ↓
unary (!, -, ++, --, *, &)
  ↓
postfix (++, --, ., ->, [], ())
  ↓
primary (nivel más bajo)
```
- "14 niveles de precedencia eliminan ambigüedad"
- "Similar a C/C++ para familiaridad"
- "Asociatividad derecha para asignación: `a = b = c`"

**E. Sistema de Tipos** (0.5 min)
```ebnf
type ::= type_base | type '*'
type_base ::= 'entero2' | 'entero4' | 'entero8' | 'flotante' | ...
```
- "Soporta tipos primitivos y punteros"
- "Punteros se indican con '*' (similar a C)"

#### 2.3 Características Importantes (2 min)

**Recursión**:
- `array_dims` para arreglos multidimensionales
- `assignment` para asignaciones anidadas
- `postfix_op` para operaciones encadenadas

**Opcionalidad**:
- `param_list?` → funciones sin parámetros
- `statement_list?` → bloques vacíos válidos
- `expression?` → sentencias expresión opcionales

**Listas**:
- `declaration+` → mínimo una declaración
- `statement+` → mínimo una sentencia
- `(',' param)*` → cero o más parámetros adicionales

---

### PARTE 3: SEMÁNTICA (10 minutos)

#### Objetivo: Explicar la semántica de estructuras de control y TDAs

#### 3.1 Introducción a la Semántica (1 min)

**Abrir**: Sección 2.6 - Interpretación Semántica

"La semántica define QUÉ hace cada construcción del lenguaje, no solo su sintaxis"

**Componentes semánticos del compilador**:
1. **Análisis de tipos**: Verificar compatibilidad de operaciones
2. **Tabla de símbolos**: Rastrear declaraciones y scopes
3. **Generación de código**: Traducir construcciones de alto nivel a ensamblador

#### 3.2 Semántica de Estructuras de Control (5 min)

**A. Secuencia** (1 min)
```ebnf
statement_list ::= statement+
```

**Interpretación semántica**:
- Las sentencias se ejecutan en orden secuencial
- Cada sentencia puede modificar el estado del programa
- El control fluye de una sentencia a la siguiente

**Ejemplo**:
```c
entero4 a = 10;      // Sentencia 1: declaración con inicialización
a = a + 5;           // Sentencia 2: asignación
imprimir(a);         // Sentencia 3: impresión
```

**Acciones del compilador**:
1. Procesar cada sentencia en orden
2. Mantener scope actual y tabla de símbolos
3. Generar código secuencial en ensamblador
4. Cada sentencia genera instrucciones consecutivas

**B. Selección (if/si)** (2 min)
```ebnf
if_stmt ::= 'si' '(' expression ')' statement ('si_no' statement)?
```

**Interpretación semántica**:
- Evaluar la expresión como condición booleana
- Si es verdadera (≠ 0), ejecutar primer statement
- Si es falsa (= 0) y existe 'si_no', ejecutar segundo statement

**Acciones del compilador**:
1. Generar código para evaluar expression
2. Verificar que expression sea de tipo compatible con booleano
3. Generar salto condicional basado en resultado
4. Crear etiquetas para las ramas verdadera/falsa

**Código generado**:
```assembly
; Evaluar condición
[código de expression]
; Si R1 (resultado) es 0, saltar a else o fin
CMP R1, 0
JE else_label        ; Si es cero (falso), saltar

; Código del then
[código del statement1]
JMP end_if

else_label:
; Código del else (si existe)
[código del statement2]

end_if:
```

**C. Iteración (while/mientras)** (2 min)
```ebnf
while_stmt ::= 'mientras' '(' expression ')' statement
```

**Interpretación semántica**:
- Pre-condición: evaluar expresión antes de cada iteración
- Si es verdadera, ejecutar cuerpo y repetir
- Si es falsa, salir del bucle

**Acciones del compilador**:
1. Crear etiqueta de inicio del bucle
2. Evaluar condición
3. Generar salto condicional al final si es falso
4. Generar código del cuerpo
5. Generar salto incondicional al inicio
6. Validar uso de `romper` y `continuar` dentro del bucle

**Código generado**:
```assembly
loop_start:
    ; Evaluar condición
    [código de expression]
    CMP R1, 0
    JE loop_end        ; Si es cero (falso), salir
    
    ; Cuerpo del bucle
    [código del statement]
    
    JMP loop_start     ; Repetir
loop_end:
```

**Consideraciones especiales**:
- `romper` → genera JMP a loop_end
- `continuar` → genera JMP a loop_start
- Validación: verificar que estén dentro de un bucle

#### 3.3 Semántica de TDAs (Tipos Abstractos de Datos) (4 min)

**A. Estructuras (struct)** (2.5 min)
```ebnf
struct_decl ::= 'estructura' ID '{' member_list '}' ';'
member_list ::= member+
member ::= type ID ';'
```

**Interpretación semántica**:
- Define un tipo compuesto con campos nombrados
- Cada campo tiene su propio tipo y offset
- El tamaño total es la suma de tamaños de campos (más padding)

**Ejemplo**:
```c
estructura Punto {
    entero4 x;
    entero4 y;
};

estructura Rectangulo {
    Punto superior_izq;
    Punto inferior_der;
    entero4 color;
};
```

**Acciones del compilador**:
1. **Registro de tipo**:
   - Agregar tipo "Punto" a la tabla de tipos
   - Calcular tamaño: 2 × 4 bytes = 8 bytes
   
2. **Cálculo de offsets**:
   ```
   Punto:
     x: offset 0, tamaño 4
     y: offset 4, tamaño 4
   Total: 8 bytes
   
   Rectangulo:
     superior_izq: offset 0, tamaño 8 (estructura Punto)
     inferior_der: offset 8, tamaño 8
     color: offset 16, tamaño 4
   Total: 20 bytes (podría ser 24 con padding)
   ```

3. **Acceso a campos** (`p.x`):
   - Si `p` está en dirección `base`
   - `p.x` está en `base + 0`
   - `p.y` está en `base + 4`

4. **Generación de código**:
   ```assembly
   ; Para p.x = 10
   LOADV R1, 10           ; Cargar valor
   LOAD R2, [BP-8]        ; Cargar dirección de p
   STORE R1, [R2+0]       ; Guardar en campo x (offset 0)
   
   ; Para p.y = 20
   LOADV R1, 20
   LOAD R2, [BP-8]
   STORE R1, [R2+4]       ; Guardar en campo y (offset 4)
   ```

**B. Arreglos** (1.5 min)
```ebnf
array_dims ::= '[' ENTERO ']'
             | array_dims '[' ENTERO ']'
```

**Interpretación semántica**:
- Colección de elementos del mismo tipo en memoria contigua
- Acceso por índice con cálculo de offset
- Soporte para arreglos multidimensionales

**Ejemplo**:
```c
entero4[10] arr;          // Arreglo 1D
entero4[3][4] matriz;     // Arreglo 2D (3 filas, 4 columnas)
```

**Cálculo de direcciones**:
```
1D: base + índice × tamaño_elemento
   arr[i] → base + i × 4

2D (row-major): base + (fila × num_cols + col) × tamaño
   matriz[i][j] → base + (i × 4 + j) × 4
                → base + (4i + j) × 4

3D: base + ((plano × rows + fila) × cols + col) × tamaño
```

**Acciones del compilador**:
1. **Declaración**:
   - Calcular tamaño total: dims × tipo_base
   - Reservar espacio en stack o data
   - Ejemplo: `entero4[3][4]` → 3 × 4 × 4 = 48 bytes

2. **Acceso** (`arr[i]`):
   - Evaluar expresión de índice
   - Verificar límites (opcional, en tiempo de ejecución)
   - Calcular offset: índice × tamaño_elemento
   - Generar dirección: base + offset

3. **Generación de código**:
   ```assembly
   ; Para arr[i] = valor
   ; Suponer: arr en BP-100, i en R2, valor en R1
   
   LOADV R3, 4            ; Tamaño de entero4
   MUL R2, R3             ; R2 = i × 4 (offset)
   LOAD R4, BP            ; Base pointer
   SUB R4, 100            ; R4 = base de arr
   ADD R4, R2             ; R4 = arr + offset
   STORE R1, [R4]         ; Guardar valor
   ```

4. **Validaciones semánticas**:
   - Índices deben ser de tipo entero
   - No se permite arreglo de tipo `vacio`
   - Dimensiones deben ser constantes positivas

---

### PARTE 4: PREGUNTAS Y DEMOSTRACIONES ADICIONALES (30 minutos)

#### 4.1 Posibles Preguntas del Profesor

**Sobre la gramática**:
- ¿Por qué usaron recursión en `array_dims`?
  → "Para soportar arreglos de cualquier dimensión de forma natural"
  
- ¿Cómo resuelven la ambigüedad en expresiones?
  → "Con 14 niveles de precedencia explícitos en la gramática"
  
- ¿Por qué separaron `type` y `type_base`?
  → "Para soportar punteros: type puede ser type_base o type_base*"

**Sobre la semántica**:
- ¿Cómo manejan el scope de variables?
  → "Tabla de símbolos con scopes anidados, cada bloque crea nuevo scope"
  
- ¿Qué pasa si llaman a una función no declarada?
  → "El analizador semántico genera error en fase de análisis"
  
- ¿Cómo verifican tipos en expresiones?
  → "Cada nodo AST tiene tipo asociado, verificamos compatibilidad recursivamente"

**Sobre el preprocesador**:
- ¿Cómo funciona #include?
  → "Lee archivo, inserta contenido textualmente antes del análisis léxico"
  
- ¿Y #define?
  → "Tabla de macros, reemplaza tokens antes de lexer"

#### 4.2 Implementación en Vivo

**Prepararse para**:
- Agregar una funcionalidad pequeña
- Modificar un algoritmo existente
- Explicar una parte específica del compilador

**Ejemplos de tareas posibles**:

**A. Agregar operador de potencia** (15 min)
1. Modificar gramática (agregar `**` a multiplicative)
2. Actualizar lexer (nuevo token POW)
3. Agregar caso en generador de código
4. Probar con ejemplo simple

**B. Implementar estructura básica** (15 min)
```c
estructura Persona {
    entero4 edad;
    entero4 id;
};

funcion vacio principal() {
    Persona p;
    p.edad = 25;
    p.id = 12345;
    imprimir(p.edad, p.id);
}
```

**C. Agregar función de biblioteca** (10 min)
- Implementar en `lib/utils.asm`
- Declarar como externa
- Usar en programa de alto nivel

---

## 🎯 CONSEJOS PARA LA SUSTENTACIÓN

### Comunicación:
- Hablar claro y pausado
- Usar términos técnicos correctamente
- Explicar mientras se demuestra
- No asumir que el profesor conoce detalles

### Demostración:
- Tener todo probado previamente
- Si algo falla, tener plan B (otro ejemplo)
- Mostrar el flujo completo al menos una vez
- Destacar características únicas del lenguaje

### Trabajo en Equipo:
- Distribuir secciones entre miembros del grupo
- Uno habla, otro maneja la computadora
- Apoyarse mutuamente en preguntas difíciles

### Gestión del Tiempo:
- No extenderse demasiado en una sección
- Dejar tiempo para preguntas
- Si el profesor interrumpe, adaptarse

### Conocimiento Técnico:
- Conocer la gramática completa
- Entender el flujo de compilación
- Saber explicar decisiones de diseño
- Estar preparado para debugging en vivo

---

## 📚 DOCUMENTOS DE REFERENCIA RÁPIDA

### Durante la sustentación, tener abierto:

1. **GUI del Simulador** (src/main.py ejecutándose)
2. **Archivos de algoritmos**:
   - euclides_con_preprocesador.txt
   - multiplicacion_matrices_3d.txt
   - bubble_sort.txt
3. **Documentación Taller 2** (secciones 2.4, 2.5, 2.6)
4. **Código fuente del compilador** (por si preguntan implementación)

### Atajos útiles:
- `Ctrl + B`: Compilar en GUI
- `Ctrl + R`: Ejecutar en GUI
- `F10`: Paso a paso
- `F5`: Ejecutar automático

---

## ✅ CHECKLIST FINAL

### 5 minutos antes de la sustentación:

- [ ] GUI abierta y funcionando
- [ ] Algoritmos probados
- [ ] Documentación lista
- [ ] Dividir responsabilidades del grupo
- [ ] Respirar profundo y confiar en la preparación

### Durante la sustentación:

- [ ] Presentarse y presentar el proyecto
- [ ] Seguir la estructura de tiempo
- [ ] Demostrar con confianza
- [ ] Responder preguntas con claridad
- [ ] Agradecer al final

---

## 🎓 PUNTOS FUERTES A DESTACAR

1. **Compilador completo** con todas las fases
2. **Preprocesador funcional** (#include, #define)
3. **Gramática bien estructurada** (66 producciones)
4. **Diagramas de sintaxis completos** (visual)
5. **Semántica detallada** con generación de código
6. **Lenguaje expresivo** similar a C pero en español
7. **Ejecución real** en simulador de CPU propio
8. **Algoritmos validados** que funcionan

---

**¡MUCHA SUERTE EN LA SUSTENTACIÓN!** 🚀
