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
    def read8(self, addr: int, signed: bool = False) -> int:
        """Leer 1 byte"""
        self._check_range(addr, 1)
        return int.from_bytes(self.mem[addr:addr+1], 'little', signed=signed)

    def read16(self, addr: int, signed: bool = False) -> int:
        """Leer 2 bytes"""
        self._check_range(addr, 2)
        return int.from_bytes(self.mem[addr:addr+2], 'little', signed=signed)

    def read32(self, addr: int, signed: bool = False) -> int:
        """Leer 4 bytes"""
        self._check_range(addr, 4)
        return int.from_bytes(self.mem[addr:addr+4], 'little', signed=signed)

    def read64(self, addr: int, signed: bool = False) -> int:
        """Leer 8 bytes"""
        self._check_range(addr, 8)
        return int.from_bytes(self.mem[addr:addr+8], 'little', signed=signed)

    # ---------- Escrituras ----------
    def write8(self, addr: int, val: int):
        """Escribir 1 byte"""
        self._check_range(addr, 1)
        self.mem[addr:addr+1] = val.to_bytes(1, 'little', signed=False)

    def write16(self, addr: int, val: int):
        """Escribir 2 bytes"""
        self._check_range(addr, 2)
        self.mem[addr:addr+2] = val.to_bytes(2, 'little', signed=False)

    def write32(self, addr: int, val: int):
        """Escribir 4 bytes"""
        self._check_range(addr, 4)
        self.mem[addr:addr+4] = val.to_bytes(4, 'little', signed=False)

    def write64(self, addr: int, val: int):
        """Escribir 8 bytes"""
        self._check_range(addr, 8)
        self.mem[addr:addr+8] = to_uint64(val).to_bytes(8, 'little', signed=False)

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