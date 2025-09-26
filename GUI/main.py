import tkinter as tk
from tkinter import ttk


class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador - Atlas")
        self.root.geometry("1200x700")

        # === LAYOUT PRINCIPAL (3 columnas) ===
        self.root.grid_columnconfigure(0, weight=1)  # izquierda
        self.root.grid_columnconfigure(1, weight=2)  # centro
        self.root.grid_columnconfigure(2, weight=1)  # derecha

        # ================== IZQUIERDA: Cargar programa ==================
        frame_carga = ttk.LabelFrame(root, text="Cargar programa")
        frame_carga.grid(row=0, column=0, rowspan=3, sticky="nswe", padx=10, pady=10)

        self.texto_programa = tk.Text(frame_carga, height=30, width=40)
        self.texto_programa.pack(side="top", padx=5, pady=5, fill="both", expand=True)

        self.boton_cargar = ttk.Button(frame_carga, text="Cargar texto", command=self.cargar_programa)
        self.boton_cargar.pack(side="bottom", padx=5, pady=5)

        # ================== CENTRO: Traducción ==================
        frame_traduccion = ttk.LabelFrame(root, text="Traducción")
        frame_traduccion.grid(row=0, column=1, rowspan=3, sticky="nswe", padx=10, pady=10)

        self.label_traduccion = tk.Label(frame_traduccion, 
                                         text="traducción del codigo a binario",
                                         relief="sunken", 
                                         anchor="center", 
                                         justify="center",
                                         wraplength=400, width=40, height=25, 
                                         bg="white")
        self.label_traduccion.pack(fill="both", expand=True, padx=10, pady=10)

        # ================== DERECHA: Banderas y contador ==================
        frame_flags = ttk.LabelFrame(root, text="Banderas y Contador")
        frame_flags.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        self.flags = {}
        for flag in ["Z (Zero)", "N (Negative)", "C (Carry)", "V (Overflow)", "PC (Program Counter)"]:
            subframe = ttk.Frame(frame_flags)
            subframe.pack(pady=5)

            label = ttk.Label(subframe, text=flag, width=18)
            label.pack(side="left")

            valor = ttk.Label(subframe, text="0", width=8, relief="solid", anchor="center")
            valor.pack(side="left", padx=5)
            self.flags[flag] = valor

        # ================== DERECHA: Modo de ejecución ==================
        frame_ejecucion = ttk.LabelFrame(root, text="Modo de ejecución")
        frame_ejecucion.grid(row=1, column=2, sticky="nswe", padx=10, pady=10)

        self.modo = tk.StringVar(value="automatico")

        ttk.Radiobutton(frame_ejecucion, text="Automático", variable=self.modo, value="automatico").pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(frame_ejecucion, text="Paso a paso", variable=self.modo, value="paso").pack(anchor="w", padx=10, pady=5)

        # ================== DERECHA: Registros ==================
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

    # ========== Metodos ==========
    def cargar_programa(self):
        texto = self.texto_programa.get("1.0", "end").strip()
        print("Programa cargado:\n", texto)

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


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGUI(root)

    app.set_registro("R04",5)

    app.set_flag("Z (Zero)",1)

    root.mainloop()


