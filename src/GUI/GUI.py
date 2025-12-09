import tkinter as tk
from tkinter import ttk, messagebox

import sys
import os
import io
from pprint import pformat

# Manejo de salida, usado al crear el AST para no modificar el archivo
from contextlib import redirect_stdout

# La CPU checkea si hay input, esto es para no bloquear el hilo de la GUI mientras hace esto
import threading

# Añadir el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from machine.CPU.CPU import CPU
from machine.IO.Devices import Screen, Keyboard
from compiler.ensamblador import Ensamblador, CodigoRelo
from compiler.Linker import Linker
from compiler.Loader import Loader
from compiler.Preprocessor import preprocess
from compiler.Lex_analizer import lexer as preprocessor_lexer
from compiler.ast_printer import print_ast
from compiler.syntax_analizer import parse as syntax_parse

class SimuladorGUI:
    def __init__(self, CPU:CPU, sdtout: Screen, stdin:Keyboard):

        # Inicializar componentes del simulador
        self.cpu = CPU
        self.machine_out = sdtout
        self.machine_in = stdin

        # Wire device callback so Screen.show forwards characters to GUI output
        try:
            # append raw without a leading newline
            def _on_machine_show(ch: str):
                try:
                    self.texto_salida.insert('end', ch)
                    self.texto_salida.see('end')
                except Exception:
                    pass
            self.machine_out.on_show = _on_machine_show
        except Exception:
            # If anything fails here, continue without GUI forwarding
            pass

        self.assembler = Ensamblador()
        self.linker = Linker()
        self.relocatables = []
        self.loader = Loader(self.cpu.memory)
        self.programa_actual = [] ##??
        self.ejecutando_paso_automatico = False

        # GUI base
        self.root = tk.Tk()
        self.root.title("Simulador Atlas")
        self.root.state("zoomed")
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)        
        self.fullscreen = False
        self._crear_columnas()
        self.update_gui()

    # ======================================================================
    #   CREACIÓN DE LAS CUATRO COLUMNAS
    # ======================================================================
    def _crear_columnas(self):
        cont = ttk.Frame(self.root)
        cont.pack(fill="both", expand=True, padx=10, pady=10)
        cont.pack_propagate(False) 

        cont.grid_columnconfigure(0, weight=1, uniform="cols")
        cont.grid_columnconfigure(1, weight=1, uniform="cols")
        cont.grid_columnconfigure(2, weight=1, uniform="cols")
        cont.grid_columnconfigure(3, weight=1, uniform="cols")
        cont.grid_rowconfigure(0, weight=1)

        col1 = ttk.Frame(cont)
        col2 = ttk.Frame(cont)
        col3 = ttk.Frame(cont)
        col4 = ttk.Frame(cont)

        col1.grid(row=0, column=0, sticky="nsew", padx=4)
        col2.grid(row=0, column=1, sticky="nsew", padx=4)
        col3.grid(row=0, column=2, sticky="nsew", padx=4)
        col4.grid(row=0, column=3, sticky="nsew", padx=4)
                
        self._columna_codigo_alto_nivel(col1)
        self._columna_codigo_assembler(col2)
        self._columna_codigo_relocalizable(col3)
        self._columna_ram_flags_registros(col4)
            
    # ======================================================================
    #   COLUMNA 1 – CÓDIGO ALTO NIVEL Y PREPROCESADO
    # ======================================================================
    def _columna_codigo_alto_nivel(self, parent):
        ttk.Label(parent, text="Código Alto Nivel", font=("Arial", 13, "bold")).pack()

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        self.texto_alto = tk.Text(frame, wrap="none", height=8)
        self.texto_alto.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.texto_alto.yview)
        sy.pack(side="right", fill="y")
        self.texto_alto.configure(yscrollcommand=sy.set)

        ttk.Button(parent, text="Preprocesar", command=self.preprocesar).pack(fill="x", pady=2)
        ttk.Button(parent, text="Cargar Archivo", command=self.cargar_archivo).pack(fill="x", pady=(2,5))

        # Preprocesado

        ttk.Label(parent, text="Código Preprocesado", font=("Arial", 13, "bold")).pack()

        frame_preprocessor = ttk.Frame(parent)
        frame_preprocessor.pack(fill="both", expand=True)

        self.texto_preprocesado = tk.Text(frame_preprocessor, wrap="none", height=8)
        self.texto_preprocesado.pack(side="left", fill="both", expand=True)

        sy_pre = ttk.Scrollbar(frame_preprocessor, orient="vertical", command=self.texto_preprocesado.yview)
        sy_pre.pack(side="right", fill="y")
        self.texto_preprocesado.configure(yscrollcommand=sy_pre.set)


        ttk.Button(parent, text="Compilar", command=self.compilar).pack(fill="x", pady=2)

        frame_buttoms = ttk.Frame(parent)
        frame_buttoms.pack(fill="x", expand=False)

        ttk.Button(frame_buttoms, text="A.Lexico", command=self._abrir_ventana_analizador_lexico).pack(side="left",fill="x", pady=2, expand=True)
        ttk.Button(frame_buttoms, text="A.Sintactico", command=self._abrir_ventana_analizador_sintactico).pack(side="left",fill="x", pady=2, expand=True)
        
        ttk.Button(parent, text="Reset", command=self.reset_cpu).pack(fill="x", pady=2)

    # ======================================================================
    #   COLUMNA 2 – CÓDIGO ASSEMBLER
    # ======================================================================
    def _columna_codigo_assembler(self, parent):
        ttk.Label(parent, text="Código Assembler", font=("Arial", 13, "bold")).pack()

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        self.texto_asm = tk.Text(frame, wrap="none")
        self.texto_asm.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.texto_asm.yview)
        sy.pack(side="right", fill="y")
        self.texto_asm.configure(yscrollcommand=sy.set)

        ttk.Button(parent, text="Ensamblar", command=self.ensamblar).pack(fill="x", pady=2)
        ttk.Button(parent, text="Cargar Archivo", command=self.cargar_archivo_asm).pack(fill="x", pady=2)
        ttk.Button(parent, text="Ensamblar y guardar .relo", command=self.save_archivo_relo).pack(fill="x", pady=2)


    # ======================================================================
    #   COLUMNA 3 – RELOCALIZABLE + SALIDA
    # ======================================================================

    def _columna_codigo_relocalizable(self, parent):


        for r in range(11):
            parent.grid_rowconfigure(r, weight=0)

        parent.grid_rowconfigure(10, weight=1)      # Visor de log
        parent.grid_rowconfigure(1, weight=3)       # Código relocalizable
        parent.grid_columnconfigure(0, weight=1)

        # ================================
        # ===== Código relocalizable =====
        # ================================
        ttk.Label(parent, text="Código Relocalizable",
                font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="n", pady=(0, 5))

        frame = ttk.Frame(parent)
        frame.grid(row=1, column=0, sticky="nsew")

        self.texto_relo = tk.Text(frame, wrap="none")
        self.texto_relo.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.texto_relo.yview)
        sy.pack(side="right", fill="y")
        self.texto_relo.configure(yscrollcommand=sy.set)

        # ================================
        # ==== Dirección de carga ========
        # ================================
        ttk.Label(parent, text="Dirección de carga (hex):").grid(row=2, column=0, sticky="w")
        self.entrada_direccion = ttk.Entry(parent)
        self.entrada_direccion.grid(row=3, column=0, sticky="ew", pady=2)
        # Valor por defecto para la dirección de carga
        try:
            self.entrada_direccion.insert(0, "0")
        except Exception:
            pass
        ttk.Button(parent, text="Cargar relocalizables",
                command=self.load_relos).grid(row=4, column=0, sticky="ew", pady=(2,5))
        
        ttk.Button(parent, text="Enlazar y Cargar",
                command=self.enlazar_y_cargar).grid(row=5, column=0, sticky="ew", pady=(2,5))

        # =================================
        # ====== Botones Ejecución ========
        # =================================
        ttk.Label(parent, text="Ejecución:").grid(row=6, column=0, sticky="w", pady=(10, 2))

        frame_botones = ttk.Frame(parent)
        frame_botones.grid(row=7, column=0, sticky="ew")

        frame_botones.grid_columnconfigure(0, weight=1)

        ttk.Button(frame_botones, text="Siguiente instrucción",
                command=self.ejecutar_paso).grid(row=0, column=0, sticky="ew", pady=2)

        ttk.Button(frame_botones, text="Ejecutar todo",
                command=self.ejecutar_programa_completo).grid(row=1, column=0, sticky="ew", pady=2)

        ttk.Button(frame_botones, text="Ejecutar todo paso a paso",
                command=self.ejecutar_programa_detallado).grid(row=2, column=0, sticky="ew", pady=2)

        self.boton_parar = ttk.Button(frame_botones, text="Parar ejecución",
                                    command=self.parar_ejecucion)
        self.boton_parar.grid(row=3, column=0, sticky="ew", pady=2)

        # =================================
        # ====== Visor de LOG  ++ ======
        # =================================
        ttk.Label(parent, text="Mensajes / Log:").grid(row=9, column=0, sticky="w", pady=(10, 2))

        frame_log = ttk.Frame(parent)
        frame_log.grid(row=10, column=0, sticky="nsew")

        frame_log.grid_columnconfigure(0, weight=1)
        frame_log.grid_rowconfigure(0, weight=1)

        self.texto_log = tk.Text(frame_log, wrap="word", height=5)
        self.texto_log.grid(row=0, column=0, sticky="nsew")

        sy_log = ttk.Scrollbar(frame_log, orient="vertical", command=self.texto_log.yview)
        sy_log.grid(row=0, column=1, sticky="ns")
        self.texto_log.configure(yscrollcommand=sy_log.set)

    # ======================================================================
    #   COLUMNA 4 – RAM + FLAGS + REGISTROS
    # ======================================================================
    def _columna_ram_flags_registros(self, parent):

        parent.columnconfigure(0, weight=1)   # que se expanda
        parent.rowconfigure(1, weight=1)      # RAM se expande

        # ======================================
        # =============== RAM ==================
        # ======================================
        ttk.Label(parent, text="RAM", font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="w")

        frame_ram = ttk.Frame(parent, borderwidth=2, relief="solid")
        frame_ram.grid(row=1, column=0, sticky="ew", pady=3)

        self.abrir_visor_ram(frame_ram)

        # ======================================
        # =========== FLAGS + PC/SP ============
        # ======================================
        cont_flags_punteros = ttk.Frame(parent)
        cont_flags_punteros.grid(row=2, column=0, sticky="ew", pady=5)
        cont_flags_punteros.columnconfigure(0, weight=1)
        cont_flags_punteros.columnconfigure(1, weight=1)

        # Subtítulos
        ttk.Label(cont_flags_punteros, text="Flags", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(cont_flags_punteros, text="Punteros", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w")

        # subframes
        frame_flags = ttk.Frame(cont_flags_punteros)
        frame_flags.grid(row=1, column=0, sticky="nw")

        frame_punteros = ttk.Frame(cont_flags_punteros)
        frame_punteros.grid(row=1, column=1, sticky="nw")

        # FLAGS
        self.flags = {}

        for flag in ["Z (Zero)", "N (Negative)", "C (Carry)", "V (Overflow)"]:
            f = ttk.Frame(frame_flags)
            f.pack(fill="x", pady=1)
            ttk.Label(f, text=flag, width=12).pack(side="left")
            lbl = ttk.Label(f, text="0", width=6, relief="solid", anchor="center")
            lbl.pack(side="left")
            self.flags[flag] = lbl

        # PC, SP y BP
        self.punteros = {}

        for p in ["PC (Program Counter)", "SP (Stack Pointer)", "BP (Base Pointer)"]:
            f = ttk.Frame(frame_punteros)
            f.pack(fill="x", pady=1)
            ttk.Label(f, text=p, width=20).pack(side="left")
            lbl = ttk.Label(f, text="0", width=8, relief="solid", anchor="center")
            lbl.pack(side="left")
            self.punteros[p] = lbl

        # ======================================
        # ============== REGISTROS =============
        # ======================================
        ttk.Label(parent, text="Registros", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", pady=5)

        reg_frame = ttk.Frame(parent)
        reg_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 5))
        
        # Configurar columnas del grid para que se expandan uniformemente
        for c in range(4):
            reg_frame.columnconfigure(c, weight=1)

        self.registros = {}

        for i in range(16):
            row = i // 4
            col = i % 4

            frame = ttk.Frame(reg_frame)
            frame.grid(row=row, column=col, padx=(2,10), pady=1, sticky="ew")

            reg_name = f"R{i:02}"
            ttk.Label(frame, text=reg_name, width=3).pack(side="left", padx=(0,5))

            valor = ttk.Label(frame, text="0", width=12, relief="solid", anchor="e", font=("Courier", 9))
            valor.pack(side="left", fill="x", expand=True, padx=(0,0))

            self.registros[reg_name] = valor

        # ======================================
        # =============== SALIDA ===============
        # ======================================
        ttk.Label(parent, text="Salida", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w")

        frame_s = ttk.Frame(parent)
        frame_s.grid(row=6, column=0, sticky="nsew")

        parent.rowconfigure(6, weight=1)  # salida crece

        self.texto_salida = tk.Text(frame_s, wrap="word")
        self.texto_salida.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame_s, orient="vertical", command=self.texto_salida.yview)
        sy.pack(side="right", fill="y")
        self.texto_salida.configure(yscrollcommand=sy.set)

        # ======================================
        # =============== ENTRADA ==============
        # ======================================
        ttk.Label(parent, text="Entrada: ", font=("Arial", 13, "bold")).grid(row=7, column=0, sticky="w")

        self.entrada_maquina = ttk.Entry(parent)
        self.entrada_maquina.grid(row=8, column=0, sticky="ew", pady=3)

        self.entrada_maquina.bind('<Return>', self.procesar_entrada_maquina)


    # ======================================================================
    #   FUNCIONES
    # ======================================================================

    def toggle_fullscreen(self, event=None):
        """Alternar entre pantalla completa y ventana normal"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.root.state('zoomed')  # Maximizar en Windows
        else:
            self.root.state('normal')  # Ventana normal
            self.root.geometry("1400x900")  # Tamaño por defecto   


    # ========== Metodos ==========

    def cargar_archivo(self):
        """Carga un archivo de texto externo en el área de programa"""
        from tkinter import filedialog
        
        # Abrir diálogo para seleccionar archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programa",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos Assembly", "*.asm"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.join(os.path.dirname(__file__), "..", "..", "Algoritmos")
        )
        
        if archivo:
            try:
                # Leer el contenido del archivo
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Limpiar y cargar en el área de texto
                self.texto_alto.delete("1.0", "end")
                self.texto_alto.insert("1.0", contenido)
                
                # Mostrar mensaje de éxito
                nombre_archivo = os.path.basename(archivo)
                self.set_log(f"Archivo '{nombre_archivo}' cargado exitosamente.\nHaz clic en 'Preprocesar' para preprocesar el programa.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
                self.set_salida(f"Error al cargar archivo: {str(e)}")
    
    def cargar_archivo_asm(self):
        """Carga un archivo de texto externo en el área de programa"""
        from tkinter import filedialog
        
        # Abrir diálogo para seleccionar archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de programa",
            filetypes=[
                ("Archivos Assembly", "*.asm"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.join(os.path.dirname(__file__), "..", "Algoritmos")
        )
        
        if archivo:
            try:
                # Leer el contenido del archivo
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Limpiar y cargar en el área de texto
                self.texto_asm.delete("1.0", "end")
                self.texto_asm.insert("1.0", contenido)
                
                # Mostrar mensaje de éxito
                nombre_archivo = os.path.basename(archivo)
                self.set_log(f"Archivo '{nombre_archivo}' cargado exitosamente.\nHaz clic en 'Cargar Programa' para ensamblarlo.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
                self.set_salida(f"Error al cargar archivo: {str(e)}")
    
    def obtener_direccion_carga(self):
        """Obtiene la dirección de carga desde el campo de entrada"""
        try:
            direccion_texto = self.entrada_direccion.get().strip()
            
            # Permitir formato hexadecimal (0x...) o decimal
            if direccion_texto.lower().startswith('0x'):
                return int(direccion_texto, 16)
            else:
                return int(direccion_texto)
                
        except ValueError:
            # Si hay error, usar 0 por defecto
            messagebox.showwarning("Dirección inválida", 
                                 f"Dirección '{self.entrada_direccion.get()}' no válida. Usando 0.")
            self.entrada_direccion.delete(0, 'end')
            self.entrada_direccion.insert(0, "0")
            return 0

    def preprocesar(self):
        codigo = self.texto_alto.get("1.0", "end")

        codigo_preprocesado = preprocess(codigo)
        #
        # Aqui va la logica de traduccion de alto nivel a a codigo preprocesado
        #
        self.texto_preprocesado.insert("1.0", codigo_preprocesado)

        self.set_log(f"✓ Preprocesado exitoso. \nHaz clic en 'Compilar' para Compilar el programa. \nPuedes dar click en A.Lexico para ver los tokens o en A.Sintactico para ver el arbol sintactico.")

    def analizador_lexico(self, codigo):
        preprocessor_lexer.input(codigo)
        tokens = ""
        while True:
            tok = preprocessor_lexer.token()
            if not tok:
                break
            tokens += f"{tok}\n"
        return tokens

    def compilar(self):
        """Compila código de alto nivel a Assembly Atlas"""
        codigo = self.texto_preprocesado.get("1.0", "end").strip()
        
        if not codigo:
            messagebox.showwarning("Advertencia", "No hay código preprocesado para compilar")
            return
        
        try:
            # Importar módulos del compilador
            from compiler.syntax_analizer import parse
            from compiler.semantic_analyzer import SemanticAnalyzer
            from compiler.code_generator import generate_code
            
            # 1. Análisis sintáctico (parsing)
            ast = parse(codigo)
            if not ast:
                msg = "Error de Sintaxis: No se pudo parsear el código\nRevise la salida del analizador sintáctico para más detalles."
                self.set_salida(msg)
                messagebox.showerror("Error de Sintaxis", "No se pudo parsear el código")
                return
            
            # 2. Análisis semántico
            analyzer = SemanticAnalyzer()
            success = analyzer.analyze(ast)
            
            # Mostrar errores semánticos si existen
            if analyzer.errors:
                errores_msg = "\n".join(analyzer.errors[:10])
                if len(analyzer.errors) > 10:
                    errores_msg += f"\n... y {len(analyzer.errors)-10} errores más"
                
                self.set_salida(f"Errores Semánticos:\n{errores_msg}")
                
                messagebox.showwarning(
                    f"Advertencias Semánticas ({len(analyzer.errors)})",
                    errores_msg
                )
            
            # 3. Generación de código Assembly
            assembly_code = generate_code(ast, analyzer.symbol_table)
            
            if not assembly_code:
                messagebox.showerror("Error", "No se pudo generar código Assembly")
                return
            
            # Insertar código Assembly en el área correspondiente
            self.texto_asm.delete("1.0", "end")
            self.texto_asm.insert("1.0", assembly_code)
            
            # DEBUG: Guardar código ensamblador generado
            with open("debug_output.asm", "w", encoding="utf-8") as f:
                f.write(assembly_code)
            
            self.set_log(f"✓ Compilación exitosa ({len(assembly_code)} caracteres de Assembly generados). \n Haga clic en 'Ensamblar' para ensamblar el programa.")
            
        except Exception as e:
            messagebox.showerror("Error de Compilación", f"Error al compilar:\n{str(e)}")
            import traceback
            print(traceback.format_exc())

    def ensamblar(self):
        texto = self.texto_asm.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Advertencia", "No hay código para cargar")
            return
        
        try:
            # Detectar si el texto es código binario hexadecimal
            #es_binario = self._es_codigo_binario(texto)
            
            # if es_binario:
            #     # Cargar código binario directamente
            #     self.programa_actual = self._parsear_codigo_binario(texto)
            #     tipo_carga = "binario"
            #     print("Cargando binario")
            # else:
                # Ensamblar el código assembly
            self.programa_actual = self.assembler.assemble(texto)
            tipo_carga = "assembly"

            #traduccion = ""
            #traduccion = f"Código {'binario cargado' if es_binario else 'ensamblado'}:\n\n"
            #for i, instr in enumerate(self.programa_actual):
            #    addr = i * 8 #+ start
            #    desasm = self.assembler.disassemble_instruction(instr)
            #    traduccion += f"{addr:04x}: {instr:016x}\n      {desasm}\n\n"   

            self.texto_relo.delete("1.0", "end")
            self.texto_relo.insert("1.0", self.programa_actual.codigo)
            self.set_log(f"✓ Ensamblado exitoso. \nAsigne una direccion de carga y haga clic en 'Enlazar y cargar' para enlazar el programa y cargarlo en la memoria RAM.")

            #self.set_salida(f"Programa cargado exitosamente desde {tipo_carga}. ¡Haz clic en 'Ejecutar'!")

        except Exception as e:
            messagebox.showerror("Error", f"Error al ensamblar programa:\n{str(e)}")
            import traceback
            print(traceback.format_exc())

    def enlazar_y_cargar(self):
        """enlazar_y_cargar el programa desde el área de codigo relocalizable a la memoria RAM"""
        texto = self.texto_relo.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("Advertencia", "No hay código para cargar")
            return
        
        try:

            ###Linkear
            if self.relocatables:
                self.linker.relocatables = [self.programa_actual] + self.relocatables

                self.programa_actual = self.linker.get_liked_code()

                self.texto_relo.delete("1.0", "end")
                self.texto_relo.insert("1.0", self.programa_actual.codigo)

            if self.programa_actual.extern_labels:
                raise Exception(f"Hay referencias sin resolver: {self.programa_actual.extern_labels}")
            ### Load
            start = self.obtener_direccion_carga()

            # Cargar programa en RAM
            program_info = self.loader.load_in_memory(self.programa_actual.codigo,start)

            # Poner PC apuntando a inicio de programa
            self.cpu.set_pc(start)
            self.cpu.set_sp(self.cpu.memory.size//2)

            #Limpiar salida
            self.machine_out.buffer = ""
            self.update_gui()
            self.set_log(f"✓ Programa cargado en memoria! Puedes ejecutar el programa")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar programa:\n{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _es_codigo_binario(self, texto):
        """Detecta si el texto contiene código binario en formato hexadecimal"""
        lineas = [l.strip() for l in texto.split('\n') if l.strip()]
        
        # Si todas las líneas son números hexadecimales de 16 dígitos, es binario
        for linea in lineas:
            # Ignorar comentarios y líneas vacías
            if linea.startswith(';') or linea.startswith('#'):
                continue
            
            # Extraer la parte hexadecimal
            if ':' in linea:
                # Formato "0000: 006110000000000a"
                partes = linea.split(':')
                if len(partes) >= 2:
                    partes_hex = partes[1].strip().split()
                    if partes_hex:
                        linea_limpia = partes_hex[0]
                    else:
                        return False  # No hay contenido después del ':'
                else:
                    return False
            else:
                # Remover prefijos comunes
                partes_sin_prefijo = linea.replace('0x', '').strip().split()
                if partes_sin_prefijo:
                    linea_limpia = partes_sin_prefijo[0]
                else:
                    return False
            
            # Verificar si es hexadecimal válido de 16 caracteres
            if len(linea_limpia) == 16 and all(c in '0123456789ABCDEFabcdef' for c in linea_limpia):
                continue
            elif linea.strip():  # Si hay contenido no hexadecimal, no es binario
                return False
        
        return len(lineas) > 0
    
    def _parsear_codigo_binario(self, texto):
        """Convierte código binario hexadecimal a lista de instrucciones"""
        instrucciones = []
        lineas = texto.split('\n')
        
        for linea in lineas:
            linea = linea.strip()
            
            # Ignorar líneas vacías y comentarios
            if not linea or linea.startswith(';') or linea.startswith('#'):
                continue
            
            # Extraer el código hexadecimal (puede tener formato "0x..." o "addr: code")
            if ':' in linea:
                # Formato "0000: 006110000000000a"
                partes = linea.split(':')
                hex_code = partes[1].strip().split()[0]
            else:
                # Formato directo "006110000000000a" o "0x006110000000000a"
                hex_code = linea.replace('0x', '').strip().split()[0]
            
            # Convertir a entero
            try:
                instruccion = int(hex_code, 16)
                instrucciones.append(instruccion)
            except ValueError:
                raise ValueError(f"Código hexadecimal inválido: {hex_code}")
        
        return instrucciones

    def ejecutar_programa_completo(self):
        """Ejecuta el programa completo"""
        try: 
            # Modo completo: ejecutar todo hasta el final de una vez
            # Problema el polling del input, con hilo se soluciona
            # Si ponemos a hacer un ciclo infinito esperando por input se bloquea el hilo de la GUI :((
            self.set_log("Ejecutando programa completo hasta el final...\n")
            self.finished = False
            cpu_thread = threading.Thread(target=self._run_cpu)
            cpu_thread.daemon = True
            cpu_thread.start()

            # Este metodo checkea cada 20ms si la cpu ya termino para actulizar GUI. 
            self.check_cpu()
             

        except Exception as e:
            messagebox.showerror("Error", f"Error durante la ejecución:\n{str(e)}")
            self.set_log(f"\nError: {str(e)}")

    def _run_cpu(self):
        self.cpu.run()
        self.finished = True

    def ejecutar_programa_detallado(self):
        """Ejecuta el programa completo"""
        if not self.programa_actual:
            messagebox.showwarning("Advertencia", "Primero carga un programa")
            return
        
        # Modo detallado: ejecutar con pausas para ver el flujo y cambios
        self.set_log("Ejecutando programa en modo detallado (paso a paso)...\n")
        self.ejecutando_paso_automatico = True
        #self.boton_parar.config(state="normal")
        self.ejecutar_modo_paso_automatico()
            
        try: pass
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la ejecución:\n{str(e)}")
            self.append_salida(f"\nError: {str(e)}")            

    def ejecutar_modo_paso_automatico(self):
        """Ejecuta el programa paso a paso con pausas automáticas"""
        if not self.ejecutando_paso_automatico or not self.cpu.running:
        #if not self.cpu.running:
            self.append_salida(f"Programa terminado, con ejectutando paso automatico {self.ejecutando_paso_automatico}, y cpu.running {self.cpu.running}")
            self.ejecutando_paso_automatico = False
            #self.boton_parar.config(state="disabled")
            self.update_gui()  # Actualizar una última vez al terminar
            return
        
        try:
            # Ejecutar una instrucción
            self.cpu.fetch()
            ins = self.cpu.decode()
            self.cpu.execute(ins)
            
            # Actualizar la interfaz gráfica después de cada instrucción
            self.update_gui()
            
            # Mostrar qué instrucción se ejecutó
            instr_info = self.assembler.disassemble_instruction(self.cpu.ir)
            self.append_salida(f"Ejecutado: {instr_info}")
            
            # Si el programa sigue corriendo y no se ha pausado, programar la siguiente instrucción
            if self.cpu.running and self.ejecutando_paso_automatico:
                # Pausa de 1 segundo y continúa automáticamente
                self.root.after(1000, self.ejecutar_modo_paso_automatico)
            else:
                self.append_salida(pformat(self.cpu.io.devices, indent=4, width=40, sort_dicts=False))

                self.append_salida("Programa terminado")
                self.ejecutando_paso_automatico = False
                #self.boton_parar.config(state="disabled")
                self.update_gui()  # Actualizar al terminar
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar paso:\n{str(e)}")
            self.append_salida(f"Error: {str(e)}")
            self.ejecutando_paso_automatico = False
            #self.boton_parar.config(state="disabled")
            self.update_gui()  # Actualizar en caso de error

    def parar_ejecucion(self):
        """Para la ejecución paso a paso automática"""
        self.ejecutando_paso_automatico = False
        #self.boton_parar.config(state="disabled")
        self.append_salida("Ejecución pausada")

    def mostrar_info_cargador(self):
        """Muestra información del cargador en una ventana separada"""
        # Crear ventana de información
        info_window = tk.Toplevel(self.root)
        info_window.title("Información del Cargador")
        info_window.geometry("600x500")
        
        # Área de texto con scroll
        text_frame = ttk.Frame(info_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_text = tk.Text(text_frame, font=("Consolas", 10))
        info_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=info_text.yview)
        scrollbar.pack(side="right", fill="y")
        info_text.config(yscrollcommand=scrollbar.set)
        
        # Obtener información del cargador
        try:
            memory_map = self.loader.get_memory_map()
            loaded_programs = self.loader.list_loaded_programs()
            
            info_content = "=== INFORMACIÓN DEL CARGADOR ===\n\n"
            info_content += f"Memoria Total: {memory_map['total_memory']} bytes\n"
            info_content += f"Memoria Usada: {memory_map['used_memory']} bytes\n"
            info_content += f"Memoria Libre: {memory_map['free_memory']} bytes\n"
            info_content += f"Utilización: {(memory_map['used_memory']/memory_map['total_memory']*100):.1f}%\n\n"
            
            info_content += "=== PROGRAMAS CARGADOS ===\n\n"
            if loaded_programs:
                for name, info in loaded_programs.items():
                    info_content += f"Programa: {name}\n"
                    info_content += f"  Dirección inicio: 0x{info['start_address']:04x}\n"
                    info_content += f"  Dirección fin:    0x{info['end_address']:04x}\n"
                    info_content += f"  Tamaño:          {info['size']} bytes\n"
                    info_content += f"  Instrucciones:   {info['instructions_count']}\n\n"
            else:
                info_content += "No hay programas cargados actualmente.\n\n"
            
            info_content += "=== MAPA DE MEMORIA ===\n\n"
            for name, region in memory_map['programs'].items():
                info_content += f"{name}: {region['start']} - {region['end']} ({region['size']} bytes)\n"
            
            info_text.insert("1.0", info_content)
            info_text.config(state="disabled")
            
        except Exception as e:
            info_text.insert("1.0", f"Error al obtener información del cargador:\n{str(e)}")
            info_text.config(state="disabled")
        
        # Botón para cerrar
        ttk.Button(info_window, text="Cerrar", command=info_window.destroy).pack(pady=10)

    def ejecutar_paso(self):
        """Ejecuta una sola instrucción"""
        if not self.programa_actual:
            messagebox.showwarning("Advertencia", "Primero carga un programa")
            return
        
        if not self.cpu.running:
            self.append_salida(pformat(self.cpu.io.devices, indent=4, width=40, sort_dicts=False))
            messagebox.showinfo("Info", "El programa ya terminó")
            return
        
        # Ejecutar una sola instrucción
        self.cpu.fetch()
        ins = self.cpu.decode()
        self.cpu.execute(ins)
        self.update_gui()
        
        # Mostrar información de la instrucción ejecutada
        instr_info = self.assembler.disassemble_instruction(self.cpu.ir)
        self.append_salida(f"Ejecutado: {instr_info}")
        try:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar paso:\n{str(e)}")
            self.append_salida(f"Error: {str(e)}")

    def reset_cpu(self):
        """Reinicia el estado del CPU"""
        # Parar cualquier ejecución paso a paso en curso
        self.ejecutando_paso_automatico = False
        #self.boton_parar.config(state="disabled")
        
        # Reiniciar componentes - preservar memoria e I/O
        memory = self.cpu.memory
        io_system = self.cpu.io
        self.cpu = CPU(memory, io_system)
        
        # Reiniciar PC a 0 y estado de ejecución
        self.cpu.pc = 0
        self.cpu.running = True
        
        # Limpiar buffers de I/O
        self.machine_out.buffer = ""
        self.machine_in.buffer = []
        
        ##self.disco = Disco()  # También reiniciar el disco
        self.programa_actual = []  # Limpiar programa actual
        
        self.linker.relocatables = []
        self.relocatables = []
        # Limpiar interfaz
        self.clear_all_text()
        self.update_gui()
        self.set_salida("CPU reiniciado. ¡Carga un nuevo programa!")

    def leer_memoria(self, direccion):
        """Lee una celda de memoria del disco"""
        return self.disco.leer(f"M{direccion}")

    def escribir_memoria(self, direccion, valor):
        """Escribe una celda de memoria en el disco"""
        # Convertir valor entero a binario de 64 bits
        valor_bin = format(valor & ((1 << 64) - 1), '064b')
        self.disco.escribir(f"M{direccion}", valor_bin)

    def leer_registro_disco(self, reg_num):
        """Lee un registro del disco (registros de 4 bits del disco)"""
        return self.disco.leer(f"R{reg_num:02d}")

    def escribir_registro_disco(self, reg_num, valor):
        """Escribe un registro en el disco (registros de 4 bits del disco)"""
        valor_bin = format(valor & 0xF, '04b')
        self.disco.escribir(f"R{reg_num:02d}", valor_bin)

    def set_flag(self, flag, valor):
        """Asignar valor a una bandera"""
        if flag in self.flags:
            self.flags[flag].config(text=str(valor))

    def set_pointer(self, pointer, valor):
        """Asignar valor a una apuntador especial de CPU"""
        if pointer in self.punteros:
            self.punteros[pointer].config(text=str(valor))

    def set_registro(self, reg, valor):
        """Asignar valor a un registro"""
        if reg in self.registros:
            self.registros[reg].config(text=str(valor))

    def set_log(self, texto):
        self.texto_log.delete("1.0", "end")
        self.texto_log.insert("1.0", texto)

    def set_salida(self, texto):
        """Actualizar el contenido del frame de salida"""
        self.texto_salida.delete("1.0", "end")
        self.texto_salida.insert("1.0", texto)

    def append_salida(self, texto):
        """Añadir texto al contenido del frame de salida"""
        self.texto_salida.insert("end", "\n" + texto)
        self.texto_salida.see("end")            

    def update_resgitros(self):
        for i,value in enumerate(self.CPU.registers):
            self.set_registro(f"R{i:02}",value)     

    def update_flags(self):
        for key, value in self.CPU.flags.items():
            self.set_flag(key,value)
        
        #PC
        self.set_flag("PC",self.CPU.pc)

    def limpiar_campos_gui(self):
        """Limpia todos los campos de texto de la GUI excepto la RAM"""
        # Parar ejecución paso a paso si está corriendo
        self.ejecutando_paso_automatico = False
        
        # Limpiar campos de texto
        self.texto_alto.delete("1.0", "end")
        self.texto_preprocesado.delete("1.0", "end")
        self.texto_asm.delete("1.0", "end")
        self.texto_relo.delete("1.0", "end")
        self.texto_salida.delete("1.0", "end")
        self.texto_log.delete("1.0", "end")
        
        # Limpiar entrada
        self.entrada_maquina.delete(0, 'end')
        
        # Limpiar buffer de salida de la máquina
        self.machine_out.buffer = ""
        
        # Resetear programa actual
        self.programa_actual = []
        
        self.set_log("Campos de GUI limpiados. La RAM y el estado del CPU se mantienen.")

    def clear_all_text(self):
        """Limpia todos los campos de texto de la GUI incluyendo la RAM"""
        self.texto_alto.delete("1.0", "end")
        self.texto_preprocesado.delete("1.0", "end")
        self.texto_asm.delete("1.0", "end")
        self.texto_relo.delete("1.0", "end")
        self.texto_salida.delete("1.0", "end")
        self.texto_log.delete("1.0", "end")
        self.entrada_maquina.delete(0, 'end')
        self.limpiar_ram()
 
    def leer_memoria_gui(self):
        """Lee memoria según dirección, tamaño, formato y signo seleccionados en el GUI"""
        try:
            addr_str = self.mem_address.get().strip()
            if not addr_str:
                messagebox.showwarning("Advertencia", "Ingrese una dirección de memoria")
                return

            # Dirección en hexadecimal
            direccion = int(addr_str, 10)

            # Tamaño (1, 2, 4, 8 bytes)
            size = int(self.mem_size.get())

            # Interpretación con signo o sin signo
            signed = (self.mem_signed.get() == "signed")

            # Leer valor desde la memoria
            valor = self.cpu.memory.read(direccion, size, signed=signed)

            # Mostrar en formato elegido
            if self.mem_format.get() == "hex":
                # Se enmascara al tamaño leído para mostrar valor "crudo"
                mask = (1 << (size * 8)) - 1
                texto = f"0x{valor & mask:0{size*2}X}"
            else:
                texto = str(valor)

            self.mem_valor.config(text=texto)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer memoria:\n{str(e)}")

    
    def update_gui(self):
        # Actualizar registros
        for i in range(16):
            self.set_registro(f"R{i:02}", self.cpu.registers[i].value)
        
        # Actualizar flags
        self.set_flag("Z (Zero)", self.cpu.flags["Z"])
        self.set_flag("N (Negative)", self.cpu.flags["N"])
        self.set_flag("C (Carry)", self.cpu.flags["C"])
        self.set_flag("V (Overflow)", self.cpu.flags["V"])

        self.set_pointer("PC (Program Counter)",self.cpu.pc)
        self.set_pointer("SP (Stack Pointer)",self.cpu.sp.value)
        # Mostrar BP usando el registro R14 (convención del proyecto)
        try:
            bp_val = self.cpu.registers[14].value
        except Exception:
            bp_val = 0
        self.set_pointer("BP (Base Pointer)", bp_val)
        
        # Actualizar visor de RAM
        self.refrescar_visor_ram()

        # Actualizar Salida maquina
        self.set_salida(self.machine_out.buffer)

    def mainloop(self):
        self.root.mainloop()

    # ========== Visor de RAM (tabla dinámica) ==========
    def abrir_visor_ram(self, parent):
        """Crea un visor RAM incrustado en la columna 4"""
        
        # Si ya existe, no lo vuelvas a crear
        if hasattr(self, "ram_frame") and self.ram_frame:
            return  

        # Frame que contiene todo
        self.ram_frame = ttk.Frame(parent)
        self.ram_frame.pack(fill="both", expand=True)

        # ------------------------
        # Controles superiores
        # ------------------------
        top_controls = ttk.Frame(self.ram_frame)
        top_controls.pack(fill="x", padx=4, pady=(4,4))

        self.ram_auto = tk.BooleanVar(value=False)
        self.ram_interval = tk.IntVar(value=1000)

        ttk.Checkbutton(
            top_controls,
            text="Auto",
            variable=self.ram_auto,
            command=self._programar_auto_refresco_ram
        ).pack(side="left")

        ttk.Label(top_controls, text="ms:").pack(side="left", padx=4)
        ttk.Entry(top_controls, textvariable=self.ram_interval, width=6).pack(side="left")

        ttk.Button(
            top_controls,
            text="Refrescar",
            command=self.refrescar_visor_ram
        ).pack(side="left", padx=4)

        ttk.Button(top_controls, text="Limpiar RAM", command=self.limpiar_ram).pack(side="left", padx=4)
        
        # Campo de búsqueda
        ttk.Label(top_controls, text="Ir a:").pack(side="left", padx=(10, 2))
        self.ram_search_addr = tk.StringVar(value="0x0000")
        search_entry = ttk.Entry(top_controls, textvariable=self.ram_search_addr, width=12)
        search_entry.pack(side="left")
        search_entry.bind('<Return>', lambda e: self._ir_a_direccion_ram())
        ttk.Button(top_controls, text="🔍", command=self._ir_a_direccion_ram, width=3).pack(side="left", padx=2)

        # ------------------------
        # Tabla Treeview
        # ------------------------
        table_frame = ttk.Frame(self.ram_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ["Addr", "B0","B1","B2","B3","B4","B5","B6","B7"]
        self.ram_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.ram_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.ram_tree.xview)
        self.ram_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.ram_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Encabezados
        self.ram_tree.heading("Addr", text="Addr")
        self.ram_tree.column("Addr", width=70, anchor="center")

        for bx in columns[1:]:
            self.ram_tree.heading(bx, text=bx)
            self.ram_tree.column(bx, width=40, anchor="center")

        # Poblar inicialmente
        self._poblar_visor_ram_inicial()


    def _poblar_visor_ram_inicial(self):
        # Borrar existente
        for iid in self.ram_tree.get_children():
            self.ram_tree.delete(iid)

        mem_len = len(self.cpu.memory)
        getb = self.cpu.memory.get_bytes
        for addr in range(0, mem_len, 8):
            chunk = getb(addr, min(8, mem_len - addr))
            if len(chunk) < 8:
                chunk = bytes(chunk) + bytes(8 - len(chunk))
            vals = [f"0x{addr:04X}"] + [f"{b:02X}" for b in chunk]
            iid = f"{addr}"
            self.ram_tree.insert("", "end", iid=iid, values=vals)

    def refrescar_visor_ram(self):
        # Actualizar valores por fila para minimizar parpadeos
        mem_len = len(self.cpu.memory)
        getb = self.cpu.memory.get_bytes
        expected_rows = (mem_len + 7) // 8
        current_rows = len(self.ram_tree.get_children(""))

        if current_rows != expected_rows:
            # Si cambia la cantidad, repoblar
            self._poblar_visor_ram_inicial()
            return

        for addr in range(0, mem_len, 8):
            chunk = getb(addr, min(8, mem_len - addr))
            if len(chunk) < 8:
                chunk = bytes(chunk) + bytes(8 - len(chunk))
            vals = [f"0x{addr:04X}"] + [f"{b:02X}" for b in chunk]
            iid = f"{addr}"
            if self.ram_tree.exists(iid):
                self.ram_tree.item(iid, values=vals)
            else:
                self.ram_tree.insert("", "end", iid=iid, values=vals)

    def _programar_auto_refresco_ram(self):
        # Cancelar programación previa
        if hasattr(self, 'ram_after_id') and self.ram_after_id:
            try:
                self.ram_window.after_cancel(self.ram_after_id)
            except Exception:
                pass
            self.ram_after_id = None

        if hasattr(self, 'ram_window') and self.ram_window and tk.Toplevel.winfo_exists(self.ram_window) and self.ram_auto.get():
            interval = max(200, int(self.ram_interval.get() or 1000))
            def _tick():
                if self.ram_window and tk.Toplevel.winfo_exists(self.ram_window):
                    self.refrescar_visor_ram()
                    self._programar_auto_refresco_ram()
            self.ram_after_id = self.ram_window.after(interval, _tick)

    def _ir_a_direccion_ram(self):
        """Desplaza el visor de RAM a una dirección específica."""
        try:
            addr_str = self.ram_search_addr.get().strip()
            # Soportar formato hex (0x1234) o decimal (1234)
            if addr_str.startswith('0x') or addr_str.startswith('0X'):
                addr = int(addr_str, 16)
            else:
                addr = int(addr_str)
            
            # Alinear a múltiplo de 8 (cada fila representa 8 bytes)
            addr = (addr // 8) * 8
            
            # Verificar que la dirección esté en rango
            if 0 <= addr < len(self.cpu.memory):
                iid = f"{addr}"
                if self.ram_tree.exists(iid):
                    # Hacer visible y seleccionar la fila
                    self.ram_tree.see(iid)
                    self.ram_tree.selection_set(iid)
                    self.ram_tree.focus(iid)
                else:
                    # Buscar la dirección más cercana
                    all_items = self.ram_tree.get_children()
                    if all_items:
                        # Encontrar el item más cercano
                        closest_iid = None
                        min_diff = float('inf')
                        for item_iid in all_items:
                            item_addr = int(item_iid)
                            diff = abs(item_addr - addr)
                            if diff < min_diff:
                                min_diff = diff
                                closest_iid = item_iid
                        
                        if closest_iid:
                            self.ram_tree.see(closest_iid)
                            self.ram_tree.selection_set(closest_iid)
                            self.ram_tree.focus(closest_iid)
            else:
                messagebox.showerror("Dirección inválida", f"La dirección debe estar entre 0x0000 y 0x{len(self.cpu.memory)-1:04X}")
        except ValueError:
            messagebox.showerror("Formato inválido", "Ingrese una dirección válida en formato hexadecimal (0x1234) o decimal (1234)")
    
    def _cerrar_visor_ram(self):
        if hasattr(self, 'ram_after_id') and self.ram_after_id:
            try:
                self.ram_window.after_cancel(self.ram_after_id)
            except Exception:
                pass
            self.ram_after_id = None
        if hasattr(self, 'ram_window') and self.ram_window:
            try:
                self.ram_window.destroy()
            except Exception:
                pass
            self.ram_window = None

    # ========== Acciones RAM ==========
    def limpiar_ram(self):
        """Limpia completamente la RAM (pone todos los bytes en 0) con confirmación."""
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres limpiar TODA la RAM? Esta acción no se puede deshacer."):
            return
        try:
            self.cpu.memory.clear()
            # Persistir inmediatamente si existe archivo configurado
            if hasattr(self.cpu.memory, 'save_to_txt') and hasattr(self.cpu.memory, 'memory_file'):
                self.cpu.memory.save_to_txt(self.cpu.memory.memory_file)
            
            # Refrescar el visor de RAM si está abierto - ejecutar el código del botón refrescar
            if hasattr(self, 'ram_tree'):
                try:
                    self.refrescar_visor_ram()
                except Exception:
                    pass  # Si falla, ignorar
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar la RAM:\n{str(e)}")

    # ======================================================================

    def run(self):
        self.root.mainloop()

    def procesar_entrada_maquina(self,event):
        texto = self.entrada_maquina.get()
        for chr in texto:
            self.machine_in.write(ord(chr))
        self.machine_in.write(0) ## NULL for finish
        self.entrada_maquina.delete(0,'end')

    def check_cpu(self):
        if self.finished:
            self.update_gui()
            self.set_log("Programa acabado")
            return

        # volver a revisarlo en 20 ms
        self.root.after(20, self.check_cpu)

    def _abrir_ventana_analizador_lexico(self):

        texto_preprocesado = self.texto_preprocesado.get("1.0", "end").strip()

        if not texto_preprocesado:
            messagebox.showwarning("Advertencia", "No hay un codigo preprocesado para analizar")
            return

        # Si ya existe, traer al frente
        if hasattr(self, 'lex_window') and self.lex_window and tk.Toplevel.winfo_exists(self.lex_window):
            self.lex_window.deiconify()
            self.lex_window.lift()
            return

        self.lex_window = tk.Toplevel(self.root)
        self.lex_window.title("Ventana LEX")

        frame = ttk.Frame(self.lex_window)
        frame.pack(fill="both", expand=True)

        self.texto_lex = tk.Text(frame, wrap="none")
        self.texto_lex.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.texto_lex.yview)
        sy.pack(side="right", fill="y")
        self.texto_lex.configure(yscrollcommand=sy.set)

        codigo_lex = self.analizador_lexico(texto_preprocesado)

        self.texto_lex.insert("1.0", codigo_lex)

    def _abrir_ventana_analizador_sintactico(self):

        texto_preprocesado = self.texto_preprocesado.get("1.0", "end").strip()

        if not texto_preprocesado:
            messagebox.showwarning("Advertencia", "No hay un codigo preprocesado para analizar")
            return

        if hasattr(self, 'syntax_window') and self.syntax_window and tk.Toplevel.winfo_exists(self.syntax_window):
            self.syntax_window.deiconify()
            self.syntax_window.lift()
            return

        self.syntax_window = tk.Toplevel(self.root)
        self.syntax_window.title("Ventana Analizador Sintactico")

        frame = ttk.Frame(self.syntax_window)
        frame.pack(fill="both", expand=True)

        self.texto_syntax = tk.Text(frame, wrap="none")
        self.texto_syntax.pack(side="left", fill="both", expand=True)

        sy = ttk.Scrollbar(frame, orient="vertical", command=self.texto_syntax.yview)
        sy.pack(side="right", fill="y")
        self.texto_syntax.configure(yscrollcommand=sy.set)

        ast = syntax_parse(texto_preprocesado, debug=False)

        # Capturar la salida de print_ast en un buffer

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            print_ast(ast)

        codigo_syntax = buffer.getvalue()

        print("Libera el buffer")

        self.texto_syntax.insert("1.0", codigo_syntax)

    def load_relos(self):
        # Abrir diálogo para seleccionar archivo
        from tkinter import filedialog
        import os
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivo relocalizables",
            filetypes=[
                ("Archivos relocalizables", "*.relo"),
            ],
            initialdir=os.path.join(os.path.dirname(__file__), "../../lib")
        )

        if archivos:
            self.relocatables = []
            for archivo in archivos:
                self.relocatables.append(CodigoRelo.load_relo(archivo))

            archivos_names = [os.path.basename(f) for f in archivos]
            self.set_log(f"{archivos_names}\nHan sido agregados para linker")



    def save_archivo_relo(self):
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
                title="Guardar archivo .relo",
                defaultextension=".relo",
                filetypes=[("Archivo Relocatable", "*.relo"), ("Todos los archivos", "*.*")]
            )
        if filename:
            texto = self.texto_asm.get("1.0", "end").strip()
            relo = self.assembler.assemble(texto)
            relo.save_to_file(filename)
            
