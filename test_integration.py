"""
Programa de prueba para demostrar la integración completa del simulador
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from CPU import CPU
from disco_64bits import Disco  
from assembler import Assembler

def test_integration():
    """Prueba la integración entre CPU, Disco y Assembler"""
    
    print("=== PRUEBA DE INTEGRACIÓN DEL SIMULADOR ===\n")
    
    # Crear componentes
    cpu = CPU()
    disco = Disco()
    assembler = Assembler()
    
    # Programa de prueba más complejo
    programa_texto = """
    ; Programa que calcula factorial de 4
    LOADV R1, 4      ; n = 4
    LOADV R2, 1      ; factorial = 1
    
    FACTORIAL_LOOP:
    CMPV R1, 0       ; comparar n con 0
    JEQ FIN          ; si n == 0, terminar
    
    MUL R2, R1       ; factorial *= n
    DEC R1           ; n--
    JMP FACTORIAL_LOOP
    
    FIN:
    ; Guardar resultado en I/O
    SVIO R2, 0x100   ; guardar factorial en IO[0x100]
    SHOWIO 0x100     ; mostrar resultado
    
    ; Guardar también en memoria del disco (simulando)
    STOREV R2, 1000  ; almacenar en dirección 1000
    
    PARAR
    """
    
    print("Código fuente:")
    print(programa_texto)
    print("\n" + "="*50 + "\n")
    
    # Ensamblar programa
    try:
        programa_binario = assembler.assemble(programa_texto)
        print("Programa ensamblado exitosamente:")
        for i, instr in enumerate(programa_binario):
            addr = i * 8
            desasm = assembler.disassemble_instruction(instr)
            print(f"{addr:04x}: {instr:016x} ; {desasm}")
        print()
    except Exception as e:
        print(f"Error al ensamblar: {e}")
        return
    
    # Cargar programa en CPU
    cpu.load_program(programa_binario, start=0)
    print("Programa cargado en CPU")
    print(f"PC inicial: {cpu.pc}")
    print()
    
    # Ejecutar programa
    print("Ejecutando programa...")
    try:
        cpu.run(max_cycles=1000)
        print("Programa terminado exitosamente")
    except Exception as e:
        print(f"Error durante ejecución: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Mostrar estado final
    print("Estado final del CPU:")
    cpu.dump_state()
    print()
    
    # Interacción con disco (ejemplo)
    print("Interacción con disco de memoria:")
    
    # Escribir algunos valores en el disco
    disco.escribir("R00", "1010")  # Registro R00 = 1010 (binario)
    disco.escribir("M0", "1111000011110000" + "0" * 48)  # Memoria M0
    
    # Leer valores del disco
    print(f"Registro R00 del disco: {disco.leer('R00')}")
    print(f"Memoria M0 del disco: {disco.leer('M0')}")
    
    print("\n=== PRUEBA COMPLETADA ===")

if __name__ == "__main__":
    test_integration()