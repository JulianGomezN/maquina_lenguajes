import os
import re
import atexit

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1
MASK16 = (1 << 16) - 1
MASK8  = (1 << 8) - 1

def to_uint64(x: int) -> int:
    return x & MASK64

def to_int_from_bytes(b: bytes, signed: bool = False) -> int:
    return int.from_bytes(b, byteorder='little', signed=signed)

def to_bytes_from_int(x: int, size: int) -> bytes:
    return int(x).to_bytes(size, byteorder='little', signed=False)

class Memory:
    """
    Memoria lineal de bytes con utilidades para leer/escribir
    valores de 1, 2, 4 y 8 bytes en little endian.
    """
    def __init__(self, size: int, *, memory_file: str | None = None, auto_load: bool = True, auto_save_at_exit: bool = True):
        """
        size: tamaño de la RAM en bytes.
        memory_file: ruta del archivo .txt para persistencia. Si None, usa 'memory_ram.txt' en el cwd.
        auto_load: si True, intenta cargar la RAM desde memory_file al construir.
        auto_save_at_exit: si True, guarda automáticamente la RAM en memory_file al terminar el proceso.
        """
        self.size = size
        # array de bytes, inicializado a 0
        self.mem = bytearray(size)

        # Configuración de archivo de memoria por defecto
        self.memory_file = memory_file or os.path.join(os.getcwd(), "memory_ram.txt")

        # Cargar contenido previo si existe y está habilitado
        if auto_load and os.path.exists(self.memory_file):
            try:
                self.load_from_txt(self.memory_file)
            except Exception:
                # En caso de error al cargar, continuar con RAM en cero
                pass

        # Registrar guardado automático al salir
        if auto_save_at_exit:
            def _save_on_exit():
                try:
                    self.save_to_txt(self.memory_file)
                except Exception:
                    pass
            atexit.register(_save_on_exit)

    def _check_range(self, addr: int, nbytes: int):
        if addr < 0 or addr + nbytes > self.size:
            raise IndexError(f"Dirección fuera de rango: {addr}..{addr+nbytes-1}")

    # ---------- Lecturas ----------
    def read(self, addr: int, size: int, signed: bool = False) -> int:
        """Leer un valor de size bytes (1, 2, 4, 8) desde memoria en little endian"""
        if size not in (1, 2, 4, 8):
            raise ValueError("El tamaño debe ser 1, 2, 4 u 8 bytes")

        self._check_range(addr, size)
        data = self.mem[addr:addr+size]
        return int.from_bytes(data, byteorder="little", signed=signed)

    # ---------- Escrituras ----------
    def write(self, addr: int, val: int, size: int):
        """Escribir un valor de size bytes (1, 2, 4, 8) en memoria en little endian"""
        if size not in (1, 2, 4, 8):
            raise ValueError("El tamaño debe ser 1, 2, 4 u 8 bytes")

        self._check_range(addr, size)
        # Convertir a bytes en little endian, siempre unsigned
        self.mem[addr:addr+size] = int(val).to_bytes(size, byteorder="little", signed=False)


    # ---------- Utilidades ----------
    def dump(self, start: int = 0, end: int = 64):
        """Volcar memoria en hex desde start a end"""
        self._check_range(start, end - start)
        for i in range(start, end, 8):
            chunk = self.mem[i:i+8]
            hexs = ' '.join(f'{b:02X}' for b in chunk)
            print(f'{i:08X}: {hexs}')

    def load_bytes(self, addr: int, data: bytes):
        """Cargar bytes crudos en memoria"""
        self._check_range(addr, len(data))
        self.mem[addr:addr+len(data)] = data

    def get_bytes(self, addr: int, n: int) -> bytes:
        """Obtener n bytes crudos desde memoria"""
        self._check_range(addr, n)
        return bytes(self.mem[addr:addr+n])

    def __len__(self):
        return self.size
    
    def __getitem__(self, key):
        return self.mem[key]

    def __setitem__(self, key, value):
        self.mem[key] = value

    # ---------- Persistencia en .txt ----------
    def save_to_txt(self, path: str):
        """
        Guarda la RAM completa en un archivo .txt en formato legible:
        - 8 bytes por línea, en hexadecimal, con dirección base al inicio.
        Ejemplo de línea: "0000: 00 3A FF 10 00 00 00 80"
        """
        # Asegurar directorio existente
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# RAM size: {self.size} bytes\n")
            for addr in range(0, self.size, 8):
                chunk = self.mem[addr:addr+8]
                # si al final no hay 8 bytes, se completa a 8 con 0 para consistencia visual
                if len(chunk) < 8:
                    chunk = bytes(chunk) + bytes(8 - len(chunk))
                hexs = ' '.join(f'{b:02X}' for b in chunk)
                f.write(f"{addr:04X}: {hexs}\n")

    def load_from_txt(self, path: str):
        """
        Carga la RAM desde un archivo .txt con bytes hexadecimales.
        Se aceptan líneas con o sin dirección al inicio. Se ignoran líneas vacías y comentarios (# ...).
        Si el archivo contiene menos bytes que la RAM, el resto quedará en 0. Si contiene más, se ignora el excedente.
        """
        # Resetear RAM a cero antes de cargar
        self.mem[:] = b"\x00" * self.size

        hex_byte_re = re.compile(r'\b([0-9A-Fa-f]{2})\b')
        write_ptr = 0
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Extraer pares hexadecimales en la línea
                for m in hex_byte_re.finditer(line):
                    if write_ptr >= self.size:
                        return  # ya llenamos la RAM
                    byte_val = int(m.group(1), 16)
                    self.mem[write_ptr] = byte_val
                    write_ptr += 1
        # Si el archivo tiene menos bytes, el resto ya está en 0