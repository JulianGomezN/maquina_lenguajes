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

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/euclides_librerias.txt`

**Conceptos teóricos del algoritmo**:
- **Máximo Común Divisor (MCD)**: El mayor número que divide exactamente a dos números
- **Algoritmo de Euclides**: Método eficiente basado en la propiedad: MCD(a,b) = MCD(b, a mod b)
- **Complejidad**: O(log min(a,b)) - muy eficiente incluso para números grandes
- **Caso base**: Cuando b=0, el MCD es a

**Puntos clave a mencionar**:
- ✅ Versión iterativa usando `mientras (b != 0)`
- ✅ Usa `#include` para incluir biblioteca (`lib/math_utils.h`)
- ✅ Usa `#define` para constantes (`VALOR_A=1071`, `VALOR_B=462`)
- ✅ Usa macro `CUADRADO(10)` que se expande a `((10) * (10))` = 100
- ✅ Demuestra preprocesador completo (inclusión y expansión de macros)

**Características del preprocesador demostradas**:
1. **#include "../lib/math_utils.h"**: 
   - Inclusión textual del archivo
   - Ruta relativa desde el archivo fuente
   - Procesado antes del análisis léxico
   
2. **#define con constantes**:
   - `VALOR_A 1071` → Reemplaza todas las ocurrencias de VALOR_A por 1071
   - `VALOR_B 462` → Reemplaza todas las ocurrencias de VALOR_B por 462
   
3. **#define con macros parametrizadas**:
   - `CUADRADO(x) ((x) * (x))` → Macro con parámetro
   - `CUADRADO(10)` se expande a `((10) * (10))`
   - Los paréntesis evitan problemas de precedencia

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

**Explicar en detalle**:
1. **Fase de Preprocesamiento**:
   - "El preprocesador lee math_utils.h y registra las macros PI, CUADRADO, EULER, GRAVEDAD"
   - "Luego procesa las definiciones locales VALOR_A y VALOR_B"
   - "Finalmente expande todas las macros: CUADRADO(10) → ((10) * (10)), VALOR_A → 1071, VALOR_B → 462"
   - "El resultado es código sin directivas, listo para el lexer"

2. **Algoritmo matemático**:
   - "Utilizamos la versión con módulo: temp = a % b"
   - "En cada iteración, a toma el valor de b, y b toma el valor de temp"
   - "Cuando b llega a cero, a contiene el MCD"
   - "Ejemplo: MCD(1071, 462) → 462, 147 → 147, 21 → 21, 0 → resultado: 21"

3. **Estructuras de control**:
   - "El `mientras` es una estructura de control pre-condicional"
   - "Evalúa la condición antes de ejecutar el cuerpo"
   - "Combinamos dos condiciones con AND lógico (&&): b != 0 y iteraciones < limite"
   - "El límite evita loops infinitos en caso de error"

4. **Gestión de memoria**:
   - "Variables locales (temp, iteraciones, limite) se almacenan en el stack"
   - "Se acceden mediante offsets desde el Base Pointer (BP)"
   - "Los parámetros (a, b) se pasan por valor en el stack"

#### 1.2 Multiplicación de Matrices (3-4 min)

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/multiplicacion_matrices_3d.txt`

**Conceptos teóricos de matrices**:
- **Matriz**: Arreglo bidimensional de elementos organizados en filas y columnas
- **Multiplicación de matrices**: Para C = A × B, cada elemento C[i][j] = Σ(A[i][k] × B[k][j])
- **Requisito**: Para multiplicar A(m×n) × B(n×p), el número de columnas de A debe ser igual al número de filas de B
- **Resultado**: Una matriz de dimensiones m×p
- **Complejidad**: O(n³) para matrices n×n con algoritmo básico

**Representación en memoria (row-major order)**:
```
Matriz 3×3:
[0][0] [0][1] [0][2]
[1][0] [1][1] [1][2]
[2][0] [2][1] [2][2]

En memoria lineal:
[0][0], [0][1], [0][2], [1][0], [1][1], [1][2], [2][0], [2][1], [2][2]

Dirección de [i][j] = base + (i × num_columnas + j) × tamaño_elemento
```

**Puntos clave**:
- ✅ Arreglos bidimensionales `entero4[3][3]`
- ✅ Acceso a elementos con índices dobles `matrizA[i][j]`
- ✅ Tres bucles anidados (i, j, k) para el algoritmo
- ✅ Algoritmo completo de multiplicación de matrices 3×3
- ✅ Uso de variables locales para optimización (`suma` acumula productos parciales)
- ✅ Demuestra manejo de memoria multidimensional

**Demostración**:
1. Cargar el archivo
2. Compilar (proceso más rápido, ya se mostró detallado)
3. Ejecutar y mostrar:
   - Matriz A (1,2,3; 4,5,6; 7,8,9)
   - Matriz B (9,8,7; 6,5,4; 3,2,1)
   - Resultado de A × B
4. Explicar el acceso a memoria para arreglos multidimensionales

**Explicar en detalle**:
1. **Organización de datos**:
   - "Declaramos tres matrices 3×3: matrizA, matrizB, resultado"
   - "Cada matriz ocupa 3 × 3 × 4 = 36 bytes en memoria"
   - "Los elementos se almacenan consecutivamente por filas (row-major)"
   - "Ejemplo: matrizA[1][2] está en offset (1×3+2)×4 = 20 bytes desde el inicio"

2. **Algoritmo de multiplicación**:
   - "Usamos tres bucles anidados: i (filas de A), j (columnas de B), k (producto punto)"
   - "Para cada posición [i][j] del resultado, calculamos: Σ A[i][k] × B[k][j] para k=0..2"
   - "Acumulamos en variable temporal 'suma' antes de asignar al resultado"
   - "Ejemplo: resultado[0][0] = A[0][0]×B[0][0] + A[0][1]×B[1][0] + A[0][2]×B[2][0]"

3. **Generación de código**:
   - "Cada acceso a[i][j] genera: dirección_base + (i×cols+j)×4"
   - "El compilador optimiza multiplicaciones constantes cuando es posible"
   - "Los índices se calculan en registros antes de acceder a memoria"

4. **Optimización**:
   - "Variable local 'suma' evita múltiples escrituras a memoria"
   - "Solo escribimos al resultado una vez por elemento, después del loop k"
   - "Los índices i, j, k se mantienen en registros durante los loops"

#### 1.3 Ordenamiento Burbuja (2-3 min)

**Archivo**: `Algoritmos/Ejemplos_alto_nivel/bubble_sort.txt`

**Conceptos teóricos del algoritmo**:
- **Bubble Sort**: Algoritmo de ordenamiento por comparación e intercambio
- **Funcionamiento**: Compara elementos adyacentes y los intercambia si están en orden incorrecto
- **Pasadas**: En cada pasada, el elemento más grande "burbujea" hacia el final
- **Complejidad**: 
  - Peor caso: O(n²) - arreglo en orden inverso
  - Mejor caso: O(n) - arreglo ya ordenado (con optimización)
  - Promedio: O(n²)
- **Estabilidad**: Es un algoritmo estable (mantiene orden relativo de elementos iguales)
- **In-place**: Ordena en el mismo arreglo, sin memoria adicional

**Análisis del algoritmo**:
```
Ejemplo con [64, 34, 25, 12, 22]:

