# Diagrama de la Gramática - Estructura Jerárquica

```
program
 └─ declaration_list
     └─ declaration (uno o más)
         ├─ function_decl
         │   ├─ normal_function_decl
         │   │   ├─ "funcion"
         │   │   ├─ type
         │   │   ├─ ID
         │   │   ├─ param_list (opcional)
         │   │   │   └─ param (uno o más)
         │   │   │       ├─ type
         │   │   │       └─ ID
         │   │   └─ block
         │   │       └─ statement_list (opcional)
         │   │           └─ statement (uno o más)
         │   └─ extern_function_decl
         │       ├─ "externo" "funcion"
         │       ├─ type
         │       ├─ ID
         │       └─ param_list (opcional)
         │
         ├─ struct_decl
         │   ├─ "estructura"
         │   ├─ ID
         │   └─ member_list
         │       └─ member (uno o más)
         │           ├─ type
         │           └─ ID
         │
         └─ var_decl_stmt
             └─ var_decl
                 ├─ Declaración simple
                 │   ├─ type
                 │   ├─ ID
                 │   └─ expression (opcional para inicialización)
                 ├─ Declaración de array
                 │   ├─ type_base
                 │   ├─ array_dims (uno o más)
                 │   │   └─ '[' ENTERO ']' (recursivo para N dimensiones)
                 │   ├─ ID
                 │   └─ expression (opcional para inicialización)
                 └─ Declaración de constante
                     ├─ "constante"
                     ├─ type
                     ├─ ID
                     └─ expression (requerido)
```

## Jerarquía de Tipos

```
type
 ├─ type_base
 │   ├─ Tipos primitivos
 │   │   ├─ "vacio"
 │   │   ├─ "entero2" / "entero4" / "entero8"
 │   │   ├─ "caracter" / "cadena"
 │   │   ├─ "flotante" / "doble"
 │   │   └─ "booleano"
 │   ├─ Modificadores
 │   │   ├─ "con_signo"
 │   │   └─ "sin_signo"
 │   └─ Tipos personalizados
 │       └─ ID (nombre de estructura)
 └─ Niveles de puntero
     └─ "*" (cero o más)

array_dims (Arrays Multidimensionales)
 └─ '[' ENTERO ']' (recursivo)
     ├─ [n] - Array 1D
     ├─ [n][m] - Array 2D (matriz)
     ├─ [n][m][k] - Array 3D (tensor)
     └─ ... (N dimensiones)
```

## Jerarquía de Sentencias

```
statement
 ├─ var_decl_stmt
 │   └─ Declaración de variable local
 │
 ├─ expr_stmt
 │   └─ expression (opcional) + ";"
 │
 ├─ if_stmt
 │   ├─ "si" "(" expression ")"
 │   ├─ statement (then)
 │   └─ "si_no" statement (opcional)
 │
 ├─ while_stmt
 │   ├─ "mientras" "(" expression ")"
 │   └─ statement (body)
 │
 ├─ for_stmt
 │   ├─ "para" "("
 │   ├─ for_init_opt (var_decl | expression | vacío)
 │   ├─ expr_opt (condition)
 │   ├─ expr_opt (increment)
 │   └─ ")" statement (body)
 │
 ├─ return_stmt
 │   └─ "retornar" [expression] ";"
 │
 ├─ break_stmt
 │   └─ "romper" ";"
 │
 ├─ continue_stmt
 │   └─ "continuar" ";"
 │
 ├─ print_stmt
 │   ├─ "imprimir" "("
 │   ├─ argument_list (opcional)
 │   └─ ")" ";"
 │
 └─ block
     └─ "{" statement_list "}"
```

## Jerarquía de Expresiones (por precedencia)

