import tkinter as tk
from tkinter import ttk

import sys
import os
from pprint import pformat

# Añadir el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.CPU import CPU
#from disco_64bits import Disco
from compiler.ensamblador import Ensamblador
from logic.Loader import Loader

class SimuladorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador Atlas – Nueva GUI")
        self.root.state("zoomed")

        self._crear_columnas()

        self.root.mainloop()

    # =============================================================
    #   CREAR ESTRUCTURA DE LAS CUATRO COLUMNAS PRINCIPALES
    # =============================================================
    def _crear_columnas(self):
        contenedor = ttk.Frame(self.root)
        contenedor.pack(fill="both", expand=True, padx=10, pady=10)

        # Columnas
        col1 = ttk.Frame(contenedor)
        col2 = ttk.Frame(contenedor)
        col3 = ttk.Frame(contenedor)
        col4 = ttk.Frame(contenedor)

        col1.pack(side="left", fill="both", expand=True, padx=5)
        col2.pack(side="left", fill="both", expand=True, padx=5)
        col3.pack(side="left", fill="both", expand=True, padx=5)
        #col4.pack(side="left", fill="y", padx=5)
        col4.pack(side="left", fill="both", expand=True, padx=5)

        # Construcción de cada columna
        self._columna_codigo_alto_nivel(col1)
        self._columna_codigo_assembler(col2)
        self._columna_codigo_relocalizable(col3)
        self._columna_ram_flags_registros(col4)

    # =============================================================
    #   COLUMNA 1 — CÓDIGO ALTO NIVEL
    # =============================================================
    def _columna_codigo_alto_nivel(self, parent):
        titulo = ttk.Label(parent, text="Código Alto Nivel", font=("Arial", 13, "bold"))
        titulo.pack(pady=5)

        frame_text = ttk.Frame(parent)
        frame_text.pack(fill="both", expand=True)

        self.texto_alto = tk.Text(frame_text, wrap="none")
        self.texto_alto.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(frame_text, orient="vertical", command=self.texto_alto.yview)
        scroll_y.pack(side="right", fill="y")
        self.texto_alto.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(parent, orient="horizontal", command=self.texto_alto.xview)
        scroll_x.pack(fill="x")
        self.texto_alto.configure(xscrollcommand=scroll_x.set)

        ttk.Button(parent, text="Compilar").pack(fill="x", pady=10)

        # Botones inferiores
        f = ttk.Frame(parent)
        f.pack(fill="x", pady=10)

        ttk.Button(f, text="Cargar Archivo").pack(fill="x", pady=2)
        ttk.Button(f, text="Reset").pack(fill="x", pady=2)
        ttk.Button(f, text="Siguiente instrucción").pack(fill="x", pady=2)
        ttk.Button(f, text="Saltar a última ins").pack(fill="x", pady=2)

    # =============================================================
    #   COLUMNA 2 — CÓDIGO ASSEMBLER
    # =============================================================
    def _columna_codigo_assembler(self, parent):
        titulo = ttk.Label(parent, text="Código Assembler", font=("Arial", 13, "bold"))
        titulo.pack(pady=5)

        frame_text = ttk.Frame(parent)
        frame_text.pack(fill="both", expand=True)

        self.texto_asm = tk.Text(frame_text, wrap="none")
        self.texto_asm.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(frame_text, orient="vertical", command=self.texto_asm.yview)
        scroll_y.pack(side="right", fill="y")
        self.texto_asm.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(parent, orient="horizontal", command=self.texto_asm.xview)
        scroll_x.pack(fill="x")
        self.texto_asm.configure(xscrollcommand=scroll_x.set)

        ttk.Button(parent, text="Ensamblar").pack(fill="x", pady=10)

    # =============================================================
    #   COLUMNA 3 — CÓDIGO RELOCALIZABLE + SALIDA
    # =============================================================
    def _columna_codigo_relocalizable(self, parent):
        titulo = ttk.Label(parent, text="Código Relocalizable", font=("Arial", 13, "bold"))
        titulo.pack(pady=5)

        frame_text = ttk.Frame(parent)
        frame_text.pack(fill="both", expand=True)

        self.texto_relo = tk.Text(frame_text, wrap="none")
        self.texto_relo.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(frame_text, orient="vertical", command=self.texto_relo.yview)
        scroll_y.pack(side="right", fill="y")
        self.texto_relo.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(parent, orient="horizontal", command=self.texto_relo.xview)
        scroll_x.pack(fill="x")
        self.texto_relo.configure(xscrollcommand=scroll_x.set)

        # Cuadro verde = dirección de carga
        ttk.Label(parent, text="Dirección de carga (hex):").pack()
        self.entry_load = ttk.Entry(parent)
        self.entry_load.pack(fill="x", pady=5)

        ttk.Button(parent, text="Enlazar y Cargar").pack(fill="x", pady=10)

        # Salida
        ttk.Label(parent, text="Salida", font=("Arial", 12, "bold")).pack(pady=5)

        frame_out = ttk.Frame(parent)
        frame_out.pack(fill="both", expand=True)

        self.texto_salida = tk.Text(frame_out, wrap="word")
        self.texto_salida.pack(side="left", fill="both", expand=True)

        scroll_out = ttk.Scrollbar(frame_out, orient="vertical",
                                   command=self.texto_salida.yview)
        scroll_out.pack(side="right", fill="y")
        self.texto_salida.configure(yscrollcommand=scroll_out.set)

    # =============================================================
    #   COLUMNA 4 — RAM + FLAGS + REGISTROS
    # =============================================================
    def _columna_ram_flags_registros(self, parent):
        # ------------------- RAM -------------------
        ttk.Label(parent, text="RAM", font=("Arial", 13, "bold")).pack()

        frame_ram = ttk.Frame(parent, borderwidth=2, relief="solid")
        frame_ram.pack(fill="both", pady=5)

        # Tabla RAM con dirección y valores hex
        columns = ("dir", "hex")
        self.tree_ram = ttk.Treeview(frame_ram, columns=columns, show="headings", height=10)
        self.tree_ram.heading("dir", text="DIR")
        self.tree_ram.heading("hex", text="HEX_VAL")
        self.tree_ram.column("dir", width=70, anchor="center")
        self.tree_ram.column("hex", width=120, anchor="center")
        self.tree_ram.pack(side="left", fill="both", expand=True)

        scroll_ram = ttk.Scrollbar(frame_ram, orient="vertical",
                                   command=self.tree_ram.yview)
        scroll_ram.pack(side="right", fill="y")
        self.tree_ram.configure(yscrollcommand=scroll_ram.set)
        
        # ------------------- FLAGS -------------------
        ttk.Label(parent, text="Flags", font=("Arial", 12, "bold")).pack(pady=5)

        frame_flags = ttk.Frame(parent, borderwidth=2, relief="solid")
        frame_flags.pack(pady=5, fill="x")

        # Z N
        self._fila_flag(frame_flags, "Z", "N")
        # C V
        self._fila_flag(frame_flags, "C", "V")
        # PC
        self._fila_flag(frame_flags, "PC", None)

        # ------------------- REGISTROS -------------------
        ttk.Label(parent, text="Registros", font=("Arial", 12, "bold")).pack(pady=5)

        frame_regs = ttk.Frame(parent, borderwidth=2, relief="solid")
        frame_regs.pack(pady=5, fill="x")

        self.reg_labels = {}

        for i in range(0, 16, 2):
            fila = ttk.Frame(frame_regs)
            fila.pack(fill="x", pady=1)

            r1 = f"R{i:02}"
            r2 = f"R{i+1:02}"

            ttk.Label(fila, text=r1).pack(side="left", padx=5)
            self.reg_labels[r1] = ttk.Entry(fila, width=8)
            self.reg_labels[r1].pack(side="left", padx=5)

            ttk.Label(fila, text=r2).pack(side="left", padx=5)
            self.reg_labels[r2] = ttk.Entry(fila, width=8)
            self.reg_labels[r2].pack(side="left", padx=5)

    # =============================================================
    #   Construcción de una fila de flags
    # =============================================================
    def _fila_flag(self, parent, f1, f2):
        fila = ttk.Frame(parent)
        fila.pack(fill="x", pady=3)

        ttk.Label(fila, text=f1).pack(side="left", padx=5)
        ttk.Entry(fila, width=5).pack(side="left", padx=5)

        if f2:
            ttk.Label(fila, text=f2).pack(side="left", padx=5)
            ttk.Entry(fila, width=5).pack(side="left", padx=5)

# =============================================================
#   EJECUTAR GUI
# =============================================================
if __name__ == "__main__":
    SimuladorGUI()

