import tkinter as tk
from tkinter import ttk, filedialog, messagebox
#from ProcesadorCPU import CPU
#from cargador import loader_cpu
from tkinter import scrolledtext
import binascii

# ===============================
# ESTRUCTURA DE VENTANA
# ===============================
root = tk.Tk()
root.title("Interfaz de Simulador 1801M - Layout 4 Columnas")
root.geometry("1600x900")

cpu = CPU()

# -------------------------------
# FUNCIONES DE TU CÓDIGO ORIGINAL
# -------------------------------

def cargar_programa():
    archivo_path = filedialog.askopenfilename(filetypes=[("Archivos binarios", "*.bin")])
    if archivo_path:
        try:
            with open(archivo_path, "rb") as archivo_bin:
                programa_binario = archivo_bin.read()
                cpu.ram.memoria = programa_binario
                mostrar_ram()
                messagebox.showinfo("Carga exitosa", f"Programa cargado desde {archivo_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el programa: {str(e)}")

def ejecutar_programa():
    try:
        loader = loader_cpu(cpu)
        loader.cargar_y_ejecutar()
        mostrar_ram()
    except Exception as e:
        messagebox.showerror("Error de ejecución", f"Se produjo un error: {str(e)}")

ram_text_area = None  # Será asignado al crear widgets

def mostrar_ram():
    if ram_text_area:
        ram_text_area.delete("1.0", tk.END)
        for direccion in range(0, len(cpu.ram.memoria), 2):
            if direccion + 1 < len(cpu.ram.memoria):
                palabra = cpu.ram.memoria[direccion] << 8 | cpu.ram.memoria[direccion + 1]
                ram_text_area.insert(
                    tk.END, f"0x{cpu.ram.base_direccion + direccion:04X}: 0x{palabra:04X}\n"
                )

def guardar_cambios_ram():
    try:
        lineas = ram_text_area.get("1.0", tk.END).strip().split("\n")
        for idx, linea in enumerate(lineas):
            if ":" in linea:
                _, valor_hex = linea.split(":")
                palabra_str = valor_hex.strip().replace("0x", "")
                if len(palabra_str) != 4:
                    raise ValueError("Formato inválido")

                palabra = int(palabra_str, 16)
                cpu.ram.escribir_palabra_en_cualquier_direccion(idx * 2, palabra)

        messagebox.showinfo("RAM actualizada", "Los valores han sido guardados.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la RAM: {str(e)}")

def actualizar_registros_y_flags():
    for reg in cpu.registros:
        if reg in registros_dict:
            registros_dict[reg].delete(0, tk.END)
            registros_dict[reg].insert(0, str(cpu.registros[reg]))

    flags_dict["Z"].delete(0, tk.END); flags_dict["Z"].insert(0, str(cpu.flags[0]))
    flags_dict["N"].delete(0, tk.END); flags_dict["N"].insert(0, str(cpu.flags[1]))
    flags_dict["C"].delete(0, tk.END); flags_dict["C"].insert(0, str(cpu.flags[2]))
    flags_dict["V"].delete(0, tk.END); flags_dict["V"].insert(0, str(cpu.flags[3]))
    flags_dict["PC"].delete(0, tk.END); flags_dict["PC"].insert(0, cpu.registros["PC"])

def limpiar_todo():
    texto_assembly.delete("1.0", tk.END)
    texto_salida.delete(0, tk.END)
    entrada_direccion.delete(0, tk.END)
    ram_text_area.delete("1.0", tk.END)

def generar_binario():
    codigo = texto_assembly.get("1.0", tk.END)
    binario = codigo.encode()
    texto_salida.delete(0, tk.END)
    texto_salida.insert(tk.END, binascii.hexlify(binario).decode())

def siguiente_instruccion():
    try:
        loader = loader_cpu(cpu)
        loader.ejecutar_paso()
        actualizar_registros_y_flags()
        mostrar_ram()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def ultima_instruccion():
    try:
        loader = loader_cpu(cpu)
        loader.ejecutar_todo()
        actualizar_registros_y_flags()
        mostrar_ram()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def ejecutar_enlazar_y_cargar():
    direccion_texto = entrada_direccion.get()
    if direccion_texto:
        try:
            direccion = int(direccion_texto, 16)
            cpu.ram.base_direccion = direccion
            messagebox.showinfo("Dirección actualizada", f"Base de RAM modificada a {direccion_texto}")
        except:
            messagebox.showerror("Error", "Dirección inválida (usar hexadecimal).")
            return

    try:
        loader = loader_cpu(cpu)
        loader.cargar_y_ejecutar()
        mostrar_ram()
        actualizar_registros_y_flags()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo completar: {str(e)}")