```
expression
 └─ assignment (asociatividad derecha)
     ├─ operators: =, +=, -=, *=, /=, %=
     └─ logical
         └─ logical_or (asociatividad izquierda)
             ├─ operator: ||
             └─ logical_and
                 ├─ operator: &&
                 └─ bitwise_or
                     ├─ operator: |
                     └─ bitwise_xor
                         ├─ operator: ^
                         └─ bitwise_and
                             ├─ operator: &
                             └─ equality
                                 ├─ operators: ==, !=
                                 └─ relational
                                     ├─ operators: <, <=, >, >=
                                     └─ additive
                                         ├─ operators: +, -
                                         └─ multiplicative
                                             ├─ operators: *, /, %
                                             └─ unary (asociatividad derecha)
                                                 ├─ operators: !, -, ++, --, *, &
                                                 └─ postfix (asociatividad izquierda)
                                                     ├─ operators: ++, --, ., ->, [], ()
                                                     └─ primary
                                                         ├─ ID
                                                         ├─ ENTERO
                                                         ├─ FLOT
                                                         ├─ CARACTER
                                                         ├─ CADENA
                                                         ├─ "(" expression ")"
                                                         ├─ new_expr
                                                         │   └─ "nuevo" type
                                                         └─ delete_expr
                                                             └─ "eliminar" unary
```

## Flujo de Análisis

```
┌─────────────────────────────────────────────────────────────┐
│                    CÓDIGO FUENTE                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PREPROCESADOR                              │
│  • Expandir macros (#define, .macro)                       │
│  • Incluir archivos (#include)                             │
│  • Procesamiento condicional                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ANALIZADOR LÉXICO (Lexer)                      │
│  • Convertir caracteres → tokens                           │
│  • Reconocer palabras reservadas                           │
│  • Identificar literales                                   │
│  • Tokens: ID, ENTERO, FUNCION, SI, MIENTRAS, etc.        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          ANALIZADOR SINTÁCTICO (Parser) ← ESTE              │
│  • Verificar estructura gramatical                          │
│  • Construir Árbol de Sintaxis Abstracta (AST)            │
│  • Detectar errores sintácticos                            │
│  • Precedencia y asociatividad de operadores               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         AST (Salida)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  FunctionDecl        StructDecl             VarDecl
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
            (Próxima fase: Analizador Semántico)
```

## Ejemplo de Parseo

### Ejemplo 1: Función recursiva
```c
funcion entero4 factorial(entero4 n) {
    si (n <= 1) {
        retornar 1;
    }
    retornar n * factorial(n - 1);
}
```

### Árbol AST generado:
```
Program
└── FunctionDecl: factorial
    ├── Return Type: entero4
    ├── Parameters:
    │   └── VarDecl: n (type: entero4)
    └── Body: Block
        └── IfStmt
            ├── Condition: BinaryOp (<=)
            │   ├── Left: Identifier (n)
            │   └── Right: IntLiteral (1)
            ├── Then: Block
            │   └── ReturnStmt
            │       └── IntLiteral (1)
            └── Else: ReturnStmt
                └── BinaryOp (*)
                    ├── Left: Identifier (n)
                    └── Right: FunctionCall
                        ├── Function: Identifier (factorial)
                        └── Arguments:
                            └── BinaryOp (-)
                                ├── Left: Identifier (n)
                                └── Right: IntLiteral (1)
```

### Ejemplo 2: Arrays multidimensionales
```c
funcion vacio principal() {
    entero4[3][3] matriz;
    matriz[0][0] = 1;
    matriz[0][1] = 2;
    matriz[1][0] = 3;
    imprimir(matriz[0][0], matriz[0][1]);
}
```

### Árbol AST generado:
```
Program
└── FunctionDecl: principal
    ├── Return Type: vacio
    ├── Parameters: (none)
    └── Body: Block
        ├── VarDecl: matriz
        │   ├── Type: entero4
        │   ├── Dimensions: [3, 3]
        │   └── Storage: Stack (36 bytes)
        ├── Assignment
        │   ├── Left: ArrayAccess
        │   │   ├── Array: ArrayAccess
        │   │   │   ├── Array: Identifier (matriz)
        │   │   │   └── Index: IntLiteral (0)
        │   │   └── Index: IntLiteral (0)
        │   └── Right: IntLiteral (1)
        ├── Assignment
        │   ├── Left: ArrayAccess
        │   │   ├── Array: ArrayAccess
        │   │   │   ├── Array: Identifier (matriz)
        │   │   │   └── Index: IntLiteral (0)
        │   │   └── Index: IntLiteral (1)
        │   └── Right: IntLiteral (2)
        ├── Assignment
        │   ├── Left: ArrayAccess
        │   │   ├── Array: ArrayAccess
        │   │   │   ├── Array: Identifier (matriz)
        │   │   │   └── Index: IntLiteral (1)
        │   │   └── Index: IntLiteral (0)
        │   └── Right: IntLiteral (3)
        └── PrintStmt
            └── Arguments:
                ├── ArrayAccess (matriz[0][0])
                └── ArrayAccess (matriz[0][1])
```

