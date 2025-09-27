import tkinter as tk
from tkinter import ttk
from logic.CPU import CPU
from logic.Memory import Memory
from GUI.MemoryGUI import MemoryViewer
class SimuladorGUI:

    def __init__(self, root, CPU:CPU, memory:Memory):
        self.root = root
        self.root.title("Simulador - Atlas")
        self.root.geometry("1200x800")

        self.CPU = CPU
        self.memory = memory
        # === LAYOUT PRINCIPAL (4 columnas) ===
        self.root.grid_columnconfigure(0, weight=1)  # Columna 0
        self.root.grid_columnconfigure(1, weight=2)  # columna 1
        self.root.grid_columnconfigure(2, weight=1)  # Columna 2
        self.root.grid_columnconfigure(3, weight=1)  # Columna 3

        # ================== Columna 0: Cargar programa ==================
        frame_carga = ttk.LabelFrame(root, text="Cargar programa")
        frame_carga.grid(row=0, column=0, rowspan=3, sticky="nswe", padx=10, pady=10)

        scroll_y = tk.Scrollbar(frame_carga, orient="vertical")
        scroll_y.pack(side="left", fill="y")

        self.texto_programa = tk.Text(frame_carga, height=30, width=40, yscrollcommand=scroll_y.set)
        self.texto_programa.pack(side="top", padx=5, pady=5, fill="both", expand=True)

        scroll_y.config(command=self.texto_programa.yview)

        self.boton_cargar = ttk.Button(frame_carga, text="Cargar texto", command=self.cargar_programa)
        self.boton_cargar.pack(side="bottom", fill="x", padx=5, pady=5)

        # ================== Columna 1: Traducción ==================
        # Panel central: aquí insertamos el visor de memoria
        frame_memoria = ttk.LabelFrame(root, text="Memoria")
        frame_memoria.grid(row=0, column=1, rowspan=3, sticky="nswe", padx=10, pady=10)


        # Creamos el visor de memoria dentro del frame central
        self.memoria_viewer = MemoryViewer(frame_memoria, memory, celda_size=8)
        self.memoria_viewer.pack(fill="both", expand=True)

        # ================== Columna 2: Banderas y contador ==================
        frame_flags = ttk.LabelFrame(root, text="Banderas y Contador")
        frame_flags.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        self.flags = {}
        for flag in ["Z", "N", "C", "V", "PC"]:
            subframe = ttk.Frame(frame_flags)
            subframe.pack(pady=5)

            label = ttk.Label(subframe, text=flag, width=18)
            label.pack(side="left")

            valor = ttk.Label(subframe, text="0", width=20, relief="solid", anchor="center")
            valor.pack(side="left", padx=5)
            self.flags[flag] = valor

        # ================== Columna 2: Modo de ejecución ==================
        frame_ejecucion = ttk.LabelFrame(root, text="Modo de ejecución")
        frame_ejecucion.grid(row=1, column=2, sticky="nswe", padx=10, pady=10)

        self.modo = tk.StringVar(value="automatico")

        ttk.Radiobutton(frame_ejecucion, text="Automático", variable=self.modo, value="automatico").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(frame_ejecucion, text="Paso a paso", variable=self.modo, value="paso").pack(anchor="w", padx=10, pady=5)
        self.boton_cargar = ttk.Button(frame_ejecucion, text="Run", command=self.correr_programa)
        self.boton_cargar.pack(side="bottom", fill="x", padx=5, pady=5)


        # ================== Columna 2: Registros ==================
        frame_registros = ttk.LabelFrame(root, text="Registros")
        frame_registros.grid(row=2, column=2, sticky="nswe", padx=10, pady=10)

        self.registros = {}
        for i in range(16):  # R00 a R15
            fila = ttk.Frame(frame_registros)
            fila.pack(anchor="w", pady=2)

            reg_name = f"R{i:02}"
            label = ttk.Label(fila, text=reg_name, width=6)
            label.pack(side="left")

            valor = ttk.Label(fila, text="0", width=10, relief="solid", anchor="center")
            valor.pack(side="left", padx=5)

            self.registros[reg_name] = valor

        # ================== Columna 3: Salida ==================

        frame_salida = ttk.LabelFrame(root, text="Salida")
        frame_salida.grid(row=0, column=3, rowspan=3, sticky="nswe", padx=10, pady=10)
        
        self.label_salida = tk.Label(frame_salida, 
                                         text="Aquí aparecerá la salida",
                                         relief="sunken", 
                                         anchor="center", 
                                         justify="center",
                                         wraplength=400, width=40, height=50, 
                                         bg="white")
        self.label_salida.pack(fill="both", expand=True, padx=10, pady=10)     


    # ========== Metodos ==========
    def cargar_programa(self):
        texto = self.texto_programa.get("1.0", "end").strip()
        print("Programa cargado:\n", texto)

        ##Traducir de acuerdo a opcion solo hex por ahora
        ##TODO

        self.set_traduccion(texto)

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

    def set_salida(self, texto):
        """Actualizar el contenido del frame de salida"""
        self.label_salida.config(text=texto)

    def append_salida(self, texto):
        """Añadir texto al contenido del frame de salida"""
        actual = self.label_salida.cget("text")
        self.label_salida.config(text=actual + "\n" + texto)    

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

if __name__ == "__main__":
    root = tk.Tk()
    mem = Memory(2**10)
    app = SimuladorGUI(root,CPU(mem),mem)

    app.set_registro("R04",5)

    app.set_flag("Z (Zero)",1)

    app.set_salida("Hola")

    app.append_salida(" mundo")

    root.mainloop()