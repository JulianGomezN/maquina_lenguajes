from typing import Optional, Dict
from loader import Loader

MASK64 = (1 << 64) - 1
MASK44 = (1 << 44) - 1

# Formatos 
RR = 1
RI = 2
R = 3
OP = 4

def to_uint64(x: int) -> int:
    return x & MASK64

def to_int64(x: int) -> int:
    x &= MASK64
    if x >> 63: #checkar negativo
        return x - (1 << 64)
    return x

class Instruction:
    def __init__(self, opcode: int, fmt: str,
                 rd: Optional[int] = None,
                 rs: Optional[int] = None,
                 imm: Optional[int] = None):
        self.opcode = opcode
        self.fmt = fmt
        self.rd = rd
        self.rs = rs
        self.imm = imm

    def __repr__(self):
        return (f"<Instr op={self.opcode:#06x} fmt={self.fmt} "
                f"rd={self.rd} rs={self.rs} imm={self.imm}>")

class CPU:
    def __init__(self, mem_size=25000, gui=None):
        self.registers = [0] * 16
        self.flags: Dict[str, int] = {"Z": 0, "N": 0, "C": 0, "V": 0}
        self.memory = [0] * mem_size
        self.pc = 0
        self.running = True
        self.io_map: Dict[int, int] = {}
        self.gui = gui  # Referencia a la GUI para actualizada
        
        # Inicializar el cargador
        self.loader = Loader(self)

        # mapa de opcode -> formato
        self.formats = {
            # Control
            0x0000: OP, 0x0001: OP,
            # Aritmética RR
            0x0010: RR, 0x0011: RR, 0x0012: RR, 0x0013: RR, 0x0014: RR,
            # Aritmética RI
            0x0020: RI, 0x0021: RI,
            # R (inc/dec/clear)
            0x0030: R, 0x0031: R,
            # Lógicas
            0x0040: R, 0x0041: RR, 0x0042: RI, 0x0043: RR,
            0x0044: RI, 0x0045: RR, 0x0046: RI,
            # Shifts
            0x0050: R, 0x0051: R, 0x0052: R, 0x0053: R,
            # Memoria
            0x0060: RI, 0x0061: RI, 0x0062: RR, 0x0063: RI, 0x0064: R,
            # Comparación
            0x0070: RR, 0x0071: RI,
            # Flags
            0x0080: OP, 0x0081: OP, 0x0082: OP, 0x0083: OP,
            0x0084: OP, 0x0085: OP, 0x0086: OP, 0x0087: OP,
            # Jumps
            0x0090: RI, 0x0091: RI, 0x0092: RI, 0x0093: RI, 0x0094: RI,
            0x0095: RI, 0x0096: RI, 0x0097: RI, 0x0098: RI,
            # I/O
            0x00A0: RI, 0x00A1: RI, 0x00A2: RI, 0x00A3: OP, 0x00A4: OP,
        }

    # ---------------- Helpers ----------------
    def update_ZN(self, val: int):
        self.flags["Z"] = int((val & MASK64) == 0)
        self.flags["N"] = int(((val >> 63) & 1) == 1)
        self.update_gui()

    @staticmethod
    def unsigned_add_carry(a: int, b: int) -> int:
        return int(a + b > MASK64)

    @staticmethod
    def unsigned_sub_borrow(a: int, b: int) -> int:
        return int(a >= b)

    @staticmethod
    def signed_overflow_add(a: int, b: int, r: int) -> int:
        return int(((a >= 0 and b >= 0 and r < 0) or (a < 0 and b < 0 and r >= 0)))

    @staticmethod
    def signed_overflow_sub(a: int, b: int, r: int) -> int:
        return int(((a >= 0 and b < 0 and r < 0) or (a < 0 and b >= 0 and r >= 0)))

    # ---------------- Fetch / Decode / Execute ----------------
    def fetch(self) -> int:
        if self.pc + 8 > len(self.memory):
            raise IndexError(f"PC fuera de rango: {self.pc:#x}")
        # little-endian: byte bajo primero
        word = int.from_bytes(self.memory[self.pc:self.pc+8], "little")
        self.pc += 8
        return word

    def decode(self, instr: int) -> Instruction:
        opcode = (instr >> 48) & 0xFFFF
        fmt = self.formats.get(opcode, None)

        if fmt == RR:
            rd = (instr >> 4) & 0xF
            rs = instr & 0xF
            return Instruction(opcode, fmt, rd=rd, rs=rs)

        elif fmt == RI:
            rd = (instr >> 44) & 0xF
            imm = instr & MASK44
            return Instruction(opcode, fmt, rd=rd, imm=imm)

        elif fmt == R:
            rd = (instr >> 44) & 0xF
            return Instruction(opcode, fmt, rd=rd)

        elif fmt == OP:
            return Instruction(opcode, fmt)

        else:
            raise ValueError(f"Formato desconocido para opcode {hex(opcode)}")

    def execute(self, ins: Instruction):
        op = ins.opcode

        # -------- Control --------
        if op == 0x0000:  # PARAR
            self.running = False
            return
        if op == 0x0001:  # NOP
            return

        # -------- Aritmética RR --------
        if op == 0x0010:  # ADD
            a, b = self.registers[ins.rd], self.registers[ins.rs]
            r = to_uint64(a + b)
            self.flags["C"] = self.unsigned_add_carry(a, b)
            self.flags["V"] = self.signed_overflow_add(to_int64(a), to_int64(b), to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0011:  # SUB
            a, b = self.registers[ins.rd], self.registers[ins.rs]
            r = to_uint64(a - b)
            self.flags["C"] = self.unsigned_sub_borrow(a, b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0012:  # MULS (signed)
            a, b = to_int64(self.registers[ins.rd]), to_int64(self.registers[ins.rs])
            res = a * b
            r = to_uint64(res)
            self.flags["V"] = int(not (-(1 << 63) <= res < (1 << 63)))
            self.flags["C"] = int((res & ~MASK64) != 0)
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0013:  # MUL (unsigned)
            a, b = self.registers[ins.rd], self.registers[ins.rs]
            res = a * b
            r = to_uint64(res)
            self.flags["C"] = int((res & ~MASK64) != 0)
            self.flags["V"] = 0
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0014:  # DIV
            a, b = self.registers[ins.rd], self.registers[ins.rs]
            if b == 0:
                self.flags["V"] = 1
                self.registers[ins.rd] = 0
            else:
                q = a // b
                self.registers[ins.rd] = to_uint64(q)
                self.flags["V"] = 0
            self.update_ZN(self.registers[ins.rd])
            return

        # -------- Aritmética RI --------
        if op == 0x0020:  # ADDV
            a, b = self.registers[ins.rd], ins.imm
            r = to_uint64(a + b)
            self.flags["C"] = self.unsigned_add_carry(a, b)
            self.flags["V"] = self.signed_overflow_add(to_int64(a), to_int64(b), to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0021:  # SUBV
            a, b = self.registers[ins.rd], ins.imm
            r = to_uint64(a - b)
            self.flags["C"] = self.unsigned_sub_borrow(a, b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        # -------- Inc / Dec / Clr --------
        if op == 0x0030:  # INC
            a = self.registers[ins.rd]
            r = to_uint64(a + 1)
            self.flags["C"] = self.unsigned_add_carry(a, 1)
            self.flags["V"] = self.signed_overflow_add(to_int64(a), 1, to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0031:  # DEC
            a = self.registers[ins.rd]
            r = to_uint64(a - 1)
            self.flags["C"] = self.unsigned_sub_borrow(a, 1)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), 1, to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd] = r
            return

        if op == 0x0064:  # CLR
            self.registers[ins.rd] = 0
            self.update_ZN(0)
            self.flags["C"] = self.flags["V"] = 0
            return

        # -------- Lógicas --------
        if op == 0x0040:  # NOT
            r = to_uint64(~self.registers[ins.rd])
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0041:  # AND
            r = to_uint64(self.registers[ins.rd] & self.registers[ins.rs])
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0042:  # ANDV
            r = to_uint64(self.registers[ins.rd] & ins.imm)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0043:  # OR
            r = to_uint64(self.registers[ins.rd] | self.registers[ins.rs])
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0044:  # ORV
            r = to_uint64(self.registers[ins.rd] | ins.imm)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0045:  # XOR
            r = to_uint64(self.registers[ins.rd] ^ self.registers[ins.rs])
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0046:  # XORV
            r = to_uint64(self.registers[ins.rd] ^ ins.imm)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        # -------- Shifts --------
        if op == 0x0050:  # SHI (left)
            amt = self.registers[ins.rd] & 0x3F
            r = to_uint64(self.registers[ins.rd] << amt)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0051:  # SHD (signed right)
            amt = self.registers[ins.rd] & 0x3F
            r = to_uint64(to_int64(self.registers[ins.rd]) >> amt)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0052:  # USHI (unsigned left)
            amt = self.registers[ins.rd] & 0x3F
            r = to_uint64(self.registers[ins.rd] << amt)
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        if op == 0x0053:  # USHD (unsigned right)
            amt = self.registers[ins.rd] & 0x3F
            r = self.registers[ins.rd] >> amt
            self.registers[ins.rd] = r
            self.update_ZN(r)
            return

        # -------- Memoria --------
        if op == 0x0060:  # LOAD R, M
            self.registers[ins.rd] = self.memory[ins.imm]
            self.update_ZN(self.registers[ins.rd])
            return

        if op == 0x0061:  # LOADV R, v
            self.registers[ins.rd] = to_uint64(ins.imm)
            self.update_ZN(self.registers[ins.rd])
            return

        if op == 0x0062:  # LOADR R, R'
            addr = self.registers[ins.rs] & MASK44
            self.registers[ins.rd] = self.memory[addr]
            self.update_ZN(self.registers[ins.rd])
            return

        if op == 0x0063:  # SV M, R
            self.memory[ins.imm] = self.registers[ins.rd]
            return

        # -------- Comparación --------
        if op == 0x0070:  # CMP R, R'
            a, b = self.registers[ins.rd], self.registers[ins.rs]
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0071:  # CMPV R, v
            a, b = self.registers[ins.rd], ins.imm
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        # -------- Flags manip --------
        if op == 0x0080: self.flags["Z"] = 0; return
        if op == 0x0081: self.flags["Z"] = 1; return
        if op == 0x0082: self.flags["N"] = 0; return
        if op == 0x0083: self.flags["N"] = 1; return
        if op == 0x0084: self.flags["C"] = 0; return
        if op == 0x0085: self.flags["C"] = 1; return
        if op == 0x0086: self.flags["V"] = 0; return
        if op == 0x0087: self.flags["V"] = 1; return

        # -------- Saltos --------
        if 0x0090 <= op <= 0x0098:
            imm = ins.imm
            take = False
            if op == 0x0090: take = True
            elif op == 0x0091: take = self.flags["Z"] == 1
            elif op == 0x0092: take = self.flags["Z"] == 0
            elif op == 0x0093: take = self.flags["N"] == 1
            elif op == 0x0094: take = self.flags["N"] == 0
            elif op == 0x0095: take = self.flags["C"] == 1
            elif op == 0x0096: take = self.flags["C"] == 0
            elif op == 0x0097: take = (self.flags["V"] ^ self.flags["N"]) == 1
            elif op == 0x0098: take = (self.flags["V"] ^ self.flags["N"]) == 0
            if take: 
                self.pc = imm
            return

        # -------- I/O --------
        if op == 0x00A0:  # SVIO
            self.io_map[ins.imm] = self.registers[ins.rd]
            return
        if op == 0x00A1:  # LOADIO
            self.registers[ins.rd] = self.io_map.get(ins.imm, 0)
            self.update_ZN(self.registers[ins.rd])
            return
        if op == 0x00A2:  # SHOWIO
            output_text = f"[IO {ins.imm:#x}] = {self.io_map.get(ins.imm, 0)}"
            print(output_text)
            if self.gui:
                self.gui.append_salida(output_text)
            return
        if op in (0x00A3, 0x00A4):
            self.io_map.clear()
            return

        raise ValueError(f"Opcode {op:#06x} no implementado")

    def update_gui(self):
        """Actualiza la GUI con el estado actual del CPU"""
        if self.gui:
            # Actualizar registros
            for i in range(16):
                self.gui.set_registro(f"R{i:02}", self.registers[i])
            
            # Actualizar flags
            self.gui.set_flag("Z (Zero)", self.flags["Z"])
            self.gui.set_flag("N (Negative)", self.flags["N"])
            self.gui.set_flag("C (Carry)", self.flags["C"])
            self.gui.set_flag("V (Overflow)", self.flags["V"])
            self.gui.set_flag("PC (Program Counter)", self.pc)

    # ---------------- Main Loop ----------------
    def run(self, max_cycles=1_000_000_000, step_mode=False):
        cycles = 0
      
        while self.running and cycles < max_cycles:
            raw = self.fetch()
            ins = self.decode(raw)
            self.execute(ins)
            cycles += 1
            
        if cycles >= max_cycles:
            raise RuntimeError("Max cycles reached")
        
        # Actualizar GUI al final de la ejecución
        if self.gui:
            self.update_gui()
      
    def load_program(self, program, start=0, program_name="main"):
        """
        Carga un programa usando el cargador
        
        Args:
            program: Lista de instrucciones binarias
            start: Dirección de inicio (0 por defecto)
            program_name: Nombre del programa
        """
        try:
            # Usar el cargador para cargar el programa
            program_info = self.loader.load_program(
                program, 
                start_address=start, 
                program_name=program_name
            )
            
            # Establecer PC al inicio del programa
            self.pc = program_info['start_address']
            
            # Si hay GUI, mostrar información de carga
            if self.gui:
                message = f"Programa '{program_name}' cargado en 0x{program_info['start_address']:04x}"
                # self.gui.append_salida(message)  # Comentado para no saturar la salida
            
            return program_info
            
        except Exception as e:
            if self.gui:
                self.gui.append_salida(f"Error al cargar programa: {str(e)}")
            raise

    def load_program_legacy(self, program, start=0):
        """
        Método legacy para compatibilidad con código existente
        DEPRECATED: Usar load_program() en su lugar
        """
        # Método anterior para compatibilidad
        for i, instr in enumerate(program):
            # convert intruction 64 bits to 8 bytes little-endian to load into memory
            bytes_instr = to_uint64(instr).to_bytes(8, "little")
            offset = start + (i * 8)
            self.memory[offset:offset+8] = bytes_instr
        self.pc = start

    def get_loader_info(self):
        """Obtiene información del cargador"""
        return self.loader.get_memory_map()
    
    def list_loaded_programs(self):
        """Lista programas cargados"""
        return self.loader.list_loaded_programs()
    
    def unload_program(self, program_name):
        """Descarga un programa"""
        return self.loader.unload_program(program_name)

    def dump_state(self):
        print("=== ESTADO DEL CPU ===")
        print("PC:", self.pc)
        for i, v in enumerate(self.registers):
            print(f"R{i:02d}: {v:#018x} ({to_int64(v)})")
        print("FLAGS:", self.flags)
        print("IO:", self.io_map)
        
        print("\n=== ESTADO DEL CARGADOR ===")
        self.loader.dump_memory_state()


if __name__ == "__main__":
    cpu = CPU()
    program = []

    #Sumar los primeros n enteros usando un ciclo
    # R1 = n 
    program.append((0x0061 << 48) | (0x1 << 44) | int(1e13)) #n= 5
    # R2 = 0 (acumulador)
    program.append((0x0064 << 48) | (0x2 << 44))

    loop_addr = 2*8  # dirección del inicio del bucle

    # loop:
    # ADD R2, R1
    program.append((0x0010 << 48) | (0x2 << 4) | 0x1)

    # DEC R1
    program.append((0x0031 << 48) | (0x1 << 44))

    # CMP R1, 0
    program.append((0x0071 << 48) | (0x1 << 44) | 0)
    # JNE loop
    program.append((0x0092 << 48) | (0x0 << 44) | loop_addr)

    # fin:
    # SVIO R2 → IO[0x30]
    program.append((0x00A0 << 48) | (0x2 << 44) | 0x30)
    # SHOWIO 0x30
    program.append((0x00A2 << 48) | (0x0 << 44) | 0x30)
    # PARAR
    program.append((0x0000 << 48))

    cpu.load_program(program, start=0x00)
    cpu.run()
    cpu.dump_state()
