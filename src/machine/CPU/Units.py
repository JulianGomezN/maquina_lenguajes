import struct
import math
import warnings

class Flags:
    """Registra los estados de las banderas: Carry, Overflow, Zero, Negative."""
    def __init__(self):
        self.C = 0  # Carry
        self.O = 0  # Overflow
        self.Z = 0  # Zero
        self.N = 0  # Negative

    def reset(self):
        self.C = self.O = self.Z = self.N = 0

    def as_dict(self):
        return {'C': self.C, 'V': self.O, 'Z': self.Z, 'N': self.N}


class ALU:
    """Unidad Aritmético-Lógica con operaciones signed/unsigned y tamaños 1,2,4,8 bytes."""
    def __init__(self):
        self.flags = Flags()

    def _mask(self, size):
        bits = size * 8
        mask = (1 << bits) - 1
        sign_bit = 1 << (bits - 1)
        return mask, sign_bit

    def _to_signed(self, val, size):
        """Convierte un entero sin signo al valor con signo del tamaño dado."""
        mask, sign_bit = self._mask(size)
        if val & sign_bit:
            return val - (1 << (size * 8))
        return val

    def _to_unsigned(self, val, size):
        """Convierte un entero a su representación sin signo."""
        mask, _ = self._mask(size)
        return val & mask

    def _update_flags(self, result, size, carry=False, overflow=False):
        mask, sign_bit = self._mask(size)
        result &= mask
        self.flags.C = 1 if carry else 0
        self.flags.O = 1 if overflow else 0
        self.flags.Z = 1 if result == 0 else 0
        self.flags.N = 1 if result & sign_bit else 0

    # ======================================
    # Operaciones básicas
    # ======================================

    def add(self, a, b, size=4, signed=False):
        mask, sign_bit = self._mask(size)
        if signed:
            a, b = self._to_signed(a, size), self._to_signed(b, size)
        res = a + b
        carry = res > mask or res < 0
        overflow = ((a ^ res) & (b ^ res) & sign_bit) != 0
        self._update_flags(res, size, carry, overflow)
        return self._to_unsigned(res, size)

    def sub(self, a, b, size=4, signed=False):
        mask, sign_bit = self._mask(size)
        if signed:
            a, b = self._to_signed(a, size), self._to_signed(b, size)
        res = a - b
        carry = a < b
        overflow = ((a ^ b) & (a ^ res) & sign_bit) != 0
        self._update_flags(res, size, carry, overflow)
        return self._to_unsigned(res, size)

    # ======================================
    # Multiplicación
    # ======================================
    def mul(self, a, b, size=4, signed=False):
        mask, sign_bit = self._mask(size)

        if signed:
            a = self._to_signed(a, size)
            b = self._to_signed(b, size)
            res = a * b
            overflow = not (-sign_bit <= res < sign_bit)
        else:
            res = a * b
            overflow = res > mask

        carry = overflow
        self._update_flags(res, size, carry, overflow)
        return self._to_unsigned(res, size)

    # ======================================
    # División
    # ======================================
    def div(self, a, b, size=4, signed=False):
        if b == 0:
            raise ZeroDivisionError("División por cero en ALU")

        mask, sign_bit = self._mask(size)

        if signed:
            a = self._to_signed(a, size)
            b = self._to_signed(b, size)
            res = int(a / b)
            overflow = not (-sign_bit <= res < sign_bit)
        else:
            res = a // b
            overflow = res > mask

        carry = 0
        self._update_flags(res, size, carry, overflow)
        return self._to_unsigned(res, size)


