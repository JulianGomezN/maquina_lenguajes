#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def limpiar_unicode(archivo_entrada, archivo_salida):
    """Reemplazar todos los caracteres Unicode problemáticos"""
    
    # Diccionario de reemplazos
    reemplazos = {
        # Caracteres de caja
        '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
        '─': '-', '│': '|',
        
        # Caracteres de caja dobles
        '═': '=', '║': '||',
        '╔': '+', '╗': '+', '╚': '+', '╝': '+',
        '╠': '+', '╣': '+', '╦': '+', '╩': '+', '╬': '+',
        
        # Flechas y símbolos
        '▼': 'v', '▲': '^', '◄': '<', '►': '>',
        '■': '*', '□': 'o', '●': '*', '○': 'o',
        '█': '#', '▌': '|', '▐': '|',
        '▀': '-', '▄': '_', '░': '.', '▒': ':', '▓': '#',
        
        # Símbolos matemáticos
        '−': '-', '×': 'x', '÷': '/', '±': '+/-',
        
        # Otros caracteres problemáticos
        ''': "'", ''': "'", '"': '"', '"': '"',
        '…': '...', '–': '-', '—': '--'
    }
    
    try:
        # Leer archivo original
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            lineas = f.readlines()

        # Aplicar reemplazos y eliminar líneas que solo contienen '---' (con o sin espacios)
        nuevas_lineas = []
        for linea in lineas:
            l = linea.strip()
            if l == '---':
                continue  # Omitir línea separadora
            # Reemplazos unicode
            for unicode_char, ascii_char in reemplazos.items():
                linea = linea.replace(unicode_char, ascii_char)
            nuevas_lineas.append(linea)

        # Escribir archivo limpio
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.writelines(nuevas_lineas)

        print(f"✓ Archivo limpio creado: {archivo_salida}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    archivo_entrada = "Tarea14_GrupoD_Hexacore_Atlas.md"
    archivo_salida = "Tarea14_Limpio.md"
    
    if not os.path.exists(archivo_entrada):
        print(f"✗ Error: No se encuentra {archivo_entrada}")
        sys.exit(1)
    
    success = limpiar_unicode(archivo_entrada, archivo_salida)
    sys.exit(0 if success else 1)