Pasada 1: [34, 25, 12, 22, 64] - 64 llega al final
Pasada 2: [25, 12, 22, 34, 64] - 34 llega a su posición
Pasada 3: [12, 22, 25, 34, 64] - 25 llega a su posición
Pasada 4: [12, 22, 25, 34, 64] - Ya está ordenado
```

**Puntos clave**:
- ✅ Arreglo unidimensional `entero4[10]` con 10 elementos
- ✅ Dos bucles anidados con `mientras` (iteración controlada)
- ✅ Comparación de elementos adyacentes: `arr[j] > arr[j+1]`
- ✅ Intercambio usando variable temporal (swap pattern)
- ✅ Bucle externo controla pasadas (n-1 pasadas necesarias)
- ✅ Bucle interno recorre elementos no ordenados

**Demostración**:
1. Cargar archivo
2. Compilar y ejecutar
3. Mostrar:
   - Arreglo original: [64, 34, 25, 12, 22, 11, 90, 88, 45, 50]
   - Arreglo ordenado: [11, 12, 22, 25, 34, 45, 50, 64, 88, 90]

**Explicar en detalle**:
1. **Estructura del algoritmo**:
   - "Bucle externo (i): Controla el número de pasadas, de 0 a n-2"
   - "En cada pasada, al menos un elemento llega a su posición final"
   - "Bucle interno (j): Compara elementos adyacentes, de 0 a n-i-2"
   - "El límite j < n-i-1 se reduce porque los últimos i elementos ya están ordenados"

2. **Proceso de intercambio (swap)**:
   - "Comparamos arr[j] con arr[j+1]"
   - "Si arr[j] > arr[j+1], están en orden incorrecto"
   - "Usamos variable temporal para el intercambio:"
     ```
     temp = arr[j]
     arr[j] = arr[j+1]
     arr[j+1] = temp
     ```
   - "Esta es la operación fundamental del algoritmo"

3. **Acceso a arreglos**:
   - "arr[j] se traduce a: base_address + j × 4"
   - "arr[j+1] se traduce a: base_address + (j+1) × 4"
   - "El compilador calcula estos offsets y genera cargas/almacenamientos"

4. **Análisis de ejecución**:
   - "Primera pasada: 9 comparaciones, elemento mayor llega al final"
   - "Segunda pasada: 8 comparaciones, segundo mayor llega a su lugar"
   - "Última pasada: 1 comparación, todos están ordenados"
   - "Total de comparaciones: n(n-1)/2 en peor caso"

5. **Demostración de conceptos**:
   - "Bucles anidados con variables de control independientes"
   - "Expresiones relacionales (<, >) en condiciones"
   - "Acceso a elementos de arreglo con expresiones (j, j+1)"
   - "Asignaciones múltiples para operaciones complejas"

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

#### 2.2 Explicación Detallada de Secciones (8 min)

**A. Estructura del Programa** (1.5 min)
```ebnf
program ::= declaration_list
declaration_list ::= declaration+
declaration ::= function_decl | struct_decl | var_decl_stmt
```

**Conceptos fundamentales**:
- **Programa**: Unidad de compilación completa, contiene todas las declaraciones
- **declaration_list**: Secuencia de una o más declaraciones (+ significa "uno o más")
- **Orden de declaraciones**: Flexible, pero las estructuras deben declararse antes de usarse

**Explicación detallada**:
- "Un programa SPL es una lista de declaraciones globales"
- "Puede tener funciones, estructuras y variables globales en cualquier orden"
- "Requiere función 'principal()' como punto de entrada (similar a main en C)"
- "Las declaraciones se procesan en orden, construyendo la tabla de símbolos global"
- "El compilador valida que 'principal' exista y tenga la firma correcta"

**Ejemplo de programa válido**:
```c
// Declaración de estructura
estructura Punto { entero4 x; entero4 y; };

// Variable global
entero4 contador = 0;

// Función auxiliar
funcion entero4 duplicar(entero4 n) {
    retornar n * 2;
}

// Función principal (obligatoria)
funcion entero4 principal() {
    entero4 resultado = duplicar(21);
    retornar resultado;
}
```

**B. Declaraciones de Función** (1.5 min)
```ebnf
function_decl ::= normal_function_decl | extern_function_decl
normal_function_decl ::= 'funcion' type ID '(' param_list? ')' block
extern_function_decl ::= 'externo' 'funcion' type ID '(' param_list? ')' ';'
param_list ::= param (',' param)*
param ::= type ID
```

**Conceptos de funciones**:
- **Firma**: Combinación de nombre, tipo de retorno y tipos de parámetros
- **Prototipo**: Declaración sin implementación (función externa)
- **Definición**: Declaración con cuerpo/implementación
- **Linkage**: Proceso de conectar llamadas a funciones con sus definiciones

**Explicación detallada**:
- "Funciones normales tienen cuerpo (block) con implementación completa"
- "Funciones externas son declaraciones sin implementación, usadas para:"
  - "Funciones de biblioteca (como imprimir, definida en stdio.asm)"
  - "Funciones definidas en otros archivos (enlazadas después)"
  - "Funciones del sistema operativo o runtime"
- "El tipo de retorno puede ser cualquier tipo válido, incluyendo 'vacio'"
- "Los parámetros se pasan por valor (se copia el valor al stack)"
- "El '?' en param_list? indica que la lista de parámetros es opcional"

**Ejemplos**:
```c
// Función normal con implementación
funcion entero4 suma(entero4 a, entero4 b) {
    retornar a + b;
}

// Función externa (declaración)
externo funcion vacio imprimir(cadena msg);

// Función sin parámetros
funcion vacio saludar() {
    imprimir("Hola mundo");
}
```

**C. Declaraciones de Variable y Arrays** (2 min)
```ebnf
var_decl ::= type ID ('=' expression)?
           | type_base array_dims ID ('=' expression)?
           | 'constante' type ID '=' expression

array_dims ::= '[' ENTERO ']'
             | array_dims '[' ENTERO ']'
```

**Conceptos de variables**:
- **Variable simple**: Almacena un único valor de un tipo
- **Arreglo**: Colección indexada de elementos del mismo tipo
- **Constante**: Variable cuyo valor no puede cambiar después de la inicialización
- **Inicialización**: Asignación de valor inicial en la declaración
- **Declaración vs Definición**: En SPL, toda declaración es también una definición

**Explicación detallada**:

1. **Variables simples**:
   - "Sintaxis: tipo nombre = valor_inicial"
   - "La inicialización es opcional (se inicializa a 0 por defecto)"
   - "Ejemplo: `entero4 x = 10;` o `entero4 y;`"

2. **Arreglos**:
   - "**IMPORTANTE**: array_dims es recursiva para soportar arreglos de cualquier dimensión"
   - "Cada dimensión se especifica con un número entero constante entre corchetes"
   - "Dimensiones se procesan de izquierda a derecha"
   - "Ejemplo paso a paso para `entero4[3][4]`:"
     - "Primera aplicación de array_dims: [3]"
     - "Segunda aplicación recursiva: [3][4]"
     - "Resultado: arreglo 2D de 3 filas y 4 columnas"
   - "El tamaño total es: 3 × 4 × 4 bytes = 48 bytes"

3. **Constantes**:
   - "Las constantes DEBEN inicializarse en la declaración (obligatorio)"
   - "Su valor no puede cambiar durante la ejecución"
   - "Se verifica en tiempo de compilación (análisis semántico)"
   - "Útil para valores que no deben modificarse, como configuraciones"

**Ejemplos completos**:
```c
// Variables simples
entero4 edad = 25;
flotante pi = 3.14159;
caracter letra;  // Inicializado a 0

// Arreglos 1D
entero4[10] numeros;  // 10 enteros
flotante[5] temperaturas = {20.5, 21.0, 19.8, 22.3, 20.1};

// Arreglos 2D
entero4[3][4] matriz;  // 3 filas, 4 columnas

// Arreglos 3D
entero4[2][3][4] cubo;  // 2 planos de matrices 3×4

// Constantes
constante entero4 MAX_SIZE = 100;
constante flotante GRAVEDAD = 9.81;
```

**Procesamiento por el compilador**:
- "El compilador calcula el tamaño total necesario"
- "Reserva espacio en el stack (locales) o en segmento de datos (globales)"
- "Para arreglos multidimensionales, usa row-major order"
- "Las constantes se pueden optimizar (reemplazar por su valor en el código)"

**D. Expresiones con Precedencia** (2.5 min)
```
expression (nivel más alto - se evalúa último)
  ↓
assignment (=, +=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=)
  ↓
logical (||, &&)
  ↓
bitwise_or (|)
  ↓
bitwise_xor (^)
  ↓
bitwise_and (&)
  ↓
equality (==, !=)
  ↓
relational (<, <=, >, >=)
  ↓
shift (<<, >>)
  ↓
additive (+, -)
  ↓
multiplicative (*, /, %)
  ↓
unary (!, -, ++, --, *, &, sizeof, cast)
  ↓
postfix (++, --, ., ->, [], ())
  ↓
primary (nivel más bajo - se evalúa primero)
```

**Conceptos de expresiones**:
- **Precedencia**: Orden en que se evalúan operadores sin paréntesis
- **Asociatividad**: Dirección de evaluación para operadores de igual precedencia
- **Árbol de expresión**: Representación interna como AST (Abstract Syntax Tree)
- **Evaluación lazy**: Para operadores lógicos (short-circuit evaluation)

**Explicación detallada**:

1. **Por qué 14 niveles**:
   - "Cada nivel de precedencia elimina ambigüedad en expresiones complejas"
   - "Ejemplo: `a + b * c` → `a + (b * c)` porque * tiene mayor precedencia que +"
   - "Sin precedencia, necesitaríamos paréntesis en todas partes"

2. **Diseño similar a C/C++**:
   - "Los programadores están familiarizados con esta estructura"
   - "Hace el lenguaje más intuitivo y reduce errores"
   - "Facilita la portabilidad de código"

3. **Asociatividad**:
   - "Derecha a izquierda para asignación: `a = b = c` → `a = (b = c)`"
   - "Izquierda a derecha para la mayoría: `a - b - c` → `(a - b) - c`"
   - "Importante para operadores no conmutativos (-, /, %)"

4. **Ejemplos de precedencia en acción**:
   ```c
   // Sin paréntesis
   resultado = 2 + 3 * 4;           // → 2 + (3 * 4) = 14
   
   // Operadores relacionales vs lógicos
   si (a < 10 && b > 20)            // → (a < 10) && (b > 20)
   
   // Asignación múltiple
   x = y = z = 0;                    // → x = (y = (z = 0))
   
   // Incremento y suma
   resultado = ++a + b * c;          // → (++a) + (b * c)
   
   // Acceso a arreglo y suma
   suma = arr[i] + arr[i+1];         // → (arr[i]) + (arr[i+1])
   ```

5. **Construcción del AST**:
   - "El parser construye un árbol sintáctico basado en la precedencia"
   - "Operadores de menor precedencia quedan en la raíz"
   - "Operadores de mayor precedencia quedan en las hojas"
   - "Ejemplo para `a + b * c`:"
     ```
         +
        / \
       a   *
          / \
         b   c
     ```

6. **Evaluación short-circuit**:
   - "Para `a && b`: si a es falso, no evalúa b"
   - "Para `a || b`: si a es verdadero, no evalúa b"
   - "Optimización importante y comportamiento esperado"
   - "Genera código con saltos condicionales"

**E. Sistema de Tipos** (1 min)
```ebnf
type ::= type_base | type '*'
type_base ::= 'entero1' | 'entero2' | 'entero4' | 'entero8'
            | 'flotante' | 'caracter' | 'cadena' | 'vacio'
            | ID  /* para estructuras definidas por usuario */
