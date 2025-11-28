"""
Script de prueba para validar el pipeline completo de compilación
Prueba el archivo 1.txt con áreas y volúmenes
"""

import sys
import os

# Añadir el directorio src al path (subir dos niveles desde tests/)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Subir un nivel a src/
sys.path.insert(0, src_dir)

from compiler.Preprocessor import preprocess
from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.code_generator import generate_code
from compiler.ensamblador import Ensamblador
from compiler.Loader import Loader
from machine.Memory.Memory import Memory
from machine.CPU.CPU import CPU
from machine.IO.IOsystem import IOSystem
from machine.IO.Devices import Screen, Keyboard

def main():
    print("=" * 70)
    print("PRUEBA DEL PIPELINE COMPLETO - Áreas y Volúmenes")
    print("=" * 70)
    
    # Determinar la ruta base del proyecto (subir dos niveles desde tests/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Subir a la raíz del proyecto
    
    # 1. Cargar archivo de alto nivel
    print("\n[1] Cargando archivo de alto nivel...")
    archivo_path = os.path.join(project_root, "Algoritmos", "Ejemplos_alto_nivel", "1.txt")
    with open(archivo_path, "r", encoding="utf-8") as f:
        codigo_alto_nivel = f.read()
    
    print(f"✓ Archivo cargado ({len(codigo_alto_nivel)} caracteres)")
    print("\nCódigo original:")
    print("-" * 70)
    print(codigo_alto_nivel[:300] + "..." if len(codigo_alto_nivel) > 300 else codigo_alto_nivel)
    print("-" * 70)
    
    # 2. Preprocesar
    print("\n[2] Preprocesando (expansión de #include y macros)...")
    try:
        # Pasar la ruta base del proyecto para que el preprocesador encuentre lib/
        codigo_preprocesado = preprocess(codigo_alto_nivel, base_path=project_root)
        print(f"✓ Preprocesado exitoso ({len(codigo_preprocesado)} caracteres)")
        
        # Mostrar expansión de macros
        if "3.14159" in codigo_preprocesado:
            print("  ✓ Macro PI expandida correctamente")
        if "(radio) * (radio)" in codigo_preprocesado or "(x) * (x)" in codigo_preprocesado:
            print("  ✓ Macro CUADRADO expandida correctamente")
            
    except Exception as e:
        print(f"✗ Error en preprocesado: {e}")
        return
    
    # 3. Parsear (análisis léxico y sintáctico)
    print("\n[3] Parseando código (análisis léxico y sintáctico)...")
    try:
        ast = parse(codigo_preprocesado)
        
        if not ast:
            print(f"✗ Error: No se pudo generar el AST (error de sintaxis)")
            return
            
        print(f"✓ AST generado exitosamente")
        
    except Exception as e:
        print(f"✗ Error en parsing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Análisis semántico
    print("\n[4] Analizando semánticamente...")
    try:
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        
        if analyzer.errors:
            print(f"  ⚠ Se encontraron {len(analyzer.errors)} errores semánticos:")
            for error in analyzer.errors[:10]:  # Mostrar solo los primeros 10
                print(f"    • {error}")
            if len(analyzer.errors) > 10:
                print(f"    ... y {len(analyzer.errors)-10} más")
            
            # Continuar de todas formas para ver qué se genera
        else:
            print(f"✓ Análisis semántico exitoso (sin errores)")
        
    except Exception as e:
        print(f"✗ Error en análisis semántico: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Generar código Assembly
    print("\n[5] Generando código Assembly...")
    try:
        assembly_code = generate_code(ast, analyzer.symbol_table)
        
        if not assembly_code:
            print(f"✗ Error: No se generó código assembly")
            return
            
        print(f"✓ Generación de código exitosa")
        print(f"  Código Assembly generado ({len(assembly_code)} caracteres)")
        
        # Guardar assembly para inspección
        build_dir = os.path.join(project_root, "build")
        os.makedirs(build_dir, exist_ok=True)  # Crear directorio si no existe
        output_file = os.path.join(build_dir, "test_1_output.asm")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(assembly_code)
        print(f"  ✓ Assembly guardado en: {output_file}")
        
        # Mostrar primeras líneas
        lineas_asm = assembly_code.split('\n')
        print("  Primeras líneas del assembly:")
        for i, linea in enumerate(lineas_asm[:15]):
            print(f"    {linea}")
        
    except Exception as e:
        print(f"✗ Error en generación de código: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. Ensamblar a binario
    print("\n[6] Ensamblando a código binario...")
    try:
        assembler = Ensamblador()
        codigo_binario = assembler.assemble(assembly_code)
        print(f"✓ Ensamblado exitoso")
        print(f"  Código binario generado ({len(codigo_binario)} líneas)")
        
        # Mostrar primeras instrucciones
        lineas = codigo_binario.strip().split('\n')
        print("  Primeras instrucciones:")
        for i, linea in enumerate(lineas[:10]):
            print(f"    {linea}")
            
    except Exception as e:
        print(f"✗ Error en ensamblado: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 7. Cargar en memoria
    print("\n[7] Cargando en memoria virtual...")
    try:
        memory = Memory(2**16)
        loader = Loader(memory)
        
        start_addr = 0x0000
        absoluto_code, end_addr = loader.load_in_memory(codigo_binario, start_addr)
        program_size = end_addr - start_addr
        
        print(f"✓ Código cargado en memoria")
        print(f"  Dirección inicial: 0x{start_addr:04X}")
        print(f"  Dirección final:   0x{end_addr:04X}")
        print(f"  Tamaño total:      {program_size} bytes")
        
    except Exception as e:
        print(f"✗ Error al cargar en memoria: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 8. Crear CPU y sistema I/O
    print("\n[8] Inicializando CPU y sistema I/O...")
    try:
        io_system = IOSystem()
        screen = Screen()
        keyboard = Keyboard()
        io_system.register(0x100, screen)
        io_system.register(0x200, keyboard)
        
        cpu = CPU(memory, io_system)
        print(f"✓ CPU inicializado")
        print(f"  PC inicial: {cpu.pc:#06x}")
        print(f"  SP inicial: {cpu.sp.value:#06x} (será inicializado por el código)")
        
    except Exception as e:
        print(f"✗ Error al inicializar CPU: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 9. Ejecutar (con límite de pasos para evitar loops infinitos)
    print("\n[9] Ejecutando programa...")
    print("-" * 70)
    
    max_steps = 10000
    step_count = 0
    
    try:
        while cpu.running and step_count < max_steps:
            cpu.tick()
            step_count += 1
            
            # Mostrar primeros pasos
            if step_count <= 10:
                print(f"  Paso {step_count}: PC={hex(cpu.pc-8)}, Instrucción ejecutada")
        
        if not cpu.running:
            print(f"\n✓ Programa terminado normalmente")
            print(f"  Total de instrucciones ejecutadas: {step_count}")
        else:
            print(f"\n⚠ Programa detenido (límite de {max_steps} pasos alcanzado)")
            
    except Exception as e:
        print(f"\n✗ Error durante ejecución en paso {step_count}: {e}")
        import traceback
        traceback.print_exc()
    
    # 10. Mostrar estado final
    print("\n[10] Estado final del sistema:")
    print("-" * 70)
    print(f"  PC (Program Counter): {hex(cpu.pc)}")
    print(f"  SP (Stack Pointer):   {hex(cpu.sp.value)}")
    print(f"  Flags: Z={cpu.flags['Z']} N={cpu.flags['N']} C={cpu.flags['C']} V={cpu.flags['V']}")
    print(f"\n  Registros:")
    for i in range(16):
        val = cpu.registers[i].value
        print(f"    R{i:02d} = {val:20d} (0x{val:016X})")
    
    # Mostrar salida de pantalla si hay
    if hasattr(screen, 'buffer') and screen.buffer:
        print(f"\n  Salida de pantalla:")
        print(f"    {screen.buffer}")
    
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()
