# Analizador Semántico - Guía de Integración

Esta guía explica el flujo de trabajo entre el analizador sintáctico y semántico, y cómo integrarlos en la interfaz gráfica y el compilador completo.

## Flujo de Trabajo: Sintáctico → Semántico

### Diagrama del Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    CÓDIGO FUENTE                            │
│              (archivo .txt o string)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: ANÁLISIS SINTÁCTICO                                │
│  ────────────────────────────────────────                  │
│  compiler.syntax_analizer.parse(code)                       │
│                                                              │
│  1. Lexer (lex_analizer.py)                                 │
│     → Tokeniza el código fuente                             │
│     → Genera lista de tokens                                │
│                                                              │
│  2. Parser (syntax_analizer.py)                             │
│     → Aplica reglas gramaticales (PLY Yacc)                │
│     → Construye Árbol de Sintaxis Abstracta (AST)          │
│     → Retorna: Program (nodo raíz) o None                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   AST válido?  │
              └────┬───────┬───┘
                   │       │
            SÍ     │       │    NO
                   │       │
                   ▼       ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  FASE 2:         │  │  ERROR:          │
    │  SEMÁNTICO        │  │  Detener proceso│
    │                   │  │  Retornar errores│
    │  analyze(ast)     │  └──────────────────┘
    │                   │
    │  1. Primera pasada│
    │     → Declara     │
    │       structs     │
    │       funciones   │
    │                   │
    │  2. Segunda pasada│
    │     → Valida tipos│
    │     → Verifica    │
    │       scopes      │
    │     → Chequea     │
    │       control     │
    │       de flujo    │
    │                   │
    │  Retorna:         │
    │  (success, errors)│
    └──────┬────────────┘
           │
           ▼
    ┌──────────────────┐
    │  AST VALIDADO    │
    │  (sin errores)   │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  GENERADOR DE    │
    │  CÓDIGO /        │
    │  ENSAMBLADOR     │
    └──────────────────┘
```

## Funciones y Métodos Principales

### 1. Análisis Sintáctico

#### `compiler.syntax_analizer.parse(code, debug=False)`

**Descripción:** Parsea código fuente y genera el AST.

**Parámetros:**
- `code` (str): Código fuente a parsear
- `debug` (bool): Activar modo debug de PLY (opcional, default=False)

**Retorna:**
- `Program`: Nodo raíz del AST si el parseo es exitoso
- `None`: Si hay errores de sintaxis

**Ejemplo:**
```python
from compiler.syntax_analizer import parse

code = """
funcion entero4 sumar(entero4 a, entero4 b) {
    retornar a + b;
}
"""

ast = parse(code)
if ast:
    print(f"Parseado exitoso: {len(ast.declarations)} declaraciones")
else:
    print("Error de sintaxis")
```

### 2. Análisis Semántico

#### `compiler.semantic_analyzer.analyze(ast)`

**Descripción:** Analiza semánticamente un AST validando tipos, scopes y reglas semánticas.

**Parámetros:**
- `ast` (Program): Nodo raíz del AST (debe ser válido sintácticamente)

**Retorna:**
- `tuple (bool, list)`: 
  - `bool`: `True` si no hay errores, `False` si hay errores
  - `list`: Lista de mensajes de error (strings)

**Ejemplo:**
```python
from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import analyze

ast = parse(code)
if ast:
    success, errors = analyze(ast)
    if success:
        print("Análisis semántico exitoso")
    else:
        print("Errores semánticos:")
        for error in errors:
            print(f"  - {error}")
```

### 3. Compilación Completa (Recomendado)

#### `compiler.compiler.compile_code(code, debug=False)`

**Descripción:** Función principal que integra análisis sintáctico y semántico.

**Parámetros:**
- `code` (str): Código fuente a compilar
- `debug` (bool): Activar modo debug (opcional, default=False)

**Retorna:**
- `tuple (ast, success, errors)`:
  - `ast` (Program|None): AST parseado o None si hay errores sintácticos
  - `success` (bool): `True` si no hay errores, `False` si hay errores
  - `errors` (list): Lista de mensajes de error (sintácticos y semánticos)

**Ejemplo:**
```python
from compiler.compiler import compile_code

code = """
funcion entero4 sumar(entero4 a, entero4 b) {
    retornar a + b;
}

funcion vacio principal() {
    entero4 resultado = sumar(10, 20);
}
"""

ast, success, errors = compile_code(code)

if success:
    print("Compilación exitosa")
    # El AST está validado y listo para usar
    # Puedes pasarlo al generador de código o ensamblador
else:
    print("Errores encontrados:")
    for error in errors:
        print(f"  - {error}")