```

**Conceptos del sistema de tipos**:
- **Tipo**: Clasificación que determina el tamaño, representación y operaciones válidas
- **Tipo primitivo**: Tipo básico del lenguaje (enteros, flotantes, caracteres)
- **Tipo derivado**: Construido a partir de otros tipos (punteros, arreglos, estructuras)
- **Type checking**: Verificación de compatibilidad de tipos en operaciones
- **Type casting**: Conversión explícita entre tipos

**Explicación detallada**:

1. **Tipos enteros** (con signo):
   - `entero1`: 1 byte (-128 a 127)
   - `entero2`: 2 bytes (-32,768 a 32,767)
   - `entero4`: 4 bytes (-2,147,483,648 a 2,147,483,647)
   - `entero8`: 8 bytes (-9,223,372,036,854,775,808 a 9,223,372,036,854,775,807)

2. **Tipo flotante**:
   - `flotante`: 4 bytes, IEEE 754 single precision
   - Rango aproximado: ±3.4 × 10³⁸
   - Precisión: ~7 dígitos decimales

3. **Tipos de texto**:
   - `caracter`: 1 byte, un carácter ASCII
   - `cadena`: Puntero a secuencia de caracteres terminada en NULL

4. **Tipo especial**:
   - `vacio`: Para funciones que no retornan valor

5. **Punteros** (type '*'):
   - "Se indican con asterisco después del tipo base (similar a C)"
   - "Ejemplos: `entero4*`, `flotante*`, `Punto*`"
   - "Un puntero almacena una dirección de memoria (8 bytes en arquitectura de 64 bits)"
   - "Permiten referencias indirectas y estructuras de datos dinámicas"

6. **Estructuras** (ID):
   - "Tipos definidos por usuario mediante `estructura`"
   - "Se referencian por su nombre (identificador)"
   - "Ejemplo: después de definir `estructura Punto`, usamos `Punto` como tipo"

**Verificación de tipos**:
- "El compilador verifica compatibilidad en asignaciones"
- "Ejemplo: no se puede asignar `flotante` a `entero4` sin conversión explícita"
- "Operaciones aritméticas requieren tipos compatibles"
- "Los punteros deben apuntar al tipo correcto"

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

#### 3.3 Semántica de TDAs (Tipos Abstractos de Datos) (5 min)

**Conceptos generales de TDAs**:
- **TDA**: Tipo de dato con operaciones definidas, ocultando detalles de implementación
- **Encapsulación**: Agrupar datos relacionados en una unidad
- **Abstracción**: Usar el tipo sin conocer su representación interna
- **Composición**: Construir tipos complejos a partir de tipos más simples

**A. Estructuras (struct)** (3 min)
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

**Validaciones semánticas para estructuras**:
1. No pueden haber ciclos de definición directa
2. Campos deben tener nombres únicos dentro de la estructura
3. No se puede instanciar estructura incompleta
4. Acceso a campos solo válido para variables de tipo estructura

**B. Arreglos** (2 min)
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
   - Número de índices debe coincidir con dimensiones del arreglo
   - Acceso fuera de límites (si se verifica) genera error en ejecución

**Optimizaciones del compilador**:
- Precalcular offsets cuando índices son constantes
- Strength reduction: convertir multiplicación por constante en sumas
- Loop unrolling: desenrollar bucles pequeños para acceso secuencial

---

### PARTE 4: PREGUNTAS Y DEMOSTRACIONES ADICIONALES (30 minutos)

#### 4.1 Posibles Preguntas del Profesor (Preparación Exhaustiva)

**CATEGORÍA 1: Gramática y Sintaxis**

**P1: ¿Por qué usaron recursión en `array_dims`?**
- **Respuesta básica**: "Para soportar arreglos de cualquier dimensión de forma natural"
- **Respuesta extendida**: 
  - "La recursión en `array_dims` permite definir arreglos multidimensionales sin limitar el número de dimensiones"
  - "Cada aplicación recursiva agrega una dimensión: [n], [n][m], [n][m][p], etc."
  - "Es más elegante que definir producciones separadas para 1D, 2D, 3D..."
  - "El parser construye una lista de dimensiones que luego usamos para calcular offsets"
  - "Alternativa sería usar `array_dims ::= ('[' ENTERO ']')+` pero la forma recursiva es más expresiva"

**P2: ¿Cómo resuelven la ambigüedad en expresiones?**
- **Respuesta básica**: "Con 14 niveles de precedencia explícitos en la gramática"
- **Respuesta extendida**:
  - "Sin precedencia, `a + b * c` sería ambiguo: ¿(a+b)*c o a+(b*c)?"
  - "Cada nivel de precedencia crea una producción separada en la gramática"
  - "Los niveles más altos (assignment) quedan en la raíz del árbol sintáctico"
  - "Los niveles más bajos (primary) quedan en las hojas"
  - "También especificamos asociatividad: izquierda para +,-, derecha para ="
  - "Ejemplo del parser: para `2+3*4`, el * se analiza primero por mayor precedencia"

**P3: ¿Por qué separaron `type` y `type_base`?**
- **Respuesta básica**: "Para soportar punteros: type puede ser type_base o type_base*"
- **Respuesta extendida**:
  - "`type_base` representa tipos fundamentales: entero4, flotante, estructura Punto, etc."
  - "`type` añade la posibilidad de punteros: type ::= type_base | type '*'"
  - "Esto permite `entero4*` (puntero a entero), `Punto*` (puntero a estructura)"
  - "También facilita punteros múltiples: `entero4**` (puntero a puntero)"
  - "Separación clara entre tipos concretos y tipos derivados"

**P4: ¿Cómo manejan el problema del dangling-else?**
- **Respuesta**: 
  - "El dangling-else ocurre en: `si (a) si (b) x=1; si_no y=1;` - ¿a cuál if pertenece el else?"
  - "Lo resolvemos con la regla: el `si_no` siempre se asocia al `si` más cercano sin emparejar"
  - "Esto se implementa naturalmente en gramáticas LL y LR por la forma de las producciones"
  - "Los usuarios pueden usar llaves {} para forzar otra interpretación"

**P5: ¿Por qué declaration_list usa + en lugar de * en EBNF?**
- **Respuesta**:
  - "El + significa 'uno o más', el * significa 'cero o más'"
  - "Un programa vacío no tiene sentido, debe tener al menos una declaración"
  - "Esto fuerza que exista mínimo la función principal()"
  - "Genera error en parse time si el archivo está vacío, no en análisis semántico"

---

**CATEGORÍA 2: Semántica y Análisis**

**P6: ¿Cómo manejan el scope de variables?**
- **Respuesta básica**: "Tabla de símbolos con scopes anidados, cada bloque crea nuevo scope"
- **Respuesta extendida**:
  - "Implementamos una pila de scopes (stack de diccionarios)"
  - "Al entrar a un bloque `{`, hacemos push de nuevo scope"
  - "Al salir del bloque `}`, hacemos pop del scope"
  - "Búsqueda de variables: empezamos por el scope más interno hacia afuera"
  - "Ejemplo: variable local oculta (shadow) variable global con el mismo nombre"
  - "Validamos: no se puede declarar dos veces la misma variable en un scope"

**P7: ¿Qué pasa si llaman a una función no declarada?**
- **Respuesta básica**: "El analizador semántico genera error en fase de análisis"
- **Respuesta extendida**:
  - "Mantenemos una tabla global de funciones declaradas"
  - "Al encontrar una llamada, verificamos que la función exista en la tabla"
  - "Si no existe, generamos error: 'Función [nombre] no declarada'"
  - "También verificamos: número de argumentos, tipos de argumentos, tipo de retorno"
  - "Las funciones externas permiten declarar sin definir (se resuelven en linking)"

**P8: ¿Cómo verifican tipos en expresiones?**
- **Respuesta básica**: "Cada nodo AST tiene tipo asociado, verificamos compatibilidad recursivamente"
- **Respuesta extendida**:
  - "Recorremos el AST en post-order (primero hijos, luego padre)"
  - "Cada nodo expresión tiene un método que retorna su tipo"
  - "Para operadores binarios: verificamos que operandos sean compatibles"
  - "Ejemplo: `a + b` verifica que a y b sean numéricos (entero o flotante)"
  - "Para asignaciones: tipo de expresión debe ser compatible con tipo de variable"
  - "Promoviones automáticas: entero4 → entero8, entero → flotante"
  - "Conversiones explícitas: cast necesario para conversiones inseguras"

**P9: ¿Cómo detectan variables no inicializadas?**
- **Respuesta**:
  - "En SPL, las variables se inicializan a 0 por defecto si no se da valor inicial"
  - "Esto evita el problema de variables no inicializadas"
  - "Alternativamente, podríamos hacer análisis de flujo de datos para detectar uso antes de asignación"
  - "Esto requiere analizar todos los caminos de ejecución posibles"

**P10: ¿Cómo validan que una función retorne un valor?**
- **Respuesta**:
  - "Verificamos que todas las rutas de ejecución terminen en `retornar` (si no es void)"
  - "Análisis de control flow: construimos grafo de flujo de control"
  - "Cada rama (if, while) debe tener retorno o converger en un retorno común"
  - "Si falta retorno, generamos warning o error según configuración"
  - "Funciones `vacio` no requieren retorno explícito (retorno implícito al final)"

---

**CATEGORÍA 3: Preprocesador**

**P11: ¿Cómo funciona #include?**
- **Respuesta básica**: "Lee archivo, inserta contenido textualmente antes del análisis léxico"
- **Respuesta extendida**:
  - "El preprocesador se ejecuta ANTES del lexer"
  - "Al encontrar `#include \"archivo.h\"`, abrimos el archivo"
  - "Copiamos su contenido completo en la posición del #include"
  - "Procesamos recursivamente el archivo incluido (puede tener sus propios #include)"
  - "Usamos path relativo al archivo que hace el #include"
  - "Guards evitan inclusión múltiple: #ifndef, #define, #endif"

