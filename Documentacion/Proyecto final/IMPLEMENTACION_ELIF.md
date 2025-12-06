# Implementación del Condicional `si-no-si` (elif)

## Resumen

Se ha implementado soporte completo para el condicional `si-no-si`, equivalente al `elif` de Python, permitiendo cadenas de condiciones sin necesidad de anidar múltiples bloques `si-no`.

## Sintaxis

```
si (<condición_1>) {
    <bloque_1>
} si_no_si (<condición_2>) {
    <bloque_2>
} si_no_si (<condición_3>) {
    <bloque_3>
} si_no {
    <bloque_else>
}
```

## Características

### 1. **Soporte Explícito en el AST**
- Nueva clase `ElifClause` para representar cláusulas elif
- `IfStmt` modificado para almacenar lista de `elif_clauses`
- Mejor representación semántica que anidamiento implícito

### 2. **Límite de Seguridad**
- **Máximo: 10 cláusulas `si_no_si` consecutivas**
- Previene desbordamiento de stack y exceso de saltos en código ensamblador
- El límite se valida durante el análisis semántico

### 3. **Validación Semántica**
- Todas las condiciones (if, elif) deben ser de tipo booleano
- Se valida cada cláusula elif independientemente
- Mensajes de error específicos para cada tipo de cláusula

### 4. **Generación de Código Optimizada**
- Genera etiquetas secuenciales (ELIF1, ELIF2, etc.)
- Estructura de saltos eficiente
- Evita anidamiento innecesario de etiquetas

## Archivos Modificados

### 1. `src/compiler/ast_nodes.py`
```python
class ElifClause(ASTNode):
    """Cláusula si-no-si (elif)"""
    def __init__(self, condition, block, lineno=None, lexpos=None):
        self.condition = condition
        self.block = block

class IfStmt(ASTNode):
    """Sentencia if / if-elif-else"""
    def __init__(self, condition, then_block, elif_clauses=None, else_block=None, ...):
        self.condition = condition
        self.then_block = then_block
        self.elif_clauses = elif_clauses or []  # Lista de ElifClause
        self.else_block = else_block
```

### 2. `src/compiler/Lex_analizer.py`
```python
reserved = {
    'si': 'SI',
    'si_no': 'SI_NO',
    'si_no_si': 'SI_NO_SI',  # ← NUEVO
    ...
}
```

### 3. `src/compiler/syntax_analizer.py`
Nuevas reglas gramaticales:
- `if_stmt` con 4 variantes
- `elif_list` para cadenas de elif
- `elif_clause` para elementos individuales

### 4. `src/compiler/semantic_analyzer.py`
- Validación de límite de 10 elif
- Validación de tipo booleano para todas las condiciones
- Análisis recursivo de bloques elif

### 5. `src/compiler/code_generator.py`
- Generación de etiquetas ELIF secuenciales
- Lógica de saltos optimizada
- Manejo correcto de última cláusula

## Ejemplos de Uso

### Ejemplo 1: Clasificación de Calificaciones
```c
funcion vacio clasificar_nota(entero4 nota) {
    si (nota >= 90) {
        imprimir("A - Excelente");
    } si_no_si (nota >= 80) {
        imprimir("B - Muy bueno");
    } si_no_si (nota >= 70) {
        imprimir("C - Bueno");
    } si_no_si (nota >= 60) {
        imprimir("D - Suficiente");
    } si_no {
        imprimir("F - Reprobado");
    }
}
```

### Ejemplo 2: Calculadora
```c
funcion entero4 calcular(entero4 a, entero4 b, caracter op) {
    entero4 resultado = 0;
    
    si (op == '+') {
        resultado = a + b;
    } si_no_si (op == '-') {
        resultado = a - b;
    } si_no_si (op == '*') {
        resultado = a * b;
    } si_no_si (op == '/') {
        resultado = a / b;
    } si_no {
        imprimir("Operación inválida");
    }
    
    retornar resultado;
}
```

