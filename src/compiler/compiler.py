# compiler.py
# Función principal de compilación que integra todas las fases

from compiler.syntax_analizer import parse
from compiler.semantic_analyzer import analyze


def compile_code(code, debug=False):
    """
    Compila código fuente pasando por todas las fases:
    1. Análisis léxico y sintáctico
    2. Análisis semántico
    
    Args:
        code: String con el código fuente
        debug: Booleano para activar modo debug
    
    Returns:
        tuple: (ast, success, errors)
            - ast: AST parseado (None si hay errores sintácticos)
            - success: True si no hay errores, False si hay errores
            - errors: Lista de mensajes de error
    """
    errors = []
    
    # Fase 1: Análisis sintáctico
    ast = parse(code, debug=debug)
    
    if ast is None:
        errors.append("Error de sintaxis: no se pudo parsear el código")
        return None, False, errors
    
    # Fase 2: Análisis semántico
    semantic_success, semantic_errors = analyze(ast)
    errors.extend(semantic_errors)
    
    success = len(errors) == 0
    
    return ast, success, errors


def compile_file(filename, debug=False):
    """
    Compila un archivo fuente
    
    Args:
        filename: Ruta al archivo fuente
        debug: Booleano para activar modo debug
    
    Returns:
        tuple: (ast, success, errors)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        return compile_code(code, debug=debug)
    except FileNotFoundError:
        return None, False, [f"Archivo no encontrado: {filename}"]
    except Exception as e:
        return None, False, [f"Error al leer archivo: {str(e)}"]


if __name__ == "__main__":
    import sys
    
    # Leer código desde stdin
    code = sys.stdin.read()
    
    # Compilar
    print("=== INICIANDO COMPILACIÓN ===\n")
    print("Fase 1: Análisis Sintáctico...")
    ast, success, errors = compile_code(code, debug=False)
    
    if ast:
        print("✓ Análisis sintáctico exitoso\n")
        print("Fase 2: Análisis Semántico...")
        
        if success:
            print("[OK] Análisis semántico exitoso\n")
            print("=== COMPILACIÓN EXITOSA ===")
            print(f"\nAST Raíz: {ast}")
            print(f"Declaraciones encontradas: {len(ast.declarations)}\n")
            
            # Imprimir resumen de declaraciones
            for i, decl in enumerate(ast.declarations, 1):
                print(f"{i}. {decl}")
        else:
            print("[ERROR] Análisis semántico falló\n")
            print("=== ERRORES SEMÁNTICOS ===")
            for error in errors:
                print(f"  - {error}")
    else:
        print("[ERROR] Análisis sintáctico falló\n")
        print("=== ERRORES ===")
        for error in errors:
            print(f"  - {error}")

