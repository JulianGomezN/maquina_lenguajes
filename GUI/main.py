import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import os

# Añadir el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CPU import CPU
from disco_64bits import Disco
from assembler import Assembler


class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador - Atlas")
        
        # Configurar pantalla completa
        self.root.state('zoomed')  # Para Windows - maximiza la ventana
        
        # Permitir salir de pantalla completa con ESC
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Inicializar componentes del simulador
        self.cpu = CPU(gui=self)
        self.disco = Disco()
        self.assembler = Assembler()
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
        
        # FILA 2: Controles de estado
        self.boton_parar = ttk.Button(buttons_container, text="⏹️ Parar", 
                                     command=self.parar_ejecucion, state="disabled", width=20)
        self.boton_parar.grid(row=2, column=0, padx=3, pady=2, sticky="ew")
        
        ttk.Button(buttons_container, text="🔄 Reset CPU", 
                  command=self.reset_cpu, width=20).grid(row=2, column=1, padx=3, pady=2, sticky="ew")
        
        ttk.Button(buttons_container, text="📊 Info Cargador", 
                  command=self.mostrar_info_cargador, width=20).grid(row=2, column=2, padx=3, pady=2, sticky="ew")

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
            traduccion = "Código ensamblado:\n\n"
            for i, instr in enumerate(self.programa_actual):
                addr = i * 8
                desasm = self.assembler.disassemble_instruction(instr)
                traduccion += f"{addr:04x}: {instr:016x}\n      {desasm}\n\n"
            
            self.set_traduccion(traduccion)
            
            # Cargar programa en la CPU
            self.cpu.load_program(self.programa_actual, start=0)
            self.cpu.update_gui()
            
            self.set_salida("Programa cargado exitosamente. ¡Haz clic en 'Ejecutar'!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ensamblar programa:\n{str(e)}")
            self.set_traduccion(f"Error de ensamblado:\n{str(e)}")

    def ejecutar_programa(self):
        """Ejecuta el programa completo"""
        if not self.programa_actual:
            messagebox.showwarning("Advertencia", "Primero carga un programa")
            return
        
        try:
            modo = self.modo.get()
            
            if modo == "automatico":
                # Modo automático: ejecutar todo de una vez
                self.set_salida("Ejecutando programa...\n")
                self.cpu.run(step_mode=False)
                self.append_salida("\nPrograma terminado")
                
            elif modo == "paso":
                # Modo paso a paso: ejecutar con pausas
                self.set_salida("Ejecutando programa paso a paso...\n")
                self.ejecutando_paso_automatico = True
                self.boton_parar.config(state="normal")
                self.ejecutar_modo_paso_automatico()
            
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
            raw = self.cpu.fetch()
            ins = self.cpu.decode(raw)
            self.cpu.execute(ins)
            self.cpu.update_gui()
            
            # Mostrar qué instrucción se ejecutó
            instr_info = self.assembler.disassemble_instruction(raw)
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
            memory_map = self.cpu.get_loader_info()
            loaded_programs = self.cpu.list_loaded_programs()
            
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
        
        try:
            # Ejecutar una sola instrucción
            raw = self.cpu.fetch()
            ins = self.cpu.decode(raw)
            self.cpu.execute(ins)
            self.cpu.update_gui()
            
            # Mostrar información de la instrucción ejecutada
            instr_info = self.assembler.disassemble_instruction(raw)
            self.append_salida(f"Ejecutado: {instr_info}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar paso:\n{str(e)}")
            self.append_salida(f"Error: {str(e)}")

    def reset_cpu(self):
        """Reinicia el estado del CPU"""
        # Parar cualquier ejecución paso a paso en curso
        self.ejecutando_paso_automatico = False
        self.boton_parar.config(state="disabled")
        
        # Reiniciar componentes
        self.cpu = CPU(gui=self)
        self.disco = Disco()  # También reiniciar el disco
        self.programa_actual = []  # Limpiar programa actual
        
        # Limpiar interfaz
        self.cpu.update_gui()
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
        self.label_traduccion.config(text=texto)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGUI(root)
    root.mainloop()