## Tabla de No Terminales por Categoría

| Categoría | No Terminales | Descripción |
|-----------|---------------|-------------|
| **Raíz** | `program`, `declaration_list`, `declaration` | Estructura principal del programa |
| **Funciones** | `function_decl`, `normal_function_decl`, `extern_function_decl`, `param_list`, `param` | Declaraciones de funciones |
| **Estructuras** | `struct_decl`, `member_list`, `member` | Definición de tipos compuestos |
| **Variables** | `var_decl_stmt`, `var_decl`, `array_dims` | Declaración de variables y arrays |
| **Tipos** | `type`, `type_base` | Sistema de tipos |
| **Sentencias Básicas** | `statement`, `block`, `statement_list`, `expr_stmt` | Sentencias fundamentales |
| **Control de Flujo** | `if_stmt`, `while_stmt`, `for_stmt`, `for_init_opt`, `expr_opt`, `return_stmt`, `break_stmt`, `continue_stmt` | Estructuras de control |
| **Entrada/Salida** | `print_stmt` | Operaciones de I/O |
| **Expresiones Lógicas** | `expression`, `assignment`, `logical`, `logical_or`, `logical_and` | Expresiones lógicas |
| **Expresiones Bitwise** | `bitwise_or`, `bitwise_xor`, `bitwise_and` | Operaciones bit a bit |
| **Expresiones Comparación** | `equality`, `relational` | Comparaciones |
| **Expresiones Aritméticas** | `additive`, `multiplicative` | Operaciones matemáticas |
| **Expresiones Unarias/Postfijas** | `unary`, `postfix`, `primary` | Operadores unarios y acceso |
| **Expresiones Especiales** | `new_expr`, `delete_expr`, `argument_list` | Gestión de memoria y llamadas |
| **Auxiliares** | `assignment_op`, `equality_op`, `relational_op`, `additive_op`, `multiplicative_op`, `unary_op`, `postfix_op`, `empty` | Operadores y reglas auxiliares |

**Total: 54 no terminales** (48 reglas principales + 6 reglas de operadores auxiliares)

## Estadísticas de la Gramática

- **No terminales**: 54 (incluye `array_dims` y `print_stmt`)
- **Terminales** (tokens): 60+ (incluyendo palabras reservadas, operadores, delimitadores)
- **Reglas de producción**: 85+ (aumentado con soporte de arrays multidimensionales)
- **Niveles de precedencia**: 12
- **Palabras reservadas**: 26 (incluye `imprimir`, `constante`)
- **Operadores**: 35+

## Características Destacadas

### Arrays Multidimensionales
- **Sintaxis**: `tipo[dim1][dim2]...[dimN] identificador;`
- **Ejemplos**:
  - `entero4[10] vector;` - Array 1D de 10 elementos
  - `entero4[3][3] matriz;` - Matriz 3×3 (9 elementos)
  - `entero4[2][3][4] tensor;` - Tensor 3D (24 elementos)
- **Acceso**: `matriz[i][j]` con sintaxis natural anidada
- **Almacenamiento**: Row-major contiguous (fila por fila)
- **Offset**: Calculado como `(i * D2 + j) * tamaño_elemento`

### Constantes
- **Sintaxis**: `constante tipo ID = expresion;`
- **Ejemplo**: `constante entero4 MAX = 100;`
- **Evaluación**: En tiempo de compilación

### Sistema de Impresión
- **Sintaxis**: `imprimir(expr1, expr2, ..., exprN);`
- **Formato**: Valores separados por espacios
- **Ejemplo**: `imprimir(a, b, c);` → "a b c"

## Validación

✅ Todos los no terminales están definidos  
✅ No hay símbolos indefinidos  
✅ No hay recursión infinita  
✅ La gramática es no ambigua (con tabla de precedencia)  
✅ Conflictos shift/reduce resueltos (8 esperados en if-else)  
✅ 1 conflicto reduce/reduce resuelto (ID como tipo vs identificador)  
