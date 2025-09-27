import tkinter as tk

class MemoryViewer(tk.Frame):
    def __init__(self, master, memory, celda_size=8, filas_visibles=50):
        super().__init__(master)
        self.memory = memory
        self.celda_size = celda_size
        self.total_filas = max(1, memory.size // celda_size)
        self.filas_visibles = filas_visibles
        self.offset = 0
        self.row_h = 20

        self.highlight_rows = {}
        self.format_addr = "hex"

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.on_scroll)
        self.scrollbar.pack(side="right", fill="y")

        # Canvas
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # eventos
        self.canvas.bind("<Configure>", lambda e: self.redibujar())
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Win/Mac
        self.canvas.bind_all("<Button-4>", self.on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel_linux)

        self.redibujar()

    # --- scroll vertical ---
    def on_scroll(self, *args):
        if args[0] == 'moveto':
            frac = float(args[1])
            self.offset = int(frac * (self.total_filas - self.filas_visibles))
        elif args[0] == 'scroll':
            try:
                step = int(args[1])
            except ValueError:
                step = 1
            if len(args) > 2 and args[2] == 'pages':
                step *= self.filas_visibles
            self.offset += step

        self.offset = max(0, min(self.offset, self.total_filas - self.filas_visibles))
        self.redibujar()

    def on_mousewheel(self, event):
        step = -1 if event.delta > 0 else 1
        self.offset += step
        self.offset = max(0, min(self.offset, self.total_filas - self.filas_visibles))
        self.redibujar()

    def on_mousewheel_linux(self, event):
        step = -1 if event.num == 4 else 1
        self.offset += step
        self.offset = max(0, min(self.offset, self.total_filas - self.filas_visibles))
        self.redibujar()

    # --- dibujar ---
    def redibujar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()

        # scrollbar estable: fracción visible = filas_visibles/total
        start_frac = self.offset / self.total_filas
        end_frac = (self.offset + self.filas_visibles) / self.total_filas
        self.scrollbar.set(start_frac, end_frac)

        for i in range(self.filas_visibles):
            fila_idx = self.offset + i
            if fila_idx >= self.total_filas:
                break

            y = i * self.row_h
            addr = fila_idx * self.celda_size
            valor64 = self.memory.read64(addr)

            # fondo
            color = self.highlight_rows.get(fila_idx, "white")
            self.canvas.create_rectangle(0, y, w, y + self.row_h,
                                         fill=color, outline="black", width=1)

            # dirección
            if self.format_addr == "hex":
                addr_str = f"{addr:08X}"
            elif self.format_addr == "dec":
                addr_str = str(addr)
            elif self.format_addr == "bin":
                addr_str = f"{addr:08b}"
            else:
                addr_str = str(addr)

            self.canvas.create_text(10, y + self.row_h / 2, anchor="w",
                                    text=addr_str)

            # valor
            self.canvas.create_text(w - 10, y + self.row_h / 2, anchor="e",
                                    text=f"{valor64:016X}")

    # --- API pública ---
    def goto_fila(self, fila_idx):
        self.offset = max(0, min(fila_idx, self.total_filas - self.filas_visibles))
        self.redibujar()

    def pintar_fondo(self, fila_idx, color):
        self.highlight_rows[fila_idx] = color
        self.redibujar()

    def set_format_addr(self, fmt):
        """Cambiar formato de dirección (hex, dec, bin)"""
        self.format_addr = fmt
        self.redibujar()
