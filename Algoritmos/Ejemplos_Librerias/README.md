# Ejemplos de Uso de Bibliotecas

Esta carpeta contiene ejemplos que demuestran el uso de las bibliotecas disponibles en `/lib`.

## Bibliotecas Disponibles

### 1. `lib/math.asm` - Operaciones Matemáticas
- **Constantes**: `PI`, `E`, `ZERO`, `ONE`
- **Macros**:
  - `SQUARE reg` - Calcula el cuadrado de un número
  - `DOUBLE reg` - Duplica un número
  - `ABS reg, temp_reg` - Valor absoluto
  - `SWAP reg1, reg2, temp` - Intercambia valores entre registros

### 2. `lib/io.asm` - Entrada/Salida
- **Constantes**: `IO_BASE`, `IO_OUTPUT_1`, `IO_OUTPUT_2`, `IO_INPUT_1`
- **Macros**:
  - `PRINT_REG reg, addr` - Imprime un registro en una dirección
  - `CLEAR_OUTPUT addr` - Limpia la salida

### 3. `lib/stack.asm` - Operaciones de Pila
- **Constantes**: `STACK_SIZE`, `STACK_BASE`
- **Macros**:
  - `PUSH_BYTE reg`, `POP_BYTE reg`
  - `PUSH_WORD reg`, `POP_WORD reg`
  - `PUSH_DWORD reg`, `POP_DWORD reg`
  - `PUSH_QWORD reg`, `POP_QWORD reg`
- **Nota**: El registro R15 actúa como puntero de pila (SP)

### 4. `lib/utils.asm` - Utilidades Generales
- **Constantes**: `TRUE`, `FALSE`, `NULL`, `BYTE_SIZE`, `WORD_SIZE`, `DWORD_SIZE`, `QWORD_SIZE`
- **Macros**:
  - `ZERO_REG reg` - Limpia un registro
  - `SET_ONE reg` - Establece un registro a 1
  - `INC_N reg, n` - Incrementa N veces
  - `DEC_N reg, n` - Decrementa N veces
  - `COPY src, dst` - Copia un registro
  - `WAIT cycles` - NOP extendido

### 5. `lib/lib_principal.asm` - Biblioteca Principal
Incluye automáticamente todas las demás bibliotecas y añade macros compuestos:
- **Macros**:
  - `PRINT_SQUARE reg, output_addr` - Calcula cuadrado, imprime y restaura
  - `PRINT_DOUBLE reg, output_addr` - Duplica, imprime y restaura

## Ejemplos Incluidos

### `ejemplo_simple.asm` ⭐ (Recomendado para empezar)
Ejemplo básico sin bibliotecas:
- Operaciones básicas de carga y almacenamiento
- Suma y multiplicación simples
- Uso de instrucciones IO (SVIO, SHOWIO)
- Ideal para verificar que el sistema funciona

### `ejemplo_constantes.asm`
Prueba de constantes definidas en bibliotecas:
- Uso de constantes matemáticas (PI, E)
- Uso de constantes IO (IO_OUTPUT_1, IO_OUTPUT_2)
- Verificación de que los #define funcionan correctamente

### `ejemplo_math.asm`
Demuestra operaciones matemáticas usando constantes de `lib/math.asm`:
- Cálculo de cuadrados (sin macros, código directo)
- Duplicación de valores
- Intercambio de registros usando MOV8
- Uso de constantes: PI, E, ZERO, ONE

### `ejemplo_io.asm`
Demuestra operaciones de entrada/salida usando constantes de `lib/io.asm`:
- Impresión de valores usando SVIO y SHOWIO
- Uso de diferentes direcciones IO
- Operaciones básicas de incremento/decremento
- Uso de constantes booleanas (TRUE, FALSE)

### `ejemplo_utils.asm`
Demuestra utilidades usando constantes de `lib/utils.asm`:
- Uso de constantes booleanas (TRUE, FALSE, NULL)
- Constantes de tamaños (BYTE_SIZE, WORD_SIZE, DWORD_SIZE, QWORD_SIZE)
- Limpieza e inicialización de registros
- Operaciones aritméticas básicas