**P12: ¿Y #define? ¿Cómo funcionan las macros?**
- **Respuesta básica**: "Tabla de macros, reemplaza tokens antes de lexer"
- **Respuesta extendida**:
  - "Mantenemos un diccionario de macros: nombre → expansión"
  - "Macros simples: `#define PI 3.14159` → reemplaza PI por 3.14159"
  - "Macros con parámetros: `#define CUADRADO(x) ((x)*(x))`"
  - "Al encontrar CUADRADO(5), sustituimos x por 5 en el cuerpo"
  - "Los paréntesis en la definición evitan problemas de precedencia"
  - "Ejemplo: CUADRADO(2+3) → ((2+3)*(2+3)) = 25, no 2+3*2+3 = 11"
  - "Es expansión textual, no evaluación: pasa tal cual al lexer"

**P13: ¿Qué problemas puede causar el preprocesador?**
- **Respuesta**:
  - "Macros sin paréntesis: `#define DOBLE(x) x*2` → DOBLE(3+4) = 3+4*2 = 11, no 14"
  - "Side effects: `#define MAX(a,b) ((a)>(b)?(a):(b))` → MAX(i++,j) evalúa i++ dos veces"
  - "Inclusiones circulares: A.h incluye B.h, B.h incluye A.h → loop infinito"
  - "Macros complejas difíciles de depurar: errores reportados en código expandido"
  - "Solución: usar funciones inline cuando sea posible"

---

**CATEGORÍA 4: Generación de Código**

**P14: ¿Cómo generan código para una asignación simple?**
- **Respuesta**:
  - "Para `x = expresión;`:"
  - "1. Generamos código para evaluar la expresión (resultado en registro)"
  - "2. Calculamos dirección de x (base + offset si es local)"
  - "3. Generamos STORE para guardar el registro en la dirección"
  - "Ejemplo: `x = a + 5;`"
    ```assembly
    LOAD R1, [BP-4]     ; Cargar a
    ADDV R1, 5          ; Sumar 5
    STORE R1, [BP-8]    ; Guardar en x
    ```

**P15: ¿Cómo manejan las llamadas a función?**
- **Respuesta**:
  - "Seguimos convención de llamada: parámetros en stack, retorno en R00"
  - "Antes de CALL:"
    - "1. Evaluar argumentos y hacer PUSH en orden inverso (derecha a izquierda)"
    - "2. CALL nombre_funcion (guarda dirección de retorno)"
  - "Dentro de la función:"
    - "3. PUSH BP (guardar base pointer del caller)"
    - "4. BP = SP (nuevo frame)"
    - "5. Reservar espacio para locales: SP += tamaño"
  - "Al retornar:"
    - "6. Colocar valor de retorno en R00"
    - "7. SP = BP (liberar locales)"
    - "8. POP BP (restaurar BP del caller)"
    - "9. RET (retorna a dirección guardada)"
  - "Después de RET:"
    - "10. Limpiar argumentos: SP += tamaño_args"

**P16: ¿Cómo optimizan el código generado?**
- **Respuesta**:
  - "Optimizaciones implementadas:"
    - "Constant folding: `3 + 4` → `7` en compile time"
    - "Dead code elimination: eliminar código después de return"
    - "Register allocation: mantener variables en registros cuando es posible"
    - "Peephole optimization: patrones pequeños (MOV R1,R2; MOV R2,R1 → eliminar)"
  - "Optimizaciones pendientes:"
    - "Common subexpression elimination: reusar resultados calculados"
    - "Loop unrolling: desenrollar bucles pequeños"
    - "Inline functions: expandir funciones pequeñas en lugar de CALL"

---

**CATEGORÍA 5: Arquitectura y Ejecución**

**P17: ¿Por qué diseñaron su propia arquitectura Atlas?**
- **Respuesta**:
  - "Propósitos educativos: control total sobre el hardware simulado"
  - "Simplificación: incluimos solo instrucciones necesarias para el lenguaje"
  - "Arquitectura de 64 bits con 16 registros de propósito general"
  - "Set de instrucciones RISC: instrucciones simples, composición de operaciones"
  - "Facilita demostración del flujo completo: código alto nivel → ensamblador → binario → ejecución"

**P18: ¿Cómo manejan los tipos de datos flotantes?**
- **Respuesta**:
  - "Usamos formato IEEE 754 single precision (32 bits)"
  - "Instrucciones especiales: FADD, FSUB, FMUL, FDIV"
  - "Conversiones: CVTF2I (float to int), CVTI2F (int to float)"
  - "Los flotantes no se pueden usar en operaciones lógicas o de bits"
  - "Comparaciones: CMPF genera flags Z, N, C basados en resta"

**P19: ¿Cómo funciona el sistema de memoria?**
- **Respuesta**:
  - "Memoria lineal de 64KB organizada en segmentos:"
    - "0x0000-0x0FFF: Código (4KB)"
    - "0x1000-0x2FFF: Datos globales (8KB)"
    - "0x3000-0x7FFF: String literals (20KB)"
    - "0x8000-0xBFFF: Heap (16KB) para malloc/free"
    - "0xC000-0xFFFF: Stack (16KB) crece hacia abajo"
  - "Stack pointer (R15) inicia en 0xC000"
  - "Base pointer (R14) marca inicio del frame actual"
  - "Heap crece hacia arriba, stack hacia abajo → máximo uso de memoria"

**P20: ¿Cómo implementan el sistema de I/O?**
- **Respuesta**:
  - "Memory-mapped I/O: direcciones especiales para dispositivos"
  - "0x100: Output port (SVIO escribe, SHOWIO muestra)"
  - "0x200: Input port (LOADIO lee carácter)"
  - "Funciones de biblioteca (stdio.asm):"
    - "PRINT_STRING: imprime cadena char por char"
    - "PRINT_INT: convierte número a ASCII y imprime"
    - "INPUT_STRING: lee hasta NULL (0x00)"
  - "Instrucciones especiales: SVIO, SHOWIO, LOADIO para I/O"

---

**CATEGORÍA 6: Máquina Virtual y Ejecución**

**P21: ¿Cómo funciona el ciclo de ejecución de la CPU Atlas?**
- **Respuesta**:
  - "Implementamos el ciclo clásico Fetch-Decode-Execute-Writeback"
  - "1. FETCH: Lee instrucción desde mem[PC], incrementa PC"
  - "2. DECODE: Extrae opcode y operandos, identifica tipo de instrucción"
  - "3. EXECUTE: Ejecuta operación en ALU, accede memoria si necesario"
  - "4. WRITEBACK: Escribe resultado en registro destino, actualiza flags"
  - "El PC se actualiza automáticamente excepto en saltos/llamadas"
  - "Los flags (Z, N, C, V) se actualizan según el resultado de operaciones"

**P22: ¿Por qué eligieron una arquitectura RISC para Atlas?**
- **Respuesta**:
  - "RISC simplifica el diseño del CPU: instrucciones uniformes, fácil decode"
  - "Set de instrucciones pequeño y consistente (vs CISC con cientos de instrucciones)"
  - "Cada instrucción ejecuta en un ciclo (o pocos ciclos), predecible"
  - "Facilita pipeline: todas las instrucciones tienen mismo formato"
  - "Load-store architecture: solo LOAD/STORE acceden memoria, resto usa registros"
  - "16 registros de propósito general permiten mantener datos en CPU"
  - "Más fácil de entender y enseñar con propósitos educativos"