class FPU:
    def __init__(self):
        self.flags = {'C': 0, 'V': 0, 'Z': 0, 'N': 0}

    # ------------------------------------------
    # Utilidades internas
    # ------------------------------------------
    def _bits_to_float(self, bits: int, size: int):
        """Convierte entero -> float/double IEEE 754."""
        if size == 4:
            return struct.unpack('!f', struct.pack('!I', bits & 0xFFFFFFFF))[0]
        elif size == 8:
            return struct.unpack('!d', struct.pack('!Q', bits & 0xFFFFFFFFFFFFFFFF))[0]
        else:
            raise ValueError("Solo tamaños 4 o 8 bytes soportados")

    def _float_to_bits(self, value: float, size: int):
        """Convierte float/double -> entero con bits IEEE 754."""
        if size == 4:
            return struct.unpack('!I', struct.pack('!f', value))[0]
        elif size == 8:
            return struct.unpack('!Q', struct.pack('!d', value))[0]
        else:
            raise ValueError("Solo tamaños 4 o 8 bytes soportados")

    def _update_flags(self, result: float):
        """Actualiza las banderas según el resultado."""
        self.flags['C'] = 0  # Carry no aplica en FPU
        self.flags['V'] = int(math.isinf(result) or math.isnan(result))
        self.flags['Z'] = int(result == 0.0)
        # bit de signo (usa signbit para detectar -0.0 también)
        self.flags['N'] = int(math.copysign(1.0, result) < 0)

    def _check_exceptions(self, op: str, a, b=None):
        """Muestra warning si ocurre operación inválida."""
        if math.isnan(a) or (b is not None and math.isnan(b)):
            warnings.warn(f"[FPU] Operación '{op}' con NaN", RuntimeWarning)
        elif math.isinf(a) or (b is not None and math.isinf(b)):
            warnings.warn(f"[FPU] Operación '{op}' con infinito", RuntimeWarning)

    # ------------------------------------------
    # Operaciones principales
    # ------------------------------------------
    def add(self, a_bits: int, b_bits: int, size: int):
        a, b = self._bits_to_float(a_bits, size), self._bits_to_float(b_bits, size)
        self._check_exceptions('add', a, b)
        result = a + b
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def sub(self, a_bits: int, b_bits: int, size: int):
        a, b = self._bits_to_float(a_bits, size), self._bits_to_float(b_bits, size)
        self._check_exceptions('sub', a, b)
        result = a - b
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def mul(self, a_bits: int, b_bits: int, size: int):
        a, b = self._bits_to_float(a_bits, size), self._bits_to_float(b_bits, size)
        self._check_exceptions('mul', a, b)
        result = a * b
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def div(self, a_bits: int, b_bits: int, size: int):
        a, b = self._bits_to_float(a_bits, size), self._bits_to_float(b_bits, size)
        self._check_exceptions('div', a, b)
        try:
            result = a / b
        except ZeroDivisionError:
            result = float('inf') if a >= 0 else float('-inf')
            warnings.warn("[FPU] División por cero", RuntimeWarning)
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def sqrt(self, a_bits: int, size: int):
        a = self._bits_to_float(a_bits, size)
        self._check_exceptions('sqrt', a)
        if a < 0:
            warnings.warn("[FPU] Raíz cuadrada de número negativo", RuntimeWarning)
            result = float('nan')
        else:
            result = math.sqrt(a)
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def sin(self, a_bits: int, size: int):
        a = self._bits_to_float(a_bits, size)
        self._check_exceptions('sin', a)
        result = math.sin(a)
        self._update_flags(result)
        return self._float_to_bits(result, size)

    def cos(self, a_bits: int, size: int):
        a = self._bits_to_float(a_bits, size)
        self._check_exceptions('cos', a)
        result = math.cos(a)
        self._update_flags(result)
        return self._float_to_bits(result, size)


# -------------------------------------------------
# Ejemplo de uso
# -------------------------------------------------
if __name__ == "__main__":
    fpu = FPU()
    
    print(fpu.cos(1078523331,4))

    alu = ALU()

    tests = [
        ("add", 0x7F, 0x01, 1, True),   # 127 + 1 → overflow (8 bits signed)
        ("sub", 0x80, 0x01, 1, True),   # -128 - 1 → overflow
        ("mul", 0x7F, 0x02, 1, True),   # 127 * 2 → overflow
        ("mul", 0xFE, 0x02, 1, True),   # -2 * 2 = -4
        ("div", 0xFE, 0x02, 1, True),   # -2 / 2 = -1
        ("div", 0x10, 0x04, 1, False),  # 16 / 4 = 4 unsigned
    ]

    print("ALU demo (res in hex, flags C O Z N):")
    for op, a, b, size, signed in tests:
        res = getattr(alu, op)(a, b, size, signed)
        print(f"{op.upper()} {'S' if signed else 'U'} size={size} a=0x{a:02X} b=0x{b:02X} "
              f"-> res=0x{res:02X} flags={alu.flags.as_dict()}")
