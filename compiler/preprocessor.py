"""
Preprocesador para el lenguaje Assembly
Maneja macros, inclusión de archivos y compilación condicional
Usa PLY Lex para el análisis léxico
"""

import ply.lex as lex
import os
import re


class Preprocessor:
    """Preprocesador que maneja directivas antes del ensamblado"""
    
    def __init__(self):
        self.macros = {}  # Diccionario de macros definidas
        self.defines = {}  # Diccionario de constantes #define
        self.included_files = set()  # Archivos ya incluidos (evitar recursión)
        self.conditional_stack = []  # Stack para #ifdef/#ifndef
        self.base_path = ""  # Ruta base para buscar archivos incluidos
        
    def preprocess(self, source_code, base_path="."):
        """
        Preprocesa el código fuente
        
        Args:
            source_code: Código fuente a preprocesar
            base_path: Ruta base para buscar archivos incluidos
            
        Returns:
            Código preprocesado listo para ensamblar
        """
        self.base_path = base_path
        self.included_files.clear()
        self.conditional_stack = []
        
        lines = source_code.split('\n')
        processed_lines = []
        skip_lines = False  # Para manejar bloques condicionales
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Procesar directivas
            if line.startswith('#'):
                directive_result = self._process_directive(line, skip_lines)
                
                if directive_result is not None:
                    if isinstance(directive_result, dict):
                        # Cambio de estado condicional
                        skip_lines = directive_result.get('skip', skip_lines)
                    elif isinstance(directive_result, str):
                        # Contenido a incluir
                        processed_lines.append(directive_result)
                    elif isinstance(directive_result, list):
                        # Múltiples líneas (archivo incluido)
                        processed_lines.extend(directive_result)
            
            elif line.startswith('.'):
                # Procesar macros estilo .macro
                macro_result = self._process_macro_directive(line, lines, i)
                if macro_result:
                    if 'skip_to' in macro_result:
                        i = macro_result['skip_to']
                        i += 1
                        continue
            
            elif not skip_lines:
                # Expandir macros y defines en la línea
                expanded_line = self._expand_line(line)
                if expanded_line:
                    processed_lines.append(expanded_line)
            
            i += 1
        
        return '\n'.join(processed_lines)
    
    def _process_directive(self, line, currently_skipping):
        """Procesa directivas de preprocesador (#define, #include, etc.)"""
        
        # #define NOMBRE valor
        if line.startswith('#define'):
            if currently_skipping:
                return None
            
            parts = line[7:].strip().split(None, 1)
            if len(parts) >= 1:
                name = parts[0]
                value = parts[1] if len(parts) > 1 else '1'
                self.defines[name] = value
            return None
        
        # #undef NOMBRE
        elif line.startswith('#undef'):
            if currently_skipping:
                return None
            
            name = line[6:].strip()
            if name in self.defines:
                del self.defines[name]
            return None
        
        # #include "archivo.asm"
        elif line.startswith('#include'):
            if currently_skipping:
                return None
            
            # Extraer nombre del archivo
            match = re.search(r'["\']([^"\']+)["\']', line)
            if match:
                filename = match.group(1)
                return self._include_file(filename)
            return None
        
        # #ifdef NOMBRE
        elif line.startswith('#ifdef'):
            name = line[6:].strip()
            is_defined = name in self.defines
            self.conditional_stack.append({
                'type': 'ifdef',
                'condition': is_defined,
                'active': is_defined and not currently_skipping
            })
            return {'skip': not (is_defined and not currently_skipping)}
        
        # #ifndef NOMBRE
        elif line.startswith('#ifndef'):
            name = line[7:].strip()
            is_not_defined = name not in self.defines
            self.conditional_stack.append({
                'type': 'ifndef',
                'condition': is_not_defined,
                'active': is_not_defined and not currently_skipping
            })
            return {'skip': not (is_not_defined and not currently_skipping)}
        
        # #else
        elif line.startswith('#else'):
            if self.conditional_stack:
                current = self.conditional_stack[-1]
                # Invertir la condición
                was_active = current['active']
                current['active'] = not current['condition'] and not currently_skipping
                return {'skip': not current['active']}
            return None
        
        # #endif
        elif line.startswith('#endif'):
            if self.conditional_stack:
                self.conditional_stack.pop()
                # Restaurar estado anterior
                if self.conditional_stack:
                    return {'skip': not self.conditional_stack[-1]['active']}
                else:
                    return {'skip': False}
            return None
        
        return None
    
    def _process_macro_directive(self, line, all_lines, current_index):
        """Procesa macros estilo .macro"""
        
        # .macro NOMBRE [parámetros]
        if line.startswith('.macro'):
            rest_of_line = line[6:].strip()
            if not rest_of_line:
                return None
            
            # Separar nombre de los parámetros
            parts = rest_of_line.split(None, 1)  # Dividir solo por el primer espacio
            macro_name = parts[0]
            
            # Procesar parámetros (pueden estar separados por comas o espacios)
            if len(parts) > 1:
                param_string = parts[1]
                # Separar por comas
                macro_params = [p.strip() for p in param_string.split(',')]
            else:
                macro_params = []
            
            # Buscar el .endmacro
            macro_body = []
            i = current_index + 1
            while i < len(all_lines):
                if all_lines[i].strip().startswith('.endmacro'):
                    break
                macro_body.append(all_lines[i])
                i += 1
            
            # Guardar la macro
            self.macros[macro_name] = {
                'params': macro_params,
                'body': macro_body
            }
            
            return {'skip_to': i}  # Saltar hasta después del .endmacro
        
        return None
    
    def _include_file(self, filename):
        """Incluye un archivo externo"""
        
        # Construir ruta completa
        filepath = os.path.join(self.base_path, filename)
        
        # Evitar inclusión recursiva
        if filepath in self.included_files:
            return None
        
        self.included_files.add(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Preprocesar el contenido incluido recursivamente
            included_dir = os.path.dirname(filepath)
            preprocessor = Preprocessor()
            preprocessor.defines = self.defines.copy()
            preprocessor.macros = self.macros.copy()
            
            processed_content = preprocessor.preprocess(content, included_dir)
            
            # Actualizar defines y macros del archivo incluido
            self.defines.update(preprocessor.defines)
            self.macros.update(preprocessor.macros)
            
            return processed_content.split('\n')
            
        except FileNotFoundError:
            print(f"Warning: No se pudo encontrar el archivo incluido: {filename}")
            return None
        except Exception as e:
            print(f"Error al incluir archivo {filename}: {str(e)}")
            return None
    
    def _expand_line(self, line):
        """Expande macros y defines en una línea"""
        
        if not line or line.startswith(';'):
            return line
        
        # Primero, verificar si es una invocación de macro
        words = line.split()
        if words and words[0] in self.macros:
            macro_name = words[0]
            # Separar argumentos de la macro (pueden estar separados por comas o espacios)
            rest_of_line = line[len(macro_name):].strip()
            if rest_of_line:
                # Dividir por comas
                macro_args = [arg.strip() for arg in rest_of_line.split(',')]
            else:
                macro_args = []
            return self._expand_macro(macro_name, macro_args)
        
        # Si no es una macro, expandir #defines
        for name, value in self.defines.items():
            # Usar word boundaries para evitar reemplazos parciales
            pattern = r'\b' + re.escape(name) + r'\b'
            line = re.sub(pattern, value, line)
        
        return line
    
    def _expand_macro(self, macro_name, args):
        """Expande una invocación de macro"""
        
        macro = self.macros[macro_name]
        params = macro['params']
        body = macro['body']
        
        # Crear diccionario de reemplazos parámetro -> argumento
        replacements = {}
        for i, param in enumerate(params):
            if i < len(args):
                replacements[param] = args[i]
        
        # Expandir el cuerpo de la macro
        expanded_lines = []
        for line in body:
            expanded_line = line
            
            # Reemplazar parámetros por argumentos
            for param, arg in replacements.items():
                pattern = r'\b' + re.escape(param) + r'\b'
                expanded_line = re.sub(pattern, arg, expanded_line)
            
            # Expandir defines dentro del cuerpo de la macro (pero NO otras macros)
            for name, value in self.defines.items():
                pattern = r'\b' + re.escape(name) + r'\b'
                expanded_line = re.sub(pattern, value, expanded_line)
            
            expanded_lines.append(expanded_line)
        
        return '\n'.join(expanded_lines)
    
    def get_defines(self):
        """Retorna el diccionario de defines actuales"""
        return self.defines.copy()
    
    def get_macros(self):
        """Retorna el diccionario de macros actuales"""
        return self.macros.copy()


# Ejemplo de uso
if __name__ == "__main__":
    # Código de ejemplo con directivas
    code = """
; Definir constantes
#define BUFFER_SIZE 1024
#define MAX_ITERATIONS 10

; Macro simple
.macro PUSH_ALL
    PUSH8 R0
    PUSH8 R1
    PUSH8 R2
.endmacro

; Macro con parámetros
.macro ADD_CONST reg, value
    ADDV reg, value
.endmacro

; Compilación condicional
#ifdef DEBUG
    LOADV R0, 1
#else
    LOADV R0, 0
#endif

; Usar constante
LOADV R1, BUFFER_SIZE

; Usar macro
ADD_CONST R2, 100

; Usar macro sin parámetros
PUSH_ALL

PARAR
"""
    
    preprocessor = Preprocessor()
    processed = preprocessor.preprocess(code)
    
    print("=" * 60)
    print("CÓDIGO ORIGINAL:")
    print("=" * 60)
    print(code)
    print("\n" + "=" * 60)
    print("CÓDIGO PREPROCESADO:")
    print("=" * 60)
    print(processed)
    print("\n" + "=" * 60)
    print("DEFINES:")
    print("=" * 60)
    for name, value in preprocessor.get_defines().items():
        print(f"  {name} = {value}")
    print("\n" + "=" * 60)
    print("MACROS:")
    print("=" * 60)
    for name, macro in preprocessor.get_macros().items():
        print(f"  {name}({', '.join(macro['params'])})")