**P23: ¿Cómo manejan el stack overflow y heap overflow?**
- **Respuesta**:
  - "El stack crece desde 0xFFFF hacia abajo, el heap desde 0x8000 hacia arriba"
  - "Se encuentran en 0xBFFF si hay colisión (límite entre heap y stack)"
  - "En la implementación actual, NO verificamos overflow automáticamente"
  - "Stack overflow ocurre si SP < 0x8000 (invade heap)"
  - "Heap overflow ocurre si heap_top > 0xC000 (invade stack)"
  - "Detección posible: verificar límites en PUSH y malloc"
  - "Consecuencias: corrupción de datos, comportamiento indefinido"
  - "Solución: programador debe limitar recursión y asignaciones dinámicas"

**P24: ¿Qué optimizaciones hace la CPU durante ejecución?**
- **Respuesta**:
  - "La CPU Atlas es simple, NO implementa optimizaciones de hardware como:"
    - "No hay pipeline (instrucciones no se solapan)"
    - "No hay cache (acceso directo a memoria)"
    - "No hay branch prediction (saltos siempre flush pipeline)"
    - "No hay out-of-order execution"
  - "Esto es intencional: prioriza claridad educativa sobre rendimiento"
  - "Las optimizaciones están en el compilador, no en el hardware"
  - "Ventaja: comportamiento 100% predecible, fácil de debuggear"

**P25: ¿Cómo se codifican las instrucciones en binario?**
- **Respuesta detallada**:
  - "Cada instrucción es de longitud variable:"
    - "Opcode: 1 byte (identifica la instrucción)"
    - "Operandos: 1-8 bytes cada uno según el tipo"
  - "Ejemplo: MOVV8 R01, 100"
    ```
    Byte 0: Opcode (MOVV8)
    Byte 1: Registro destino (R01 = 0x01)
    Bytes 2-9: Valor inmediato (100 en 64 bits)
    Total: 10 bytes
    ```
  - "Ejemplo: ADD8 R01, R02"
    ```
    Byte 0: Opcode (ADD8)
    Byte 1: Registro destino (R01)
    Byte 2: Registro fuente (R02)
    Total: 3 bytes
    ```
  - "El ensamblador convierte mnemonics a estos bytes"
  - "El CPU decodifica byte por byte según el opcode"

**P26: ¿Cómo funciona el sistema de interrupciones (si lo tienen)?**
- **Respuesta**:
  - "La arquitectura Atlas actual NO implementa interrupciones"
  - "Todas las operaciones son síncronas y polled (polling)"
  - "Para I/O: esperamos activamente (busy-wait) con LOADIO"
  - "Si implementáramos interrupciones:"
    - "Tabla de vectores de interrupción en memoria baja"
    - "Al recibir IRQ: guardar PC y flags, saltar a handler"
    - "Handler ejecuta, hace IRET que restaura estado"
    - "Tipos: I/O interrupt, timer, exception, trap"
  - "Ventaja sin interrupciones: más simple de entender"
  - "Desventaja: no hay multitasking real, I/O ineficiente"

**P27: ¿Cómo se implementa la GUI y el simulador?**
- **Respuesta**:
  - "Escrito en Python usando tkinter para interfaz gráfica"
  - "Componentes principales:"
    - "Editor de código con syntax highlighting"
    - "Panel de registros que muestra R00-R15 en tiempo real"
    - "Panel de memoria con vista hexadecimal"
    - "Panel de flags (Z, N, C, V)"
    - "Console de salida para I/O"
    - "Controles de ejecución: Step, Run, Stop, Reset"
  - "El simulador mantiene estado de CPU:"
    ```python
    class CPU:
        registers = [0] * 16  # R00-R15
        memory = [0] * 65536  # 64KB
        pc = 0
        flags = {'Z': 0, 'N': 0, 'C': 0, 'V': 0}
    ```
  - "Cada instrucción actualiza estado y refresca GUI"
  - "Modo paso a paso útil para debugging y enseñanza"

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
```c
// 1. Implementar en lib/utils.asm
abs_valor:
    PUSH8 R14
    MOV8 R14, R15
    MOV8 R03, R14
    SUBV8 R03, 24
    LOADR4 R01, R03     ; Cargar argumento
    CMPV R01, 0
    JGE abs_positive
    MOVV4 R02, 0
    SUB4 R02, R01
    MOV4 R01, R02
abs_positive:
    MOV4 R00, R01
    MOV8 R15, R14
    POP8 R14
    RET

// 2. Declarar como externa en programa
externo funcion entero4 abs_valor(entero4 n);

// 3. Usar en programa
funcion entero4 principal() {
    entero4 x = -15;
    entero4 resultado = abs_valor(x);
    imprimir("Valor absoluto: ", resultado);
    retornar 0;
}
```

---

### 4.3 Casos Especiales y Corner Cases

**Manejo de Errores Comunes**:

**Error 1: División por cero**
```c
funcion entero4 dividir(entero4 a, entero4 b) {
    si (b == 0) {
        imprimir("Error: división por cero");
        retornar -1;  // Código de error
    }
    retornar a / b;
}
```

**Error 2: Desbordamiento de enteros**
```c
// Para entero4 (32 bits con signo): -2,147,483,648 a 2,147,483,647
entero4 x = 2000000000;
entero4 y = 2000000000;
entero4 suma = x + y;  // Overflow! Resultado incorrecto
// Solución: usar entero8 o verificar antes de operar
```

**Error 3: Acceso fuera de límites**
```c
entero4[10] arr;
arr[15] = 5;  // Error! Índice fuera de rango
// En SPL: el compilador no verifica límites en runtime (por eficiencia)
// Responsabilidad del programador asegurar índices válidos
```

**Error 4: Uso de variable no inicializada**
```c
funcion entero4 mal_ejemplo() {
    entero4 x;  // Inicializado a 0 en SPL
    retornar x;  // En SPL: retorna 0, no es error
}
```

**Error 5: Return type mismatch**
```c
funcion entero4 obtener_valor() {
    flotante x = 3.14;
    retornar x;  // Error semántico: tipo incompatible
}
```

---

### 4.4 Depuración y Troubleshooting

**Estrategias de Depuración**:

1. **Errores Léxicos**:
   - Token no reconocido
   - Carácter ilegal
   - String sin cerrar
   - **Solución**: Revisar sintaxis básica, comillas, paréntesis

2. **Errores Sintácticos**:
   - Unexpected token
   - Missing semicolon
   - Parenthesis mismatch
   - **Solución**: Verificar estructura, balancear delimitadores

3. **Errores Semánticos**:
   - Tipo incompatible
   - Variable no declarada
   - Función no definida
   - **Solución**: Revisar declaraciones, tipos, scopes

4. **Errores de Ejecución**:
   - Segmentation fault (acceso memoria inválido)
   - Stack overflow (recursión infinita)
   - División por cero
   - **Solución**: Usar debugger, imprimir valores intermedios

**Técnicas de Debugging**:
- **Ejecución paso a paso**: F10 en GUI
- **Breakpoints**: Pausar en línea específica
- **Inspección de registros**: Ver valores en tiempo real
- **Stack trace**: Seguir llamadas a función
- **Print debugging**: Imprimir valores intermedios

---

### 4.5 Comparación con Otros Lenguajes

**SPL vs C**:

| Característica | SPL | C |
|---|---|---|
| Palabras clave | Español | Inglés |
| Tipos | entero4, flotante | int, float |
| Arrays | entero4[10] | int arr[10] |
| Estructuras | estructura | struct |
| Punteros | tipo* | tipo* |
| Funciones | funcion tipo nombre() | tipo nombre() |
| Control | si, mientras, para | if, while, for |
| E/S | imprimir(), leer() | printf(), scanf() |

**SPL vs Python**:

| Característica | SPL | Python |
|---|---|---|
| Tipado | Estático, fuerte | Dinámico, fuerte |
| Compilación | Compilado a binario | Interpretado (bytecode) |
| Declaración | Obligatoria con tipo | Opcional, sin tipo |
| Rendimiento | Rápido (nativo) | Más lento (interpretado) |
| Sintaxis | Similar a C | Más simple |

**Ventajas de SPL**:
- En español: más accesible para hispanohablantes
- Tipado estático: detecta errores en compile time
- Compilado: ejecución rápida
- Bajo nivel: control total sobre hardware

**Limitaciones de SPL**:
- Sin garbage collection: manejo manual de memoria
- Sin excepciones: manejo de errores básico
- Sin generics: no hay templates o tipos parametrizados
- Sin OOP completo: solo estructuras, no herencia/polimorfismo

---

---

## 📖 CONCEPTOS TEÓRICOS FUNDAMENTALES

### A. Notación EBNF y Análisis Sintáctico

#### ¿Qué es EBNF?

**EBNF (Extended Backus-Naur Form)** es una notación formal para describir la sintaxis de lenguajes de programación. Es una extensión de BNF que añade operadores para hacer las gramáticas más compactas y legibles.

