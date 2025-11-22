"""
Script de prueba para el preprocesador
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.preprocessor import Preprocessor
from compiler.ensamblador import Ensamblador

def test_preprocessor():
    print("=" * 80)
    print("PRUEBA DEL PREPROCESADOR")
    print("=" * 80)
    
    # Código de ejemplo
    code = """
; Definir constantes
#define SIZE 100
#define MAX 50

; Macro simple
.macro SAVE_REGS
    PUSH8 R0
    PUSH8 R1
.endmacro

; Macro con parámetros
.macro ADD_NUM reg, val
    ADDV reg, val
.endmacro

; Programa
LOADV R0, SIZE
ADD_NUM R1, MAX

SAVE_REGS

#ifdef DEBUG
    LOADV R2, 1
#else
    LOADV R2, 0
#endif

PARAR
"""
    
    print("\n" + "=" * 80)
    print("CÓDIGO ORIGINAL:")
    print("=" * 80)
    print(code)
    
    # Preprocesar
    preprocessor = Preprocessor()
    processed = preprocessor.preprocess(code)
    
    print("\n" + "=" * 80)
    print("CÓDIGO PREPROCESADO:")
    print("=" * 80)
    print(processed)
    
    print("\n" + "=" * 80)
    print("DEFINES ENCONTRADOS:")
    print("=" * 80)
    for name, value in preprocessor.get_defines().items():
        print(f"  {name} = {value}")
    
    print("\n" + "=" * 80)
    print("MACROS ENCONTRADAS:")
    print("=" * 80)
    for name, macro in preprocessor.get_macros().items():
        params = ', '.join(macro['params']) if macro['params'] else 'sin parámetros'
        print(f"  {name}({params})")
    
    print("\n" + "=" * 80)
    print("ENSAMBLADO:")
    print("=" * 80)
    
    # Ensamblar el código preprocesado
    assembler = Ensamblador(use_preprocessor=True)
    try:
        program = assembler.assemble(code)
        print(f"✅ Ensamblado exitoso: {len(program)} instrucciones generadas")
        
        # Mostrar las primeras instrucciones
        print("\nPrimeras instrucciones:")
        for i, instr in enumerate(program[:10]):
            disasm = assembler.disassemble_instruction(instr)
            print(f"  {i:03d}: 0x{instr:016X}  {disasm}")
            
        if len(program) > 10:
            print(f"  ... ({len(program) - 10} instrucciones más)")
            
    except Exception as e:
        print(f"❌ Error al ensamblar: {str(e)}")
    
    print("\n" + "=" * 80)

def test_file():
    """Prueba con el archivo de ejemplo"""
    print("\n\n" + "=" * 80)
    print("PRUEBA CON ARCHIVO EXTERNO")
    print("=" * 80)
    
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Algoritmos",
        "ejemplo_preprocesador.asm"
    )
    
    if not os.path.exists(filepath):
        print(f"❌ Archivo no encontrado: {filepath}")
        return
    
    print(f"\nArchivo: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("\n" + "=" * 80)
    print("CÓDIGO ORIGINAL:")
    print("=" * 80)
    print(code)
    
    # Ensamblar con preprocesador
    assembler = Ensamblador(use_preprocessor=True)
    try:
        program = assembler.assemble(code, source_file=filepath)
        print("\n" + "=" * 80)
        print(f"✅ ENSAMBLADO EXITOSO: {len(program)} instrucciones")
        print("=" * 80)
        
        # Mostrar código desensamblado
        print("\nCódigo desensamblado:")
        for i, instr in enumerate(program):
            addr = i * 8
            disasm = assembler.disassemble_instruction(instr)
            print(f"  {addr:04X}: {instr:016X}  {disasm}")
            
    except Exception as e:
        print(f"\n❌ Error al ensamblar: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_preprocessor()
    test_file()
