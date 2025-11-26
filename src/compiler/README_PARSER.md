# Analizador Sintáctico

Implementación de un analizador sintáctico (parser) usando PLY Yacc para el lenguaje de programación de alto nivel con sintaxis tipo-C y palabras clave en español.

## Archivos Principales

### `compiler/ast_nodes.py`
Define todos los nodos del Árbol de Sintaxis Abstracta (AST):
- **Declaraciones**: `FunctionDecl`, `StructDecl`, `VarDecl`
- **Sentencias**: `IfStmt`, `WhileStmt`, `ForStmt`, `ReturnStmt`, `BreakStmt`, `ContinueStmt`, `Block`, `ExprStmt`
- **Expresiones**: `BinaryOp`, `UnaryOp`, `Assignment`, `FunctionCall`, `MemberAccess`, `ArrayAccess`, `NewExpr`, `DeleteExpr`
- **Literales**: `IntLiteral`, `FloatLiteral`, `StringLiteral`, `CharLiteral`, `Identifier`

Cada nodo incluye información de línea (`lineno`) y posición (`lexpos`) para reportar errores.

### `compiler/syntax_analizer.py`
Implementación del parser con PLY Yacc:
- Reglas gramaticales BNF para todo el lenguaje
- Tabla de precedencia de operadores
- Manejo de errores con recuperación en modo pánico
- Función `parse(code)` para parsear código fuente

### `compiler/ast_printer.py`
Utilidad para visualizar el AST de forma jerárquica y legible.

## Características del Lenguaje

### Palabras Reservadas
- **Control de flujo**: `si`, `si_no`, `mientras`, `para`, `romper`, `continuar`
- **Tipos**: `vacio`, `entero2`, `entero4`, `entero8`, `caracter`, `cadena`, `flotante`, `doble`, `booleano`
- **Modificadores**: `constante`, `con_signo`, `sin_signo`
- **Declaraciones**: `funcion`, `estructura`, `externo`
- **Memoria**: `nuevo`, `eliminar`
- **Retorno**: `retornar`

### Operadores (por precedencia)

1. **Postfijos** (mayor precedencia): `++`, `--`, `.`, `->`, `[]`, `()`
2. **Unarios**: `!`, `-`, `++`, `--`, `*` (desreferencia), `&` (dirección)
3. **Multiplicativos**: `*`, `/`, `%`
4. **Aditivos**: `+`, `-`
5. **Relacionales**: `<`, `<=`, `>`, `>=`
6. **Igualdad**: `==`, `!=`
7. **AND bitwise**: `&`
8. **XOR bitwise**: `^`
9. **OR bitwise**: `|`
10. **AND lógico**: `&&`
11. **OR lógico**: `||`
12. **Asignación** (menor precedencia): `=`, `+=`, `-=`, `*=`, `/=`, `%=`

### Sintaxis

#### Funciones
```c
funcion entero4 sumar(entero4 a, entero4 b) {
    retornar a + b;
}

funcion vacio principal() {
    entero4 resultado = sumar(10, 20);
}

externo funcion vacio imprimir(cadena texto);
```

#### Estructuras
```c
estructura Persona {
    cadena nombre;
    entero4 edad;
    flotante altura;
};

funcion vacio test() {
    Persona p;
    p.edad = 25;
    
    Persona* ptr = nuevo Persona;
    ptr->nombre = "Juan";
    eliminar ptr;
}
```

#### Variables
```c
entero4 x = 10;
constante entero4 MAX = 100;
flotante pi = 3.14;
cadena mensaje = "Hola";
caracter letra = 'A';
entero4* puntero;
```

#### Control de Flujo
```c
// If-else
si (x < 10) {
    x = x + 1;
} si_no {
    x = x - 1;
}

// While
mientras (i < 10) {
    i += 1;
    si (i == 5) {
        continuar;
    }
}

// For
para (entero4 i = 0; i < 10; i++) {
    si (i == 7) {
        romper;
    }
}
```

## Uso

### Análisis Sintáctico Básico
```bash
# Windows PowerShell
$env:PYTHONPATH="."
Get-Content archivo.txt | python .\compiler\syntax_analizer.py
```

### Visualización del AST
```bash
# Windows PowerShell
$env:PYTHONPATH="."
Get-Content archivo.txt | python .\compiler\ast_printer.py
```

### Uso Programático
```python
from compiler.syntax_analizer import parse
from compiler.ast_printer import print_ast

# Leer código
with open('programa.txt', 'r') as f:
    code = f.read()

# Parsear
ast = parse(code)

if ast:
    # Visualizar AST
    print_ast(ast)
    
    # Procesar AST
    for decl in ast.declarations:
        print(f"Declaración: {decl}")
else:
    print("Error de sintaxis")
```