**Componentes de EBNF**:

1. **Símbolos No Terminales**: Representan estructuras sintácticas (escritos en minúsculas)
   - Ejemplo: `expression`, `statement`, `declaration`

2. **Símbolos Terminales**: Tokens del lenguaje (escritos entre comillas o mayúsculas)
   - Ejemplo: `'si'`, `'mientras'`, `ID`, `ENTERO`

3. **Producciones**: Reglas que definen cómo se construyen los no terminales
   - Formato: `no_terminal ::= definición`

**Operadores EBNF**:

| Operador | Significado | Ejemplo | Equivalente |
|----------|-------------|---------|-------------|
| `|` | Alternativa (OR) | `a | b` | "a o b" |
| `?` | Opcional (0 o 1) | `a?` | "a o nada" |
| `*` | Cero o más | `a*` | "ninguno, uno o varios a" |
| `+` | Uno o más | `a+` | "uno o varios a" |
| `()` | Agrupación | `(a | b)` | "agrupa alternativas" |
| `::=` | Definición | `x ::= y` | "x se define como y" |

**Diferencias entre BNF y EBNF**:

```ebnf
// En BNF (más verboso):
statement_list ::= statement
                 | statement_list statement

// En EBNF (más compacto):
statement_list ::= statement+
```

#### Ejemplo Detallado de Interpretación EBNF

Tomemos una regla compleja de SPL:

```ebnf
var_decl ::= type ID ('=' expression)?
           | type_base array_dims ID ('=' expression)?
           | 'constante' type ID '=' expression
```

**Interpretación paso a paso**:

**Opción 1**: `type ID ('=' expression)?`
- Comienza con un `type` (puede ser entero4, flotante, etc.)
- Seguido de un `ID` (identificador, nombre de variable)
- Opcionalmente (`?`) puede tener `'=' expression` (inicialización)
- **Ejemplos válidos**:
  ```c
  entero4 x              // sin inicialización
  entero4 x = 10         // con inicialización
  flotante pi = 3.14     // con inicialización
  ```

**Opción 2**: `type_base array_dims ID ('=' expression)?`
- Comienza con `type_base` (tipo primitivo sin puntero)
- Seguido de `array_dims` (dimensiones del arreglo)
- Seguido de `ID` (nombre del arreglo)
- Opcionalmente puede tener inicialización
- **Ejemplos válidos**:
  ```c
  entero4[10] numeros                    // arreglo sin inicializar
  entero4[3][4] matriz                   // arreglo 2D
  flotante[5] temps = {1.0, 2.0, 3.0}   // con inicialización
  ```

**Opción 3**: `'constante' type ID '=' expression`
- **DEBE** comenzar con palabra clave `'constante'`
- Seguido de `type`
- Seguido de `ID`
- Seguido **obligatoriamente** de `'=' expression` (no hay `?`)
- **Ejemplos válidos**:
  ```c
  constante entero4 MAX = 100      // válido
  constante flotante PI = 3.14159  // válido
  ```
- **Ejemplos INVÁLIDOS**:
  ```c
  constante entero4 MAX;           // ERROR: falta inicialización
  ```

#### Ejemplo: Análisis de Expresiones con Precedencia

```ebnf
expression ::= assignment

assignment ::= logical (assignment_op assignment)?

assignment_op ::= '=' | '+=' | '-=' | '*=' | '/='

logical ::= bitwise_or (('||' | '&&') bitwise_or)*

bitwise_or ::= bitwise_xor ('|' bitwise_xor)*

bitwise_xor ::= bitwise_and ('^' bitwise_and)*

bitwise_and ::= equality ('&' equality)*

equality ::= relational (('==' | '!=') relational)*

relational ::= additive (('<' | '<=' | '>' | '>=') additive)*

additive ::= multiplicative (('+' | '-') multiplicative)*

multiplicative ::= unary (('*' | '/' | '%') unary)*

unary ::= ('!' | '-' | '++' | '--' | '*' | '&')? postfix

postfix ::= primary (postfix_op)*

postfix_op ::= '++' | '--' | '.' ID | '->' ID | '[' expression ']' | '(' arg_list? ')'

primary ::= ID | ENTERO | FLOT | CADENA | '(' expression ')'
```

**Análisis de la expresión**: `a + b * c`

1. **expression** → **assignment**
2. **assignment** → **logical** (no hay operador de asignación)
3. **logical** → **bitwise_or** (no hay || ni &&)
4. **bitwise_or** → **bitwise_xor** (no hay |)
5. **bitwise_xor** → **bitwise_and** (no hay ^)
6. **bitwise_and** → **equality** (no hay &)
7. **equality** → **relational** (no hay == ni !=)
8. **relational** → **additive** (no hay <, >, etc.)
9. **additive** → **multiplicative** `('+' multiplicative)*`
   - Detecta el `+`, entonces tenemos: multiplicative + multiplicative
10. Primera parte: **multiplicative** → **unary** (para 'a')
    - **unary** → **postfix** → **primary** → `ID` (a)
11. Segunda parte: **multiplicative** → **unary** `('*' unary)*`
    - Detecta el `*`, entonces: unary * unary
12. Primera parte del producto: **unary** → **postfix** → **primary** → `ID` (b)
13. Segunda parte del producto: **unary** → **postfix** → **primary** → `ID` (c)

**Árbol resultante**:
```
        additive (+)
       /            \
      a        multiplicative (*)
                   /          \
                  b            c
```

Esto demuestra cómo la precedencia está codificada en la estructura de la gramática: `*` se evalúa antes que `+` porque está más abajo en la jerarquía de producciones.

#### Ventajas de EBNF

1. **Compacidad**: Menos reglas que BNF puro
2. **Legibilidad**: Más fácil de entender para humanos
3. **Mantenibilidad**: Cambios más simples
4. **Documentación**: Sirve como especificación formal
5. **Generación automática**: Herramientas pueden generar parsers desde EBNF

#### De EBNF a Código (Parser)

Para cada no terminal en EBNF, creamos una función en el parser:

```python
# EBNF: statement ::= if_stmt | while_stmt | return_stmt

def parse_statement(self):
    if self.current_token.type == 'SI':
        return self.parse_if_stmt()
    elif self.current_token.type == 'MIENTRAS':
        return self.parse_while_stmt()
    elif self.current_token.type == 'RETORNAR':
        return self.parse_return_stmt()
    else:
        self.error("Expected statement")

# EBNF: if_stmt ::= 'si' '(' expression ')' statement ('si_no' statement)?

def parse_if_stmt(self):
    self.expect('SI')
    self.expect('LPAREN')
    condition = self.parse_expression()
    self.expect('RPAREN')
    then_stmt = self.parse_statement()
    
    else_stmt = None
    if self.current_token.type == 'SI_NO':
        self.expect('SI_NO')
        else_stmt = self.parse_statement()
    
    return IfNode(condition, then_stmt, else_stmt)
```

---

### B. Teoría de Compiladores

**Fases del Compilador**:
1. **Preprocesador**: Expande macros e incluye archivos
2. **Análisis Léxico (Lexer)**: Convierte caracteres → tokens
3. **Análisis Sintáctico (Parser)**: Tokens → AST (Abstract Syntax Tree)
4. **Análisis Semántico**: Verifica tipos, scopes, validaciones
5. **Generación de Código Intermedio**: AST → representación intermedia
6. **Optimización**: Mejora el código intermedio
7. **Generación de Código Final**: Intermedio → ensamblador
8. **Ensamblador**: Ensamblador → código binario
9. **Linker**: Resuelve símbolos externos, combina módulos
10. **Loader**: Carga binario en memoria y prepara ejecución

**Front-end vs Back-end**:
- **Front-end**: Análisis léxico, sintáctico, semántico (dependiente del lenguaje)
- **Back-end**: Generación de código, optimización (dependiente de la arquitectura)
- **Ventaja de separación**: Un front-end puede generar para múltiples arquitecturas

**Gramáticas**:
- **Gramática Libre de Contexto (CFG)**: Formalmente: G = (N, T, P, S)
  - N: símbolos no terminales (program, expression, statement)
  - T: símbolos terminales (tokens como 'si', '+', ID)
  - P: producciones (reglas de reescritura)
  - S: símbolo inicial (usualmente 'program')

- **Notación E-BNF**: Extensión de BNF con operadores:
  - `?` : opcional (cero o uno)
  - `*` : cero o más
  - `+` : uno o más
  - `|` : alternativa
  - `()`: agrupación

- **Parsing LL vs LR**:
  - **LL (Left-to-right, Leftmost)**: Parser predictivo, decide producción viendo siguiente token
  - **LR (Left-to-right, Rightmost)**: Parser shift-reduce, más potente que LL
  - SPL usa parser LL recursivo descendente (cada no-terminal → función)

**Tabla de Símbolos**:
- Estructura de datos central del compilador
- Almacena: nombre, tipo, scope, offset, atributos
- Operaciones: insert, lookup, delete (al salir de scope)
- Implementación: hash table para búsqueda O(1)
- Scope anidado: stack de tablas o lista enlazada

