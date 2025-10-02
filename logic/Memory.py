from typing import Union

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
    def __init__(self, size: int):
        self.size = size
        # array de bytes, inicializado a 0
        self.mem = bytearray(size)

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