### `ejemplo_stack.asm`
Demuestra operaciones con pila usando `lib/stack.asm`:
- PUSH8 y POP8 (8 bytes)
- PUSH4 y POP4 (4 bytes)
- Guardar y restaurar múltiples registros
- Configuración del puntero de pila (R15)
- Demostración del comportamiento LIFO (Last In, First Out)

### `ejemplo_lib_principal.asm`
Demuestra el uso combinado de todas las bibliotecas:
- Incluye math, io, utils y stack juntas
- Operaciones matemáticas con constantes
- Uso de pila para preservar valores
- Ejemplo de cálculo complejo: 3² + 4² = 25 (Teorema de Pitágoras)
- Copia de valores entre registros con MOV8

## Cómo Usar

1. **Para incluir una biblioteca específica:**
   ```assembly
   #include "lib/math.asm"
   ```

2. **Para incluir múltiples bibliotecas:**
   ```assembly
   #include "lib/math.asm"
   #include "lib/io.asm"
   #include "lib/utils.asm"
   #include "lib/stack.asm"
   ```

3. **Compilar y ejecutar:**
   ```bash
   python main.py
   ```
   Luego selecciona el archivo `.asm` que deseas ejecutar desde la interfaz.

## Orden de Aprendizaje Recomendado

1. **`ejemplo_simple.asm`** - Comienza aquí para entender las instrucciones básicas
2. **`ejemplo_constantes.asm`** - Aprende cómo funcionan las constantes #define
3. **`ejemplo_math.asm`** - Operaciones matemáticas y uso de constantes
4. **`ejemplo_io.asm`** - Entrada/salida y direcciones IO
5. **`ejemplo_utils.asm`** - Constantes útiles y operaciones básicas
6. **`ejemplo_stack.asm`** - Operaciones de pila (más avanzado)
7. **`ejemplo_lib_principal.asm`** - Uso combinado de todo (más complejo)

## Notas Importantes

### Sistema de Preprocesamiento
- Las bibliotecas usan directivas `#include` y `#define`
- Las constantes `#define` se expanden automáticamente durante la compilación
- Los macros `.macro/.endmacro` también son soportados pero estos ejemplos usan código directo

### Arquitectura del Procesador
- **Registros disponibles**: R0 a R15 (16 registros de propósito general)
- **Registro especial**: R15 actúa como puntero de pila (Stack Pointer)
- **No hay secciones**: No uses `.data` o `.text`, todo el código son instrucciones directamente

### Instrucciones Clave
- **`LOADV Rd, valor`**: Carga un valor inmediato en un registro
- **`MOV8 Rd, Rs`**: Copia el contenido de un registro a otro (8 bytes)
- **`STOREV Rd, addr`**: Guarda el registro en una dirección de memoria
- **`LOAD Rd, addr`**: Carga desde memoria a un registro
- **`SVIO Rd, addr`**: Guarda registro en IO[addr]
- **`SHOWIO addr`**: Muestra el valor en IO[addr] en la GUI
- **`PUSH8 Rd` / `POP8 Rd`**: Operaciones de pila de 8 bytes

### Pila (Stack)
- **Siempre** inicializa R15 antes de usar operaciones de pila:
  ```assembly
  LOADV R15, STACK_BASE  ; donde STACK_BASE está definido en lib/stack.asm
  ```
- La pila funciona como LIFO (Last In, First Out)
- Usa `PUSH8`/`POP8` para valores de 64 bits, `PUSH4`/`POP4` para 32 bits, etc.

### Errores Comunes
- ❌ `LOADV R1, R2` - **INCORRECTO**: LOADV solo acepta valores inmediatos
- ✅ `MOV8 R1, R2` - **CORRECTO**: Usa MOV8 para copiar entre registros
- ❌ Usar `.data` o `.qword` - **INCORRECTO**: No existen en esta arquitectura
- ✅ Usar `STOREV` y direcciones numéricas directas - **CORRECTO**