---

### B. Teoría de Lenguajes

**Sistema de Tipos**:
- **Tipado Fuerte vs Débil**:
  - Fuerte: No permite operaciones entre tipos incompatibles (SPL es fuerte)
  - Débil: Permite conversiones implícitas (JavaScript, C parcialmente)

- **Tipado Estático vs Dinámico**:
  - Estático: Tipos verificados en compile time (SPL, C, Java)
  - Dinámico: Tipos verificados en runtime (Python, JavaScript)

- **Type Safety**: Garantía de que operaciones no causen errores de tipo
- **Type Inference**: Deducir tipos sin declaración explícita (no en SPL, sí en Haskell/ML)

**Semántica Operacional**:
- Define significado de construcciones mediante reglas de evaluación
- **Small-step**: Evalúa un paso a la vez (útil para debugging)
- **Big-step**: Evalúa directamente a resultado final

**Ejemplo de regla semántica para while**:
```
⟨e, σ⟩ → ⟨true, σ'⟩    ⟨s, σ'⟩ → σ''    ⟨while e do s, σ''⟩ → σ'''
────────────────────────────────────────────────────────────────────
                  ⟨while e do s, σ⟩ → σ'''

⟨e, σ⟩ → ⟨false, σ'⟩
────────────────────────────
⟨while e do s, σ⟩ → σ'
```

**Closure y Scope**:
- **Scope léxico (estático)**: Basado en estructura del código fuente
- **Scope dinámico**: Basado en cadena de llamadas (poco común)
- **Closure**: Función que captura variables de scope externo

---

### C. Arquitectura de Computadoras

**Modelo de von Neumann**:
- Memoria unificada para datos e instrucciones
- CPU ejecuta instrucciones secuencialmente (fetch-decode-execute)
- Componentes: CPU (ALU + Control Unit), Memoria, I/O

**Arquitectura RISC vs CISC**:
- **RISC** (Reduced Instruction Set Computer):
  - Instrucciones simples, tamaño fijo
  - Más registros, load/store architecture
  - Atlas es RISC-like
- **CISC** (Complex Instruction Set Computer):
  - Instrucciones complejas, tamaño variable
  - Menos registros, operaciones memoria-memoria
  - x86 es CISC

**Pipeline de Instrucciones**:
1. **Fetch**: Leer instrucción de memoria
2. **Decode**: Interpretar opcode y operandos
3. **Execute**: Ejecutar operación en ALU
4. **Memory**: Acceder memoria si necesario
5. **Write-back**: Escribir resultado a registro

**Stack vs Heap**:
- **Stack**: LIFO, crece hacia abajo, variables locales, rápido, tamaño fijo
- **Heap**: Dinámico, malloc/free, crece hacia arriba, más lento, fragmentación

**Calling Convention**:
- **Caller-saved**: Caller guarda registros antes de CALL (volatiles)
- **Callee-saved**: Callee guarda registros al entrar (no volatiles)
- **Return value**: Usualmente en registro específico (R00 en Atlas)
- **Stack frame**: Estructura que contiene locales, params, return address

---

### D. Algoritmos y Complejidad

**Análisis de Complejidad**:
- **Notación O**: Cota superior asintótica
- **Notación Ω**: Cota inferior asintótica
- **Notación Θ**: Cota ajustada (cuando O = Ω)

**Complejidades Comunes**:
- O(1): Acceso a array por índice
- O(log n): Búsqueda binaria, algoritmo de Euclides
- O(n): Recorrido lineal de array
- O(n log n): Merge sort, quick sort (promedio)
- O(n²): Bubble sort, multiplicación de matrices naive
- O(n³): Multiplicación de matrices (algoritmo mostrado)
- O(2ⁿ): Problemas exponenciales (backtracking)

**Algoritmo de Euclides**:
- **Complejidad**: O(log min(a,b))
- **Propiedad fundamental**: MCD(a,b) = MCD(b, a mod b)
- **Prueba de correctitud**: Por inducción sobre el segundo argumento
- **Versión extendida**: Encuentra coeficientes de identidad de Bézout

**Multiplicación de Matrices**:
- **Naive**: O(n³) con 3 loops anidados
- **Strassen**: O(n^2.807) divide and conquer
- **Coppersmith-Winograd**: O(n^2.376) teórico
- **Óptimo**: Θ(n²) conjeturado pero no probado

---

### E. Estructuras de Datos

**Arrays**:
- **Acceso**: O(1) por índice calculado
- **Búsqueda**: O(n) lineal, O(log n) si ordenado
- **Inserción/Eliminación**: O(n) en general (shift elements)
- **Ventajas**: Acceso rápido, cache-friendly
- **Desventajas**: Tamaño fijo, inserción costosa

**Estructuras (Structs)**:
- Colección heterogénea de datos
- Acceso a campos por offset: O(1)
- Alineación de memoria (padding) para eficiencia
- Base para implementar objetos en OOP

**Abstract Data Types (ADT)**:
- Definición de operaciones sin especificar implementación
- Ejemplos: Stack, Queue, Priority Queue, Dictionary
- Permite cambiar implementación sin afectar código cliente

---

### F. Arquitectura de la Máquina Atlas

#### Especificaciones Generales

**Tipo de Arquitectura**: RISC de 64 bits con arquitectura load-store

**Características principales**:
- 16 registros de propósito general (R00-R15)
- Palabra de 64 bits (8 bytes)
- Espacio de direccionamiento: 64 KB (0x0000 - 0xFFFF)
- Set de instrucciones RISC (Reduced Instruction Set Computer)
- Memoria unificada (código y datos en el mismo espacio)

#### Registros del Procesador

**Registros de Propósito General**:
```
R00: Retorno de funciones / Acumulador general
R01-R13: Registros de trabajo general
R14: Base Pointer (BP) - Apunta al frame actual del stack
R15: Stack Pointer (SP) - Apunta al tope del stack
```

**Registros Especiales** (internos del CPU):
```
PC (Program Counter): Dirección de la siguiente instrucción
FLAGS: Registro de banderas (Zero, Negative, Carry, Overflow)
```

**Banderas (FLAGS)**:
- **Z (Zero)**: Se activa cuando resultado es cero
- **N (Negative)**: Se activa cuando resultado es negativo
- **C (Carry)**: Se activa en desbordamiento aritmético (unsigned)
- **V (Overflow)**: Se activa en desbordamiento aritmético (signed)

#### Organización de Memoria

**Mapa de Memoria (64 KB total)**:

```
0xFFFF ┌─────────────────────┐
       │                     │
       │   STACK (16 KB)     │ ← Crece hacia abajo
       │   (0xC000-0xFFFF)   │   desde 0xFFFF
0xC000 ├─────────────────────┤ ← SP inicial = 0xC000
       │                     │
       │   HEAP (16 KB)      │ ← Crece hacia arriba
       │   (0x8000-0xBFFF)   │   desde 0x8000
0x8000 ├─────────────────────┤
       │                     │
       │ STRING LITERALS     │
       │   (20 KB)           │
       │   (0x3000-0x7FFF)   │
0x3000 ├─────────────────────┤
       │                     │
       │ DATOS GLOBALES      │
       │   (8 KB)            │
       │   (0x1000-0x2FFF)   │
0x1000 ├─────────────────────┤
       │                     │
       │   CÓDIGO            │
       │   (4 KB)            │
       │   (0x0000-0x0FFF)   │
0x0000 └─────────────────────┘
```

**Detalles de cada segmento**:

1. **Segmento de Código (0x0000-0x0FFF)**:
   - Contiene instrucciones ejecutables
   - Bibliotecas (stdio.asm, memory.asm)
   - Código del programa principal
   - Tamaño: 4 KB

2. **Segmento de Datos Globales (0x1000-0x2FFF)**:
   - Variables globales
   - Datos estáticos
   - Tabla de free list para heap (en 0x1000)
   - Tamaño: 8 KB

3. **Segmento de String Literals (0x3000-0x7FFF)**:
   - Cadenas de texto del programa
   - Almacenadas como secuencias de bytes terminadas en NULL
   - Generadas en tiempo de compilación
   - Tamaño: 20 KB

4. **Heap (0x8000-0xBFFF)**:
   - Memoria dinámica (malloc/free)
   - Crece hacia arriba (hacia direcciones mayores)
   - Gestión mediante lista enlazada de bloques libres
   - Tamaño: 16 KB

5. **Stack (0xC000-0xFFFF)**:
   - Variables locales de funciones
   - Parámetros de funciones
   - Direcciones de retorno
   - Base pointers guardados
   - Crece hacia abajo (hacia direcciones menores)
   - Tamaño: 16 KB

#### Ciclo de Instrucción (Fetch-Decode-Execute)

```
┌─────────────────────────────────────────┐
│  1. FETCH (Capturar)                    │
│     - Leer instrucción en PC            │
│     - PC = PC + tamaño_instrucción      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. DECODE (Decodificar)                │
│     - Identificar opcode                │
│     - Extraer operandos                 │
│     - Determinar tipo de instrucción    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. EXECUTE (Ejecutar)                  │
│     - Realizar operación en ALU         │
│     - Acceder memoria si necesario      │
│     - Actualizar flags                  │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. WRITEBACK (Escribir resultado)      │
│     - Guardar resultado en registro     │
│     - Actualizar PC si es salto         │
└─────────────────────────────────────────┘
```

