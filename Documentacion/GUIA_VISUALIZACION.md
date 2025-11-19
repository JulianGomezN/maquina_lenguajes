# Guía Rápida: Visualizar la Gramática EBNF

## 🎯 Objetivo

Generar diagramas de sintaxis ferroviaria (railroad diagrams) para visualizar la gramática del lenguaje.

## 📁 Archivos Disponibles

1. **`gramatica.ebnf`** - Gramática completa (todas las reglas)
2. **`gramatica_simple.ebnf`** - Versión simplificada para pruebas rápidas

## 🚀 Pasos Rápidos

### Opción 1: Railroad Diagram Generator (Recomendado)

1. Abrir <https://www.bottlecaps.de/rr/ui>

2. Copiar el contenido de `gramatica.ebnf` o `gramatica_simple.ebnf`

3. Pegar en el editor de la herramienta

4. Click en **"Display Diagram"**

5. Explorar las reglas navegando por los enlaces

### Opción 2: Probar reglas específicas

Si la gramática completa es muy grande, puedes copiar solo las secciones que te interesen:

**Para ver declaración de funciones:**

```ebnf
function_decl ::= normal_function_decl | extern_function_decl

normal_function_decl ::= 'funcion' type ID '(' param_list? ')' block

param_list ::= param (',' param)*

param ::= type ID

block ::= '{' statement* '}'

type ::= type_base '*'*

type_base ::= 'vacio' | 'entero4' | 'flotante' | ID

statement ::= var_decl | expr_stmt | if_stmt | return_stmt
```

**Para ver jerarquía de expresiones:**

```ebnf
expression ::= assignment

assignment ::= logical (('=' | '+=') assignment)?

logical ::= equality ('&&' equality)*

equality ::= additive (('==' | '!=') additive)*

additive ::= multiplicative (('+' | '-') multiplicative)*

multiplicative ::= unary (('*' | '/') unary)*

unary ::= ('!' | '-') unary | primary

primary ::= ID | NUMERO | '(' expression ')'
```

## 📊 Qué verás

Los diagramas muestran visualmente:

- **Caminos obligatorios** - Línea principal
- **Opciones** - Bifurcaciones
- **Repeticiones** - Bucles
- **Alternativas** - Múltiples caminos

### Ejemplo de diagrama:

Para la regla:

```ebnf
if_stmt ::= 'si' '(' expression ')' statement ('si_no' statement)?
```

Verás un diagrama que muestra:

1. Palabra clave `si` (obligatoria)
2. Paréntesis abierto `(` (obligatorio)
3. Expresión (obligatoria)
4. Paréntesis cerrado `)` (obligatorio)
5. Sentencia (obligatoria)
6. Bifurcación opcional hacia `si_no` + sentencia

## ✅ Verificaciones

La herramienta automáticamente verifica:

- ✓ Sintaxis EBNF correcta
- ✓ No hay reglas sin definir
- ✓ No hay recursión infinita a la izquierda
- ✓ Todas las referencias son válidas

Si carga sin errores = gramática válida ✓

## 🎨 Exportar Diagramas

Una vez generados:

1. **Clic derecho** en cualquier diagrama
2. **"Guardar imagen como..."** o **"Copiar imagen"**
3. Formato: SVG (escalable) o PNG

## 🔍 Reglas Principales para Explorar

| Regla | Descripción |
|-------|-------------|
| `program` | Punto de entrada (raíz) |
| `function_decl` | Declaraciones de funciones |
| `struct_decl` | Declaraciones de estructuras |
| `statement` | Todas las sentencias |
| `expression` | Jerarquía completa de expresiones |
| `type` | Sistema de tipos con punteros |
| `if_stmt` | Sentencia condicional |
| `while_stmt` | Bucle while |
| `for_stmt` | Bucle for |

## 💡 Tips

- Empieza con `gramatica_simple.ebnf` para familiarizarte
- Luego prueba la gramática completa
- Navega entre reglas haciendo clic en los nombres
- Los diagramas son interactivos

## 🐛 Solución de Problemas

**Si la página no carga:**

- Prueba con `gramatica_simple.ebnf` primero
- Copia solo una sección del archivo completo
- Verifica que el navegador tenga JavaScript habilitado

**Si hay errores de sintaxis:**

- El archivo ya está validado, pero si modificas:
- Verifica que uses `::=` para definiciones
- Usa comillas simples `' '` para terminales
- Respeta la sintaxis: `?` (opcional), `*` (0+), `+` (1+)

## 📚 Referencias

- Sintaxis W3C EBNF: <https://www.w3.org/TR/REC-xml/#sec-notation>
- Railroad Diagram Generator: <https://www.bottlecaps.de/rr/ui>
- ISO EBNF: ISO/IEC 14977

## ✨ Resultado Final

Tendrás una representación visual completa de la gramática que:

- Facilita la comprensión de la sintaxis
- Ayuda a identificar ambigüedades
- Sirve como documentación visual
- Es útil para enseñar el lenguaje