texto_assembly = None
texto_salida = None
entrada_direccion = None
registros_dict = {}
flags_dict = {}

# ===============================
# 4 COLUMNAS PRINCIPALES
# ===============================
col1 = tk.Frame(root, padx=10, pady=10)
col2 = tk.Frame(root, padx=10, pady=10)
col3 = tk.Frame(root, padx=10, pady=10)
col4 = tk.Frame(root, padx=10, pady=10)

col1.grid(row=0, column=0, sticky="n")
col2.grid(row=0, column=1, sticky="n")
col3.grid(row=0, column=2, sticky="n")
col4.grid(row=0, column=3, sticky="n")

# ===============================
# COLUMNA 1 — Código Alto Nivel
# ===============================
tk.Label(col1, text="Código Alto Nivel", font=("Arial", 12, "bold")).pack()
txt_alto = scrolledtext.ScrolledText(col1, width=40, height=20)
txt_alto.pack()

tk.Button(col1, text="Compilar", bg="#b3e6ff").pack(pady=5)

bottom1 = tk.Frame(col1)
bottom1.pack(pady=15)

tk.Button(bottom1, text="Cargar Archivo", bg="#b3e6ff", command=cargar_programa, width=18).grid(row=0, column=0, pady=4)
tk.Button(bottom1, text="Reset", bg="#b3e6ff", command=limpiar_todo, width=18).grid(row=1, column=0, pady=4)

# ===============================
# COLUMNA 2 — Código Assembler
# ===============================
tk.Label(col2, text="Código Assembler", font=("Arial", 12, "bold")).pack()
texto_assembly = scrolledtext.ScrolledText(col2, width=40, height=20)
texto_assembly.pack()

tk.Button(col2, text="Ensamblar", bg="#b3e6ff", command=generar_binario).pack(pady=5)

bottom2 = tk.Frame(col2)
bottom2.pack(pady=15)

tk.Button(bottom2, text="Siguiente Instrucción", bg="#b3e6ff", command=siguiente_instruccion, width=18).grid(row=0, column=0, pady=4)
tk.Button(bottom2, text="Saltar a Última Ins", bg="#b3e6ff", command=ultima_instruccion, width=18).grid(row=1, column=0, pady=4)

# ===============================
# COLUMNA 3 — Relocalizable + Cargar + Salida
# ===============================
tk.Label(col3, text="Código Relocalizable", font=("Arial", 12, "bold")).pack()
texto_relocalizable = scrolledtext.ScrolledText(col3, width=40, height=20)
texto_relocalizable.pack()

# Entrada verde
direccion_frame = tk.Frame(col3, bg="#90ee90")
direccion_frame.pack(pady=5)

entrada_direccion = tk.Entry(direccion_frame, width=10)
entrada_direccion.pack()

tk.Button(col3, text="Enlazar y Cargar", bg="#b3e6ff", command=ejecutar_enlazar_y_cargar).pack(pady=5)

tk.Label(col3, text="Salida", font=("Arial", 12, "bold")).pack(pady=4)
texto_salida = tk.Entry(col3, width=50)
texto_salida.pack()

# ===============================
# COLUMNA 4 — RAM + Flags + Registros
# ===============================
tk.Label(col4, text="RAM", font=("Arial", 12, "bold")).pack()

ram_frame = scrolledtext.ScrolledText(col4, width=40, height=25)
ram_frame.pack()
ram_text_area = ram_frame

tk.Button(col4, text="Guardar RAM", bg="#b3e6ff", command=guardar_cambios_ram).pack(pady=3)

# FLAGS
tk.Label(col4, text="Flags", font=("Arial", 12, "bold")).pack(pady=4)
flags_area = tk.Frame(col4)
flags_area.pack()

for flag in ["Z", "N", "C", "V", "PC"]:
    frame = tk.Frame(flags_area)
    tk.Label(frame, text=flag).pack(side="left")
    entry = tk.Entry(frame, width=5)
    entry.pack(side="left")
    frame.pack()
    flags_dict[flag] = entry

# REGISTROS
tk.Label(col4, text="Registros", font=("Arial", 12, "bold")).pack(pady=4)
regs_area = tk.Frame(col4)
regs_area.pack()

for i in range(0, 16, 2):
    fila = tk.Frame(regs_area)
    for r in [i, i+1]:
        tk.Label(fila, text=f"R{r:02}").pack(side="left")
        e = tk.Entry(fila, width=6)
        e.pack(side="left", padx=5)
        registros_dict[f"R{r:02}"] = e
    fila.pack()

root.mainloop()