### Ejemplo 3: Año Bisiesto
```c
funcion booleano es_bisiesto(entero4 año) {
    booleano resultado = 0;
    
    si (año % 400 == 0) {
        resultado = 1;
    } si_no_si (año % 100 == 0) {
        resultado = 0;
    } si_no_si (año % 4 == 0) {
        resultado = 1;
    }
    
    retornar resultado;
}
```

## Código Ensamblador Generado

Para el código:
```c
si (x > 10) {
    y = 1;
} si_no_si (x > 5) {
    y = 2;
} si_no {
    y = 3;
}
```

Se genera:
```assembly
  ; Evaluar condición principal (x > 10)
  CMPV R00, 10
  JEQ ELIF001        ; Si falso, ir a elif
  ; Bloque then
  SETV R01, 1
  JMP ENDIF001       ; Saltar al final
ELIF001:
  ; Evaluar condición elif (x > 5)
  CMPV R00, 5
  JEQ ELSE001        ; Si falso, ir a else
  ; Bloque elif
  SETV R01, 2
  JMP ENDIF001       ; Saltar al final
ELSE001:
  ; Bloque else
  SETV R01, 3
ENDIF001:
  ; Continuar...
```

## Testing

### Script de Prueba Automático
Se incluye `test_elif.py` que valida:
- ✓ Elif simple con else
- ✓ Múltiples elif consecutivos
- ✓ Elif sin else final
- ✓ Compatibilidad con if-else tradicional

### Ejemplos de Prueba
Ubicados en `Algoritmos/Ejemplos_alto_nivel/`:
1. `ejemplo_elif_simple.txt` - Clasificación de calificaciones
2. `ejemplo_elif_calculadora.txt` - Calculadora con operadores
3. `ejemplo_elif_complejo.txt` - Temperatura, año bisiesto, días en mes

## Compatibilidad

### ✓ Retrocompatibilidad
La sintaxis anterior `si-no` sigue funcionando sin cambios:
```c
si (condicion) {
    // ...
} si_no {
    // ...
}
```

### ✓ Anidamiento
Se pueden anidar `si-no-si` dentro de bloques:
```c
si (a > 10) {
    si (b > 5) {
        // ...
    } si_no_si (b > 2) {
        // ...
    }
} si_no_si (a > 5) {
    // ...
}
```

## Gramática EBNF Actualizada

```ebnf
if_stmt ::= 'si' '(' expression ')' statement 
            ('si_no_si' '(' expression ')' statement)* 
            ('si_no' statement)?
```

**Restricción:** Máximo 10 cláusulas `si_no_si` consecutivas.

## Documentación Actualizada

Los siguientes archivos de documentación han sido actualizados:
- `Documentacion/GUIA_VISUALIZACION.md`
- `Documentacion/Taller2/gramatica/index.md`

## Mensajes de Error

### Error: Demasiados elif
```
Error semántico: Máximo 10 cláusulas 'si_no_si' permitidas, se encontraron 11
```

### Error: Condición no booleana
```
Error semántico: Condición de 'si_no_si' debe ser de tipo booleano
```

## Notas de Implementación

### Decisión de Diseño: Soporte Explícito vs. Sintáctico
Se eligió **soporte explícito** (modificar AST) sobre transformación sintáctica porque:
- ✓ AST más limpio y semánticamente correcto
- ✓ Mejor mensajes de error
- ✓ Más fácil para optimizaciones futuras
- ✓ Generación de código más eficiente

### Límite de 10 elif
El límite previene:
- Desbordamiento de stack en la máquina virtual
- Exceso de etiquetas de salto en ensamblador
- Código difícil de mantener
- En la práctica, >10 elif indica necesidad de refactorización (usar switch/match)

## Autor
Implementado por: Grupo D - Hexacore Atlas
Fecha: Diciembre 2025
