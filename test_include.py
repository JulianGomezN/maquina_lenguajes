"""
Test de la funcionalidad #include del preprocesador
Demuestra el uso de bibliotecas con #include
"""

import os
from compiler.preprocessor import Preprocessor
from compiler.ensamblador import Ensamblador

def test_include_basico():
    """Prueba #include básico"""
    print("=" * 80)
    print("TEST 1: #include básico (lib/io.asm)")
    print("=" * 80)
    
    code = """
#include "lib/io.asm"

MAIN:
    LOADV R1, 42
    PRINT_REG R1, IO_OUTPUT_1
    PARAR
"""
    
    print("\nCódigo original:")
    print(code)
    
    preprocessor = Preprocessor()
    resultado = preprocessor.preprocess(code)
    
    print("\nCódigo después del preprocesamiento:")
    print(resultado)
    print("\n" + "=" * 80)


def test_include_multiple():
    """Prueba múltiples #include"""
    print("\n\n" + "=" * 80)
    print("TEST 2: Múltiples #include")
    print("=" * 80)
    
    code = """
#include "lib/math.asm"
#include "lib/io.asm"
#include "lib/utils.asm"

MAIN:
    LOADV R1, 10
    DOUBLE R1
    PRINT_REG R1, IO_OUTPUT_1
    PARAR
"""
    
    print("\nCódigo original:")
    print(code)
    
    preprocessor = Preprocessor()
    resultado = preprocessor.preprocess(code)
    
    print("\nCódigo después del preprocesamiento:")
    print(resultado)
    print("\n" + "=" * 80)


def test_include_anidado():
    """Prueba #include anidado (biblioteca que incluye otras)"""
    print("\n\n" + "=" * 80)
    print("TEST 3: #include anidado (lib_principal.asm)")
    print("=" * 80)
    
    code = """
#include "lib/lib_principal.asm"

MAIN:
    LOADV R1, 5
    PRINT_SQUARE R1, IO_OUTPUT_1
    PARAR
"""
    
    print("\nCódigo original:")
    print(code)
    
    preprocessor = Preprocessor()
    resultado = preprocessor.preprocess(code)
    
    print("\nCódigo después del preprocesamiento:")
    print(resultado)
    print("\n" + "=" * 80)


def test_include_con_defines():
    """Prueba #include con #define propios"""
    print("\n\n" + "=" * 80)
    print("TEST 4: #include + #define locales")
    print("=" * 80)
    
    code = """
#include "lib/math.asm"
#include "lib/io.asm"

#define MI_NUMERO 25
#define MI_SALIDA 0x500

MAIN:
    LOADV R1, MI_NUMERO
    SQUARE R1
    PRINT_REG R1, MI_SALIDA
    PARAR
"""
    
    print("\nCódigo original:")
    print(code)
    
    preprocessor = Preprocessor()
    resultado = preprocessor.preprocess(code)
    
    print("\nCódigo después del preprocesamiento:")
    print(resultado)
    print("\n" + "=" * 80)


def test_archivo_ejemplo():
    """Prueba con archivos de ejemplo reales"""
    print("\n\n" + "=" * 80)
    print("TEST 5: Archivos de ejemplo del proyecto")
    print("=" * 80)
    
    ejemplos = [
        "Algoritmos/ejemplo_include_basico.asm",
        "Algoritmos/ejemplo_include_multiple.asm",
        "Algoritmos/ejemplo_include_completo.asm",
        "Algoritmos/ejemplo_include_anidado.asm"
    ]
    
    for ejemplo in ejemplos:
        if not os.path.exists(ejemplo):
            print(f"\n⚠️  Archivo no encontrado: {ejemplo}")
            continue
        
        print(f"\n{'─' * 80}")
        print(f"Archivo: {ejemplo}")
        print('─' * 80)
        
        with open(ejemplo, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print("\nCódigo original:")
        print(code[:200] + "..." if len(code) > 200 else code)
        
        preprocessor = Preprocessor()
        try:
            resultado = preprocessor.preprocess(code)
            print(f"\n✓ Preprocesamiento exitoso ({len(resultado)} caracteres)")
            print("\nPrimeras líneas del resultado:")
            lineas = resultado.split('\n')[:15]
            print('\n'.join(lineas))
            if len(resultado.split('\n')) > 15:
                print("...")
        except Exception as e:
            print(f"\n✗ Error: {e}")


def test_ensamblado_completo():
    """Prueba ensamblar un archivo con #include"""
    print("\n\n" + "=" * 80)
    print("TEST 6: Ensamblado completo con #include")
    print("=" * 80)
    
    code = """
#include "lib/io.asm"
#include "lib/math.asm"

INICIO:
    LOADV R1, 10
    LOADV R2, 5
    ADD R1, R2
    DOUBLE R1
    PRINT_REG R1, IO_OUTPUT_1
    PARAR
"""
    
    print("\nCódigo a ensamblar:")
    print(code)
    
    # Usar el ensamblador con preprocesador
    asm = Ensamblador(use_preprocessor=True)
    
    try:
        programa = asm.assemble(code)
        print(f"\n✓ Ensamblado exitoso!")
        print(f"Instrucciones generadas: {len(programa)}")
        print("\nBytecode:")
        for i, instr in enumerate(programa):
            print(f"  {i*8:04x}: {instr:016x}")
    except Exception as e:
        print(f"\n✗ Error de ensamblado: {e}")
        import traceback
        traceback.print_exc()


def verificar_bibliotecas():
    """Verifica que existan todas las bibliotecas"""
    print("\n\n" + "=" * 80)
    print("VERIFICACIÓN DE BIBLIOTECAS")
    print("=" * 80)
    
    bibliotecas = [
        "lib/io.asm",
        "lib/math.asm",
        "lib/stack.asm",
        "lib/utils.asm",
        "lib/lib_principal.asm"
    ]
    
    print("\nBibliotecas disponibles:")
    for lib in bibliotecas:
        existe = "✓" if os.path.exists(lib) else "✗"
        print(f"  {existe} {lib}")


def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "TEST DE #include" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Verificar bibliotecas primero
    verificar_bibliotecas()
    
    # Tests
    try:
        test_include_basico()
        test_include_multiple()
        test_include_anidado()
        test_include_con_defines()
        test_archivo_ejemplo()
        test_ensamblado_completo()
        
        print("\n\n" + "=" * 80)
        print("TODOS LOS TESTS COMPLETADOS")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error en tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