## Pruebas

### Ejecutar Todas las Pruebas
```bash
python -m unittest test_syntax_analizer.TestSyntaxAnalizer -v
```

### Ejecutar Prueba Específica
```bash
python -m unittest test_syntax_analizer.TestSyntaxAnalizer.test_simple_function -v
```

### Suite de Pruebas
- `test_simple_function`: Función sin parámetros
- `test_function_with_params`: Función con parámetros
- `test_variable_declarations`: Declaraciones de variables
- `test_const_declaration`: Constantes
- `test_if_statement`, `test_if_else_statement`: Condicionales
- `test_while_loop`, `test_for_loop`: Ciclos
- `test_return_statement`: Retornos
- `test_break_continue`: Break y continue
- `test_binary_operations`: Operaciones binarias
- `test_logical_operations`: Operaciones lógicas
- `test_assignment_operators`: Asignación compuesta
- `test_increment_decrement`: ++ y --
- `test_function_call`: Llamadas a funciones
- `test_struct_declaration`: Estructuras
- `test_member_access`: Acceso a miembros (`.` y `->`)
- `test_array_access`: Acceso a arrays
- `test_new_delete`: Operadores `nuevo` y `eliminar`
- `test_pointer_type`: Tipos puntero
- `test_extern_function`: Funciones externas
- `test_complex_expression`: Expresiones complejas
- `test_nested_blocks`: Bloques anidados
- `test_ejemplo_alto_nivel_1`: Archivo de ejemplo completo

## Gramática Formal

La gramática está implementada en formato BNF dentro del archivo `syntax_analizer.py`. Las reglas principales son:

```bnf
program ::= declaration_list

declaration ::= function_decl | struct_decl | var_decl_stmt

function_decl ::= FUNCION type ID '(' params? ')' block
                | EXTERNO FUNCION type ID '(' params? ')' ';'

struct_decl ::= ESTRUCTURA ID '{' member_list '}' ';'

var_decl ::= type ID ('=' expression)?
           | CONSTANTE type ID '=' expression

type ::= type_base ('*')*

statement ::= var_decl_stmt | expr_stmt | if_stmt | while_stmt 
            | for_stmt | return_stmt | break_stmt | continue_stmt | block

expression ::= assignment ::= logical (op assignment)* | logical
```

## Manejo de Errores

El parser incluye:
- **Detección de errores**: Reporta línea, token y contexto del error
- **Recuperación en modo pánico**: Continúa parseando después de errores
- **Mensajes informativos**: Muestra el contexto alrededor del error

Ejemplo de salida de error:
```
Error de sintaxis en línea 5, token 'PUNTOCOMA' con valor ';'
Contexto: ...entero4 x = 10;...
```

## Conflictos del Parser

El parser tiene algunos conflictos shift/reduce que son esperados:
- **8 shift/reduce conflicts**: Principalmente en expresiones if-else anidadas (ambigüedad del "dangling else")
- **1 reduce/reduce conflict**: Entre ID como tipo (nombre de estructura) y ID como identificador en expresiones primarias

Estos conflictos se resuelven automáticamente por PLY usando las reglas de precedencia definidas.

## Integración

El analizador sintáctico forma parte de la pipeline de compilación:

```
Código Fuente
    ↓
Preprocesador (macros, includes)
    ↓
Analizador Léxico (tokens)
    ↓
[Analizador Sintáctico] ← ESTE MÓDULO
    ↓
AST
    ↓
[Analizador Semántico] ← PRÓXIMO PASO
    ↓
Generador de Código
```

El AST generado está listo para ser consumido por un analizador semántico que validará:
- Tipos de datos
- Alcance de variables
- Declaraciones antes de uso
- Número de parámetros en llamadas
- Y otras validaciones semánticas

## Notas de Implementación

1. **Tokens específicos vs KEYWORD genérico**: Se usan tokens específicos (`SI`, `MIENTRAS`, `FUNCION`, etc.) en lugar de un token genérico `KEYWORD` para evitar conflictos reduce/reduce en el parser.

2. **Tipos como objetos**: Los tipos se representan como objetos `Type` con atributo `is_pointer` para facilitar el análisis semántico posterior.

3. **Información de línea**: Todos los nodos AST incluyen `lineno` y `lexpos` para reportar errores en fases posteriores.

4. **For loops flexibles**: El inicializador del `for` acepta tanto declaraciones de variables como expresiones.

5. **Acceso a miembros**: Se distingue entre `.` (acceso directo) y `->` (acceso por puntero) mediante el token `FLECHA`.
