"""
Test de carga de código binario
Verifica que la UI pueda cargar código hexadecimal directamente
"""

# Simular las funciones de detección de binario
def es_codigo_binario(texto):
    """Detecta si el texto contiene código binario en formato hexadecimal"""
    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
    
    for linea in lineas:
        # Ignorar comentarios
        if linea.startswith(';') or linea.startswith('#'):
            continue
        
        # Extraer la parte hexadecimal
        if ':' in linea:
            # Formato "0000: 006110000000000a"
            partes = linea.split(':')
            if len(partes) >= 2:
                linea_limpia = partes[1].strip().split()[0]
            else:
                return False
        else:
            # Remover prefijos comunes
            linea_limpia = linea.replace('0x', '').strip().split()[0]
        
        # Verificar si es hexadecimal válido de 16 caracteres
        if len(linea_limpia) == 16 and all(c in '0123456789ABCDEFabcdef' for c in linea_limpia):
            continue
        elif linea.strip():
            return False
    
    return len(lineas) > 0

def parsear_codigo_binario(texto):
    """Convierte código binario hexadecimal a lista de instrucciones"""
    instrucciones = []
    lineas = texto.split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        
        # Ignorar líneas vacías y comentarios
        if not linea or linea.startswith(';') or linea.startswith('#'):
            continue
        
        # Extraer el código hexadecimal
        if ':' in linea:
            partes = linea.split(':')
            hex_code = partes[1].strip().split()[0]
        else:
            hex_code = linea.replace('0x', '').strip().split()[0]
        
        # Convertir a entero
        try:
            instruccion = int(hex_code, 16)
            instrucciones.append(instruccion)
        except ValueError:
            raise ValueError(f"Código hexadecimal inválido: {hex_code}")
    
    return instrucciones


# Tests
print("=" * 80)
print("TEST 1: Código binario simple")
print("=" * 80)

codigo_simple = """
006110000000000a
0061200000000005
0010000000000012
00a0100000000100
00a2000000000100
0000000000000000
"""

es_bin = es_codigo_binario(codigo_simple)
print(f"¿Es binario? {es_bin}")
if es_bin:
    instrs = parsear_codigo_binario(codigo_simple)
    print(f"Instrucciones parseadas: {len(instrs)}")
    for i, instr in enumerate(instrs):
        print(f"  {i}: 0x{instr:016x}")

print("\n" + "=" * 80)
print("TEST 2: Código con direcciones")
print("=" * 80)

codigo_con_dir = """
0000: 006110000000000a
0008: 0061200000000005
0010: 0010000000000012
0018: 00a0100000000100
0020: 00a2000000000100
0028: 0000000000000000
"""

es_bin = es_codigo_binario(codigo_con_dir)
print(f"¿Es binario? {es_bin}")
if es_bin:
    instrs = parsear_codigo_binario(codigo_con_dir)
    print(f"Instrucciones parseadas: {len(instrs)}")
    for i, instr in enumerate(instrs):
        print(f"  {i}: 0x{instr:016x}")

print("\n" + "=" * 80)
print("TEST 3: Código assembly (NO binario)")
print("=" * 80)

codigo_asm = """
LOADV R1, 10
LOADV R2, 5
ADD R1, R2
PARAR
"""

es_bin = es_codigo_binario(codigo_asm)
print(f"¿Es binario? {es_bin}")
print("Correcto: debe detectarse como assembly")

print("\n" + "=" * 80)
print("TEST 4: Código con comentarios")
print("=" * 80)

codigo_comentarios = """
; Cargar valores
006110000000000a
# Sumar
0010000000000012
; Terminar
0000000000000000
"""

es_bin = es_codigo_binario(codigo_comentarios)
print(f"¿Es binario? {es_bin}")
if es_bin:
    instrs = parsear_codigo_binario(codigo_comentarios)
    print(f"Instrucciones parseadas: {len(instrs)}")
    for i, instr in enumerate(instrs):
        print(f"  {i}: 0x{instr:016x}")

print("\n" + "=" * 80)
print("TEST 5: Código con prefijo 0x")
print("=" * 80)

codigo_0x = """
0x006110000000000a
0x0061200000000005
0x0010000000000012
"""

es_bin = es_codigo_binario(codigo_0x)
print(f"¿Es binario? {es_bin}")
if es_bin:
    instrs = parsear_codigo_binario(codigo_0x)
    print(f"Instrucciones parseadas: {len(instrs)}")
    for i, instr in enumerate(instrs):
        print(f"  {i}: 0x{instr:016x}")

print("\n" + "=" * 80)
print("TODOS LOS TESTS COMPLETADOS")
print("=" * 80)