```

#### `compiler.compiler.compile_file(filename, debug=False)`

**Descripción:** Compila un archivo fuente.

**Parámetros:**
- `filename` (str): Ruta al archivo fuente
- `debug` (bool): Activar modo debug (opcional, default=False)

**Retorna:**
- `tuple (ast, success, errors)`: Mismo formato que `compile_code()`

**Ejemplo:**
```python
from compiler.compiler import compile_file

ast, success, errors = compile_file("programa.txt")

if success:
    print("Archivo compilado exitosamente")
else:
    print("Errores:")
    for error in errors:
        print(f"  - {error}")
```

## Integración con la Interfaz Gráfica

### Ejemplo de Integración en GUI (Tkinter)

```python
import tkinter as tk
from tkinter import messagebox, scrolledtext
from compiler.compiler import compile_code

class CompiladorGUI:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
    
    def setup_ui(self):
        # Área de código fuente
        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            width=80, 
            height=25,
            font=("Consolas", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Área de errores
        self.error_area = scrolledtext.ScrolledText(
            self.root,
            width=80,
            height=10,
            font=("Consolas", 9),
            fg="red"
        )
        self.error_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botón de compilación
        btn_compile = tk.Button(
            self.root,
            text="Compilar",
            command=self.compilar,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        btn_compile.pack(pady=10)
    
    def compilar(self):
        """Compila el código y muestra resultados"""
        # Obtener código del área de texto
        code = self.text_area.get("1.0", tk.END)
        
        # Limpiar área de errores
        self.error_area.delete("1.0", tk.END)
        
        # Compilar
        from compiler.compiler import compile_code
        ast, success, errors = compile_code(code)
        
        if success:
            messagebox.showinfo(
                "Compilación Exitosa",
                f"El código se compiló correctamente.\n"
                f"Declaraciones encontradas: {len(ast.declarations)}"
            )
            # Aquí puedes pasar el AST al generador de código
            # self.generar_codigo(ast)
        else:
            # Mostrar errores
            error_text = "\n".join([f"• {error}" for error in errors])
            self.error_area.insert("1.0", error_text)
            messagebox.showerror(
                "Errores de Compilación",
                f"Se encontraron {len(errors)} error(es).\n"
                f"Revisa el área de errores."
            )

# Uso
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Compilador - Atlas")
    app = CompiladorGUI(root)
    root.mainloop()
```

### Manejo de Errores en GUI

```python
def compilar_con_detalles(self):
    """Compilación con información detallada de errores"""
    code = self.text_area.get("1.0", tk.END)
    
    # Compilar
    ast, success, errors = compile_code(code)
    
    if not ast:
        # Error sintáctico
        self.mostrar_error("Error de Sintaxis", 
                          "No se pudo parsear el código.\n"
                          "Verifica la sintaxis.")
        return
    
    if not success:
        # Errores semánticos
        errores_sintacticos = [e for e in errors if "sintaxis" in e.lower()]
        errores_semanticos = [e for e in errors if "semántico" in e.lower()]
        
        mensaje = f"Errores encontrados:\n\n"
        if errores_sintacticos:
            mensaje += f"Sintácticos: {len(errores_sintacticos)}\n"
        if errores_semanticos:
            mensaje += f"Semánticos: {len(errores_semanticos)}\n"
        
        self.mostrar_errores_detallados(errors)
        return
    
    # Compilación exitosa
    self.procesar_ast(ast)
```

## Integración con el Compilador Completo

### Flujo Completo: Alto Nivel → Ensamblador

```python
from compiler.compiler import compile_code
from compiler.code_generator import CodeGenerator  # Asumiendo que existe
from compiler.ensamblador import Ensamblador

def compilar_completo(code_fuente):
    """
    Compila código de alto nivel hasta código ensamblador
    """
    # Paso 1: Compilación (sintáctico + semántico)
    ast, success, errors = compile_code(code_fuente)
    
    if not success:
        return None, errors
    
    # Paso 2: Generación de código intermedio
    # (Asumiendo que existe un generador de código)
    generator = CodeGenerator()
    codigo_intermedio = generator.generate(ast)
    
    # Paso 3: Ensamblador (si es necesario)
    assembler = Ensamblador()
    codigo_ensamblador = assembler.assemble(codigo_intermedio)
    
    return codigo_ensamblador, []
```

### Ejemplo con Manejo de Errores por Fase

```python
def compilar_con_fases(code):
    """
    Compila mostrando el progreso de cada fase
    """
    resultados = {
        'sintactico': None,
        'semantico': None,
        'ast': None,
        'errores': []
    }
    
    # Fase 1: Sintáctico
    from compiler.syntax_analizer import parse
    ast = parse(code)
    
    if ast is None:
        resultados['errores'].append("Error de sintaxis")
        return resultados
    
    resultados['sintactico'] = True
    resultados['ast'] = ast
    
    # Fase 2: Semántico
    from compiler.semantic_analyzer import analyze
    success, errors = analyze(ast)
    
    resultados['semantico'] = success
    resultados['errores'].extend(errors)
    
    return resultados
```

## Uso en Módulos Externos

### Importación Correcta

```python
# Opción 1: Usar la función integrada (RECOMENDADO)
from compiler.compiler import compile_code, compile_file

# Opción 2: Usar funciones individuales
from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import analyze

# Opción 3: Acceso a clases internas (avanzado)
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.symbol_table import SymbolTable
```

### Patrón de Uso Recomendado

```python
def procesar_codigo(code):
    """
    Patrón recomendado para procesar código
    """
    # 1. Compilar (incluye sintáctico + semántico)
    ast, success, errors = compile_code(code)
    
    # 2. Verificar éxito
    if not success:
        return {
            'exito': False,
            'errores': errors,
            'ast': None
        }
    
    # 3. Procesar AST validado
    return {
        'exito': True,
        'errores': [],
        'ast': ast,
        'declaraciones': ast.declarations,
        'estadisticas': {
            'funciones': sum(1 for d in ast.declarations 
                           if isinstance(d, FunctionDecl)),
            'estructuras': sum(1 for d in ast.declarations 
                             if isinstance(d, StructDecl)),
        }
    }
```

## Estructura de Datos de Retorno

### AST (Árbol de Sintaxis Abstracta)

El AST es un objeto `Program` con la siguiente estructura:

```python
class Program:
    declarations: List[Declaration]  # Lista de declaraciones
    
# Tipos de Declaration:
# - FunctionDecl: Declaración de función
# - StructDecl: Declaración de estructura
# - VarDecl: Declaración de variable global
```

### Ejemplo de Navegación del AST

```python
ast, success, errors = compile_code(code)

if success:
    # Iterar sobre declaraciones
    for decl in ast.declarations:
        if isinstance(decl, FunctionDecl):
            print(f"Función: {decl.name}")
            print(f"  Retorna: {decl.return_type.name}")
            print(f"  Parámetros: {len(decl.params)}")
            
            # Acceder al cuerpo
            if decl.body:
                for stmt in decl.body.statements:
                    # Procesar sentencias
                    pass
```

## Manejo de Errores

### Tipos de Errores

1. **Errores Sintácticos**: Detectados por el parser
   - Formato: `"Error de sintaxis en línea X: ..."`
   - El AST será `None`

2. **Errores Semánticos**: Detectados por el analizador semántico
   - Formato: `"Error semántico en línea X: ..."`
   - El AST existe pero tiene errores de validación

### Ejemplo de Manejo de Errores

```python
ast, success, errors = compile_code(code)

if not ast:
    # Solo errores sintácticos
    print("Errores de sintaxis:")
    for error in errors:
        print(f"  {error}")
elif not success:
    # Errores semánticos (y posiblemente algunos sintácticos)
    errores_semanticos = [e for e in errors if "semántico" in e]
    print(f"Errores semánticos: {len(errores_semanticos)}")
    for error in errores_semanticos:
        print(f"  {error}")
else:
    # Todo correcto
    print("Compilación exitosa")
```

## Pruebas y Validación

### Ejecutar Tests

```bash
# Todos los tests semánticos
python -m unittest test_semantic_analyzer -v

# Test específico
python -m unittest test_semantic_analyzer.TestSemanticAnalyzer.test_undeclared_variable -v
```

### Test de Integración

```python
import unittest
from compiler.compiler import compile_code

class TestIntegracion(unittest.TestCase):
    def test_compilacion_completa(self):
        code = """
        funcion entero4 sumar(entero4 a, entero4 b) {
            retornar a + b;
        }
        """
        ast, success, errors = compile_code(code)
        self.assertTrue(success)
        self.assertIsNotNone(ast)
        self.assertEqual(len(errors), 0)
```

## Notas Importantes

1. **Siempre verificar el AST**: Antes de usar el AST, verifica que no sea `None`
2. **Errores acumulativos**: Los errores se acumulan, no se detiene en el primer error
3. **AST válido con errores**: El AST puede existir incluso con errores semánticos
4. **Dos pasadas**: El analizador semántico hace dos pasadas sobre el AST
5. **Scopes anidados**: Los scopes se manejan automáticamente con pila

## Referencias

- `compiler/syntax_analizer.py`: Parser y generación de AST
- `compiler/semantic_analyzer.py`: Validación semántica
- `compiler/symbol_table.py`: Gestión de tablas de símbolos
- `compiler/compiler.py`: Función principal de compilación
- `compiler/ast_nodes.py`: Definición de nodos del AST
