# Cómo usar la gramática EBNF con Railroad Diagram Generator

## Plataforma: https://www.bottlecaps.de/rr/ui

### Pasos para generar diagramas:

1. **Abrir la herramienta**
   - Ir a https://www.bottlecaps.de/rr/ui
   
2. **Cargar la gramática**
   - Copiar el contenido del archivo `gramatica.ebnf`
   - Pegar en el área de texto de la herramienta
   - Click en "Display Diagram"

3. **Navegar por los diagramas**
   - La herramienta generará diagramas de sintaxis ferroviaria (railroad diagrams)
   - Cada regla de la gramática tendrá su propio diagrama
   - Los diagramas muestran visualmente los caminos posibles en la sintaxis

4. **Explorar reglas específicas**
   - Puedes hacer clic en las reglas para navegar entre ellas
   - Las reglas están enlazadas, permitiendo seguir la jerarquía

### Reglas principales para explorar:

- **`program`** - Punto de entrada de la gramática
- **`function_decl`** - Estructura de funciones
- **`expression`** - Jerarquía completa de expresiones
- **`statement`** - Todas las sentencias del lenguaje
- **`type`** - Sistema de tipos con punteros

### Ejemplos de uso:

#### Ver declaración de función:
Buscar la regla `function_decl` o `normal_function_decl` para ver:
```
funcion → type → ID → ( → param_list? → ) → block
```

#### Ver expresiones:
Buscar `expression` para ver la jerarquía completa desde asignación hasta literales.

#### Ver control de flujo:
Buscar `if_stmt`, `while_stmt`, `for_stmt` para ver estructuras de control.

### Formato de la gramática:

El archivo ahora usa la sintaxis W3C EBNF que es compatible con Railroad Diagram Generator:

- **`::=`** - Definición de regla
- **`|`** - Alternativa (o)
- **`?`** - Opcional (0 o 1 vez)
- **`*`** - Repetición (0 o más veces)
- **`+`** - Repetición (1 o más veces)
- **`( )`** - Agrupación
- **`' '`** - Literales (terminales)
- **`/* */`** - Comentarios

### Notas importantes:

1. La herramienta puede tener problemas con gramáticas muy grandes. Si no carga todo:
   - Prueba copiando solo secciones específicas
   - Comienza con reglas básicas como `program` y `statement`

2. Los comentarios están incluidos y no afectarán la generación de diagramas

3. Las reglas léxicas (ID, ENTERO, FLOT, etc.) están al final del archivo

### Alternativas a Railroad Diagram Generator:

Si la herramienta de bottlecaps.de no funciona bien, también puedes usar:

1. **RR - Railroad Diagram Generator (línea de comandos)**
   ```bash
   npm install -g railroad-diagrams
   ```

2. **ANTLR Lab** (para gramáticas ANTLR, requiere conversión)
   - https://lab.antlr.org/

3. **Syntax Diagram Generator**
   - Diferentes implementaciones disponibles en GitHub

### Exportar diagramas:

Una vez generados los diagramas en bottlecaps.de:

1. Click derecho en el diagrama
2. "Save Image As..." o "Copy Image"
3. Los diagramas se pueden exportar como SVG o PNG

### Verificación de la gramática:

La herramienta también sirve para validar que:
- No hay reglas sin definir
- No hay recursión infinita a la izquierda
- La sintaxis EBNF es correcta

Si la herramienta carga sin errores, la gramática es sintácticamente válida.
