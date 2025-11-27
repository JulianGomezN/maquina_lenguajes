"""
Script para probar el flujo Assembly → Binario → Ejecución
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from compiler.Preprocessor import preprocess
from compiler.ensamblador import Ensamblador
from compiler.Loader import Loader
from machine.Memory.Memory import Memory
from machine.CPU.CPU import CPU
from machine.IO.IOsystem import IOSystem
from machine.IO.Devices import Screen, Keyboard

def main():
    print("=" * 70)
    print("PRUEBA: ASSEMBLY DIRECTO → BINARIO → EJECUCIÓN")
    print("=" * 70)
    
    # 1. Cargar archivo Assembly
    print("\n[1] Cargando archivo Assembly...")
    with open("test_simple.asm", "r", encoding="utf-8") as f:
        codigo_asm = f.read()
    
    print(f"✓ Archivo cargado ({len(codigo_asm)} caracteres)")
    
    # 2. Preprocesar (para #include)
    print("\n[2] Preprocesando (expandir #include)...")
    try:
        codigo_preprocesado = preprocess(codigo_asm)
        print(f"✓ Preprocesado exitoso ({len(codigo_preprocesado)} caracteres)")
    except Exception as e:
        print(f"✗ Error en preprocesado: {e}")
        return
    
    # 3. Ensamblar
    print("\n[3] Ensamblando a código binario...")
    try:
        assembler = Ensamblador()
        codigo_binario = assembler.assemble(codigo_preprocesado)
        print(f"✓ Ensamblado exitoso")
        
        lineas = codigo_binario.strip().split('\n')
        print(f"  Total de instrucciones: {len([l for l in lineas if l.strip() and not l.startswith('[')])} ")
        
    except Exception as e:
        print(f"✗ Error en ensamblado: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Cargar en memoria
    print("\n[4] Cargando en memoria...")
    try:
        memory = Memory(2**16)
        loader = Loader(memory)
        loader.load_in_memory(codigo_binario, 0)
        print(f"✓ Código cargado en memoria desde dirección 0x0000")
        
    except Exception as e:
        print(f"✗ Error al cargar: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Crear CPU e I/O
    print("\n[5] Inicializando CPU...")
    try:
        io_system = IOSystem()
        screen = Screen()
        keyboard = Keyboard()
        io_system.register(0x100, screen)
        io_system.register(0x200, keyboard)
        
        cpu = CPU(memory, io_system)
        cpu.set_pc(0)
        cpu.set_sp(memory.size // 2)
        
        print(f"✓ CPU inicializado (PC={hex(cpu.pc)}, SP={hex(cpu.sp.read(8))})")
        
    except Exception as e:
        print(f"✗ Error al inicializar CPU: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. Ejecutar
    print("\n[6] Ejecutando programa...")
    print("-" * 70)
    
    max_steps = 1000
    step_count = 0
    
    try:
        while cpu.running and step_count < max_steps:
            ins = cpu.fetch()
            cpu.execute(ins)
            step_count += 1
            
            # Mostrar primeros pasos
            if step_count <= 20:
                pc_before = cpu.pc - 8
                print(f"  Paso {step_count:3d}: PC={hex(pc_before):6s}")
        
        if not cpu.running:
            print(f"\n✓ Programa terminado normalmente")
        else:
            print(f"\n⚠ Límite de {max_steps} pasos alcanzado")
            
        print(f"  Total de instrucciones ejecutadas: {step_count}")
        
    except Exception as e:
        print(f"\n✗ Error en paso {step_count}: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Mostrar resultados
    print("\n[7] Resultados:")
    print("-" * 70)
    print(f"  Flags: Z={cpu.flags['Z']} N={cpu.flags['N']} C={cpu.flags['C']} V={cpu.flags['V']}")
    
    print(f"\n  Primeros 8 registros:")
    for i in range(8):
        val = cpu.registers[i].read(8)
        print(f"    R{i:02d} = {val:20d} (0x{val:016X})")
    
    if hasattr(screen, 'buffer') and screen.buffer:
        print(f"\n  Salida de pantalla:")
        print(f"    '{screen.buffer}'")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()
