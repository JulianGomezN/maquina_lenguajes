import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os
from pprint import pformat

# Añadir el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.CPU import CPU
#from disco_64bits import Disco
from compiler.assembler import Assembler
from logic.Loader import Loader


class SimuladorGUI:

    def __init__(self , CPU:CPU):
        self.root = tk.Tk()
        self.root.title("Simulador - Atlas")
        
        # Configurar pantalla completa
        self.root.state('zoomed')  # Para Windows - maximiza la ventana
        
        # Permitir salir de pantalla completa con ESC
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Inicializar componentes del simulador
        self.cpu = CPU
        self.assembler = Assembler()
        self.loader = Loader(self.cpu.memory)
        self.programa_actual = []

        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ================ COLUMNA IZQUIERDA: PROGRAMA ================
        left_frame = ttk.LabelFrame(main_frame, text="Programa Assembly")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Área de texto
        text_frame = ttk.Frame(left_frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.texto_programa = tk.Text(text_frame, height=25, width=50, font=("Consolas", 10))
        self.texto_programa.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.texto_programa.yview)
        scrollbar.pack(side="right", fill="y")
        self.texto_programa.config(yscrollcommand=scrollbar.set)
        
        # Marco principal para botones
        buttons_container = ttk.LabelFrame(left_frame, text="Controles", padding=10)
        buttons_container.pack(fill="x", padx=5, pady=5)
        
        # Configurar grid para botones organizados
        buttons_container.grid_columnconfigure(0, weight=1)
        buttons_container.grid_columnconfigure(1, weight=1)
        buttons_container.grid_columnconfigure(2, weight=1)
        
        # FILA 1: Operaciones principales
        ttk.Label(buttons_container, text="📝 Programa:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        ttk.Button(buttons_container, text="🔄 Cargar Programa", 
                  command=self.cargar_programa, width=20).grid(row=1, column=0, padx=3, pady=2, sticky="ew")
        
        ttk.Label(buttons_container, text="▶️ Ejecución:", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5))
        ttk.Button(buttons_container, text="🚀 Ejecutar", 
                  command=self.ejecutar_programa, width=20).grid(row=1, column=1, padx=3, pady=2, sticky="ew")
        
        ttk.Label(buttons_container, text="🎯 Control:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w", pady=(0, 5))
        ttk.Button(buttons_container, text="👆 Paso Manual", 
                  command=self.ejecutar_paso, width=20).grid(row=1, column=2, padx=3, pady=2, sticky="ew")
        
        # FILA 2: Dirección de carga
        ttk.Label(buttons_container, text="📍 Dirección de carga:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 2))
        
        # Frame para dirección de carga
        direccion_frame = ttk.Frame(buttons_container)
        direccion_frame.grid(row=3, column=0, columnspan=3, padx=3, pady=2, sticky="ew")
        
        ttk.Label(direccion_frame, text="Cargar programa en dirección:").pack(side="left")
        self.entrada_direccion = ttk.Entry(direccion_frame, width=10)
        self.entrada_direccion.pack(side="left", padx=(5, 5))
        self.entrada_direccion.insert(0, "0")  # Valor por defecto
        
        # Botones de dirección rápida
        ttk.Button(direccion_frame, text="Euclides (2500)", 
                  command=lambda: self.entrada_direccion.delete(0, 'end') or self.entrada_direccion.insert(0, "2500")).pack(side="left", padx=2)
        ttk.Button(direccion_frame, text="Matrices (3700)", 
                  command=lambda: self.entrada_direccion.delete(0, 'end') or self.entrada_direccion.insert(0, "3700")).pack(side="left", padx=2)
        ttk.Button(direccion_frame, text="Origen (0)", 
                  command=lambda: self.entrada_direccion.delete(0, 'end') or self.entrada_direccion.insert(0, "0")).pack(side="left", padx=2)
        
        # FILA 4: Controles de estado
        self.boton_parar = ttk.Button(buttons_container, text="⏹️ Parar", 
                                     command=self.parar_ejecucion, state="disabled", width=20)
        self.boton_parar.grid(row=4, column=0, padx=3, pady=2, sticky="ew")
        
        ttk.Button(buttons_container, text="🔄 Reset CPU", 
                  command=self.reset_cpu, width=20).grid(row=4, column=1, padx=3, pady=2, sticky="ew")
        
        ttk.Button(buttons_container, text="📊 Info Cargador", 
                  command=self.mostrar_info_cargador, width=20).grid(row=4, column=2, padx=3, pady=2, sticky="ew")

        # ================ COLUMNA CENTRO: TRADUCCIÓN ================
        center_frame = ttk.LabelFrame(main_frame, text="Traducción Binaria")
        center_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.label_traduccion = tk.Text(center_frame, height=25, width=40, font=("Consolas", 9))
        self.label_traduccion.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ================ COLUMNA DERECHA: ESTADO CPU ================
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        
        # Registros
        reg_frame = ttk.LabelFrame(right_frame, text="Registros")
        reg_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Crear registros en grid
        self.registros = {}
        for i in range(16):
            row = i // 4
            col = i % 4
            
            frame = ttk.Frame(reg_frame)
            frame.grid(row=row, column=col, padx=2, pady=1, sticky="w")
            
            reg_name = f"R{i:02}"
            ttk.Label(frame, text=reg_name, width=4).pack(side="left")
            
            valor = ttk.Label(frame, text="0", width=10, relief="solid", anchor="center")
            valor.pack(side="left")
            
            self.registros[reg_name] = valor
        
        # Flags
        flags_frame = ttk.LabelFrame(right_frame, text="Flags y PC")
        flags_frame.pack(fill="x", pady=5)
        
        self.flags = {}
        flag_names = ["Z (Zero)", "N (Negative)", "C (Carry)", "V (Overflow)", "PC (Program Counter)"]
        
        for i, flag in enumerate(flag_names):
            frame = ttk.Frame(flags_frame)
            frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(frame, text=flag, width=20).pack(side="left")
            valor = ttk.Label(frame, text="0", width=8, relief="solid", anchor="center")
            valor.pack(side="right")
            
            self.flags[flag] = valor
        
                # ================ MEMORIA ================
        mem_frame = ttk.LabelFrame(right_frame, text="Examinador de Memoria")
        mem_frame.pack(fill="x", pady=5)

        # Dirección de memoria
        ttk.Label(mem_frame, text="Dirección (dec):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mem_address = ttk.Entry(mem_frame, width=10)
        self.mem_address.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Tamaño de lectura
        ttk.Label(mem_frame, text="Tamaño:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mem_size = tk.StringVar(value="1")
        size_combo = ttk.Combobox(mem_frame, textvariable=self.mem_size, 
                                  values=["1", "2", "4", "8"], width=5, state="readonly")
        size_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Formato de salida (hex/dec)
        ttk.Label(mem_frame, text="Formato:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.mem_format = tk.StringVar(value="hex")
        ttk.Radiobutton(mem_frame, text="Hex", variable=self.mem_format, value="hex").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(mem_frame, text="Dec", variable=self.mem_format, value="dec").grid(row=2, column=2, sticky="w")

        # Signo
        ttk.Label(mem_frame, text="Interpretación:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.mem_signed = tk.StringVar(value="unsigned")
        ttk.Radiobutton(mem_frame, text="Sin signo", variable=self.mem_signed, value="unsigned").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(mem_frame, text="Con signo", variable=self.mem_signed, value="signed").grid(row=3, column=2, sticky="w")

        # Botón leer
        ttk.Button(mem_frame, text="Leer", command=self.leer_memoria_gui).grid(row=0, column=3, rowspan=4, padx=5, pady=2, sticky="ns")

        # Resultado
        ttk.Label(mem_frame, text="Valor:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.mem_valor = ttk.Label(mem_frame, text="--", width=25, relief="solid", anchor="center")
        self.mem_valor.grid(row=4, column=1, columnspan=3, padx=5, pady=2, sticky="ew")

        # Modo de ejecución
        mode_frame = ttk.LabelFrame(right_frame, text="Modo de Ejecución")
        mode_frame.pack(fill="x", pady=5)
        
        self.modo = tk.StringVar(value="automatico")
        ttk.Radiobutton(mode_frame, text="Automático", variable=self.modo, value="automatico").pack(anchor="w", padx=5)
        ttk.Radiobutton(mode_frame, text="Paso a paso", variable=self.modo, value="paso").pack(anchor="w", padx=5)
        
        # Salida
        output_frame = ttk.LabelFrame(right_frame, text="Salida")
        output_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.texto_salida = tk.Text(output_frame, height=10, width=40, font=("Consolas", 9))
        self.texto_salida.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Variable para controlar ejecución paso a paso
        self.ejecutando_paso_automatico = False
        
        # Variable para controlar estado de pantalla completa
        self.fullscreen = True
        
        # Cargar programa de ejemplo
        self.cargar_ejemplo()

    def toggle_fullscreen(self, event=None):
        """Alternar entre pantalla completa y ventana normal"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.root.state('zoomed')  # Maximizar en Windows
        else:
            self.root.state('normal')  # Ventana normal
            self.root.geometry("1400x900")  # Tamaño por defecto

    def cargar_ejemplo(self):
        """Carga un programa de ejemplo"""
        ejemplo = """; Programa de ejemplo - suma de los primeros 5 enteros
LOADV R1, 5      ; n = 5
CLEAR R2         ; acumulador = 0

LOOP:
ADD R2, R1       ; acumulador += n
DEC R1           ; n--
CMPV R1, 0       ; comparar n con 0
JNE LOOP         ; si n != 0, saltar al loop

; Mostrar resultado
SVIO R2, 0x30    ; guardar resultado en IO[0x30]  
SHOWIO 0x30      ; mostrar resultado
PARAR            ; terminar programa"""
        
        self.texto_programa.insert("1.0", ejemplo)
        self.set_salida("¡Simulador listo! Haz clic en 'Cargar Programa' y luego 'Ejecutar'")     


    # ========== Metodos ==========
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

    def cargar_programa(self):
        """Carga y ensambla el programa desde el área de texto"""
        texto = self.texto_programa.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Advertencia", "No hay código para cargar")
            return
        
            
        try:
           # Ensamblar el código
            self.programa_actual = self.assembler.assemble(texto)
            
            # Mostrar la traducción

            start = self.obtener_direccion_carga()

            traduccion = "Código ensamblado:\n\n"
            for i, instr in enumerate(self.programa_actual):
                addr = i * 8 + start
                desasm = self.assembler.disassemble_instruction(instr)
                traduccion += f"{addr:04x}: {instr:016x}\n      {desasm}\n\n"
            
            self.set_traduccion(traduccion)
            
            # Cargar programa en la CPU
            
            print(start)
            program_info = self.loader.load_program(
                    self.programa_actual, 
                    start_address=start, 
                    program_name="program_name"
                )
            self.cpu.set_pc(start)
            self.update_gui()
            self.set_salida("Programa cargado exitosamente. ¡Haz clic en 'Ejecutar'!")
        except Exception as e:
            messagebox.showerror("Error", f"Error al ensamblar programa:\n{str(e)}")
            self.set_traduccion(f"Error de ensamblado:\n{str(e)}")

    def ejecutar_programa(self):
        """Ejecuta el programa completo"""
        if not self.programa_actual:
            messagebox.showwarning("Advertencia", "Primero carga un programa")
            return
        
        modo = self.modo.get()
        
        if modo == "automatico":
            # Modo automático: ejecutar todo de una vez
            print("SIA")
            self.set_salida("Ejecutando programa...\n")
            self.cpu.run(step_mode=False)
            self.append_salida(
                pformat(self.cpu.io_map, indent=4, width=40, sort_dicts=False)
                )
            self.append_salida("\nPrograma terminado")
        elif modo == "paso":
            # Modo paso a paso: ejecutar con pausas
            self.set_salida("Ejecutando programa paso a paso...\n")
            self.ejecutando_paso_automatico = True
            self.boton_parar.config(state="normal")
            self.ejecutar_modo_paso_automatico()
            
        self.update_gui()
        try: pass
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la ejecución:\n{str(e)}")
            self.append_salida(f"\nError: {str(e)}")
            

    def ejecutar_modo_paso_automatico(self):
        """Ejecuta el programa paso a paso con pausas automáticas"""
        if not self.ejecutando_paso_automatico or not self.cpu.running:
            self.append_salida("Programa terminado")
            self.ejecutando_paso_automatico = False
            self.boton_parar.config(state="disabled")
            return
        
        try:
            # Ejecutar una instrucción
            self.cpu.fetch()
            ins = self.cpu.decode()
            self.cpu.execute(ins)
            #self.cpu.update_gui()
            
            # Mostrar qué instrucción se ejecutó
            instr_info = self.assembler.disassemble_instruction(self.cpu.ir)
            self.append_salida(f"Ejecutado: {instr_info}")
            
            # Si el programa sigue corriendo y no se ha pausado, programar la siguiente instrucción
            if self.cpu.running and self.ejecutando_paso_automatico:
                # Pausa de 1 segundo y continúa automáticamente
                self.root.after(1000, self.ejecutar_modo_paso_automatico)
            else:
                self.append_salida("Programa terminado")
                self.ejecutando_paso_automatico = False
                self.boton_parar.config(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar paso:\n{str(e)}")
            self.append_salida(f"Error: {str(e)}")
            self.ejecutando_paso_automatico = False
            self.boton_parar.config(state="disabled")

    def parar_ejecucion(self):
        """Para la ejecución paso a paso automática"""
        self.ejecutando_paso_automatico = False
        self.boton_parar.config(state="disabled")
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
        self.boton_parar.config(state="disabled")
        
        # Reiniciar componentes
        self.cpu = CPU(self.cpu.memory)
        ##self.disco = Disco()  # También reiniciar el disco
        self.programa_actual = []  # Limpiar programa actual
        
        # Limpiar interfaz
        self.update_gui()
        self.set_salida("CPU y memoria reiniciados. ¡Carga un nuevo programa!")
        self.set_traduccion("Traducción aparecerá aquí después de cargar un programa...")

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

    def set_traduccion(self, texto):
        """Actualizar la traducción en el label central"""
        PC = self.CPU.pc
        for i, text in enumerate(texto.splitlines()):
            ##Load into real memory
            self.memory.write64(PC+i*8,int(text,16))
        self.memoria_viewer.redibujar()

    def set_flag(self, flag, valor):
        """Asignar valor a una bandera"""
        if flag in self.flags:
            self.flags[flag].config(text=str(valor))

    def set_registro(self, reg, valor):
        """Asignar valor a un registro"""
        if reg in self.registros:
            self.registros[reg].config(text=str(valor))

    def set_traduccion(self, texto):
        """Actualizar la traducción"""
        self.label_traduccion.delete("1.0", "end")
        self.label_traduccion.insert("1.0", texto)

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

    def correr_programa(self):

        #TODO modos de ejecucion por ahora automatico
        self.CPU.run()
        self.update_resgitros()
        self.update_flags()
        self.CPU.dump_state()

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
        self.set_flag("PC (Program Counter)", self.cpu.pc)

    def mainloop(self):
        self.root.mainloop()