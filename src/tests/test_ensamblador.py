"""
Script para validar solo el ensamblado
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from compiler.ensamblador import Ensamblador

codigo_asm = """
; Cargar 5 en R1 y calcular su cuadrado
LOADV R1, 5
MUL8 R1, R1

; Duplicar un número en R2
LOADV R2, 7
ADD8 R2, R2

; Resultado en R0
MOV8 R0, R2

PARAR
"""

print("Código Assembly:")
print(codigo_asm)
print("\nEnsamblando...")

assembler = Ensamblador()
binario = assembler.assemble(codigo_asm)

print("\nCódigo Binario Generado:")
print(binario)