#### Set de Instrucciones (ISA - Instruction Set Architecture)

**Categorías de Instrucciones**:

**1. Movimiento de Datos**:
```assembly
MOV8 Rd, Rs          ; Rd = Rs (copia registro a registro)
MOVV8 Rd, inmediato  ; Rd = inmediato (carga valor inmediato)
LOAD Rd, [addr]      ; Rd = mem[addr] (carga desde memoria)
LOADR8 Rd, Rs        ; Rd = mem[Rs] (carga indirecta)
STORE Rd, [addr]     ; mem[addr] = Rd (guarda en memoria)
STORER8 Rd, Rs       ; mem[Rs] = Rd (guarda indirecta)
```

**2. Aritmética Entera**:
```assembly
ADD8 Rd, Rs          ; Rd = Rd + Rs
ADDV8 Rd, inm        ; Rd = Rd + inm
SUB8 Rd, Rs          ; Rd = Rd - Rs
SUBV8 Rd, inm        ; Rd = Rd - inm
MUL8 Rd, Rs          ; Rd = Rd * Rs
DIV8 Rd, Rs          ; Rd = Rd / Rs
MOD8 Rd, Rs          ; Rd = Rd % Rs
```

**3. Aritmética Flotante**:
```assembly
FADD4 Rd, Rs         ; Rd = Rd + Rs (float)
FSUB4 Rd, Rs         ; Rd = Rd - Rs (float)
FMUL4 Rd, Rs         ; Rd = Rd * Rs (float)
FDIV4 Rd, Rs         ; Rd = Rd / Rs (float)
```

**4. Operaciones Lógicas y de Bits**:
```assembly
AND8 Rd, Rs          ; Rd = Rd & Rs (AND bitwise)
OR8 Rd, Rs           ; Rd = Rd | Rs (OR bitwise)
XOR8 Rd, Rs          ; Rd = Rd ^ Rs (XOR bitwise)
NOT8 Rd              ; Rd = ~Rd (NOT bitwise)
SHL8 Rd, Rs          ; Rd = Rd << Rs (shift left)
SHR8 Rd, Rs          ; Rd = Rd >> Rs (shift right)
```

**5. Comparación y Saltos**:
```assembly
CMP Rd, Rs           ; Compara Rd con Rs, actualiza flags
CMPV Rd, inm         ; Compara Rd con inmediato
JMP label            ; Salto incondicional
JEQ label            ; Salto si igual (Z=1)
JNE label            ; Salto si no igual (Z=0)
JLT label            ; Salto si menor (N≠V)
JLE label            ; Salto si menor o igual (Z=1 o N≠V)
JGT label            ; Salto si mayor (Z=0 y N=V)
JGE label            ; Salto si mayor o igual (N=V)
```

**6. Control de Funciones**:
```assembly
CALL label           ; Llamar función (push PC, jump)
RET                  ; Retornar (pop PC)
PUSH8 Rd             ; Push registro al stack (SP-=8, mem[SP]=Rd)
POP8 Rd              ; Pop desde stack (Rd=mem[SP], SP+=8)
```

**7. Conversión de Tipos**:
```assembly
CVTF2I4 Rd, Rs       ; Rd = (int)Rs (float to int)
CVTI2F4 Rd, Rs       ; Rd = (float)Rs (int to float)
```

**8. I/O (Entrada/Salida)**:
```assembly
SVIO Rd, port        ; Escribir Rd al puerto
SHOWIO port          ; Mostrar contenido del puerto
LOADIO Rd, port      ; Leer del puerto a Rd
```

**9. Control**:
```assembly
PARAR                ; Detener ejecución (halt)
NOP                  ; No operation (sin operación)
```

#### Convención de Llamada a Funciones

**Estructura del Stack Frame**:
```
┌─────────────────────┐ ← SP al entrar a función
│  Variables locales  │
├─────────────────────┤ ← BP (Base Pointer)
│  BP anterior        │ (guardado)
├─────────────────────┤
│  Dirección retorno  │ (guardado por CALL)
├─────────────────────┤
│  Argumento N        │
│  Argumento N-1      │
│  ...                │
│  Argumento 1        │
└─────────────────────┘ ← SP antes de CALL
```

**Secuencia de Llamada**:

**En el Caller (quien llama)**:
```assembly
; 1. Evaluar argumentos y push al stack (orden inverso)
PUSH4 arg2
PUSH4 arg1

; 2. Llamar función
CALL nombre_funcion

; 3. Limpiar argumentos después de RET
ADDV8 R15, 8        ; Limpiar 2 argumentos de 4 bytes cada uno
```

**En el Callee (función llamada)**:
```assembly
nombre_funcion:
    ; PRÓLOGO
    PUSH8 R14           ; Guardar BP anterior
    MOV8 R14, R15       ; BP = SP (nuevo frame)
    ADDV8 R15, N        ; Reservar N bytes para locales
    
    ; CUERPO DE LA FUNCIÓN
    ; ...
    MOV4 R00, resultado ; Colocar valor de retorno en R00
    
    ; EPÍLOGO
    MOV8 R15, R14       ; SP = BP (liberar locales)
    POP8 R14            ; Restaurar BP anterior
    RET                 ; Retornar (pop PC)
```

**Acceso a Parámetros y Locales**:
```assembly
; Parámetros (offsets negativos desde BP)
; arg1 está en BP - 20 (si es entero4)
; arg2 está en BP - 24

MOV8 R01, R14
SUBV8 R01, 20
LOADR4 R02, R01     ; R02 = arg1

; Variables locales (offsets positivos desde BP)
; local1 está en BP + 0
; local2 está en BP + 4

MOV8 R03, R14
ADDV8 R03, 0
LOADR4 R04, R03     ; R04 = local1
```

#### Sistema de I/O (Entrada/Salida)

**Puertos de I/O (Memory-Mapped)**:
```
0x100: Puerto de salida (output)
0x200: Puerto de entrada (input)
```

**Operaciones básicas**:
```assembly
; Escribir carácter
MOVV1 R01, 65       ; ASCII 'A'
SVIO R01, 0x100     ; Escribir al puerto
SHOWIO 0x100        ; Mostrar en pantalla

; Leer carácter
LOADIO R01, 0x200   ; Leer del puerto
; R01 contiene 0xFF si no hay entrada
; R01 contiene código ASCII si hay carácter
```

#### Gestión de Memoria Dinámica (Heap)

**Estructura de Bloque en Heap**:
```
┌────────────────┐
│ Tamaño (8B)    │ ← Tamaño del bloque de datos
├────────────────┤
│ Siguiente (8B) │ ← Puntero al siguiente bloque libre
├────────────────┤
│                │
│  Datos         │ ← Área útil que se retorna al usuario
│                │
└────────────────┘
```

**malloc(tamaño)**:
1. Buscar en free_list un bloque ≥ tamaño
2. Si se encuentra:
   - Quitar de free_list
   - Retornar dirección + 16 (saltar header)
3. Si no se encuentra:
   - Retornar NULL (0)

**free(puntero)**:
1. Retroceder 16 bytes para obtener header
2. Insertar bloque al inicio de free_list
3. (No hace coalescing - simplificación)

---

### G. Optimización de Código

**Optimizaciones a Nivel de Expresión**:
- **Constant Folding**: Evaluar expresiones constantes en compile time
  - `3 + 4 * 2` → `11`
- **Constant Propagation**: Sustituir variables por sus valores constantes
  - `x = 5; y = x + 3;` → `y = 8;`
- **Algebraic Simplification**: Simplificar expresiones algebraicas
  - `x * 0` → `0`
  - `x + 0` → `x`
  - `x * 1` → `x`

**Optimizaciones a Nivel de Control**:
- **Dead Code Elimination**: Eliminar código inalcanzable
  ```c
  if (true) { a; } else { b; }  →  a;
  return x; y = 5;  →  return x;
  ```
- **Loop Unrolling**: Desenrollar bucles pequeños
  ```c
  for (i=0; i<4; i++) a[i] = 0;
  →
  a[0]=0; a[1]=0; a[2]=0; a[3]=0;
  ```

**Optimizaciones a Nivel de Datos**:
- **Common Subexpression Elimination (CSE)**:
  ```c
  a = b * c + d;
  e = b * c + f;
  →
  temp = b * c;
  a = temp + d;
  e = temp + f;
  ```
- **Strength Reduction**: Reemplazar operaciones costosas por baratas
  - `x * 2` → `x + x` o `x << 1`
  - `x / 2` → `x >> 1` (para enteros sin signo)

**Optimizaciones de Registros**:
- **Register Allocation**: Asignar variables a registros
  - Graph coloring algorithm
  - Variables más usadas en registros, menos usadas en memoria
- **Register Spilling**: Cuando no hay registros suficientes, guardar en memoria

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
