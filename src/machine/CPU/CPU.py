from ast import List
from typing import Optional, Dict
from machine.Memory.Memory import Memory
from machine.IO.IOsystem import IOSystem
from machine.CPU.Register import Register
from machine.CPU.Units import ALU, FPU

MASK64 = (1 << 64) - 1

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
    def __init__(self, memory:Memory, io_sytem : IOSystem):
        self.registers: List[Register] = [Register(f"R{i}") for i in range(16)]
        self.flags: Dict[str, int] = {"Z": 0, "N": 0, "C": 0, "V": 0}
        self.memory = memory
        self.pc = 0
        self.ir = 0
        self.sp:Register = self.registers[15]
        self.running = True
        self.io = io_sytem
        self.alu = ALU()
        self.fpu = FPU()

        # mapa de opcode -> formato
        self.formats = {
            # Control
            0x0000: OP, 0x0001: OP,
            # Aritmética RR (8 bytes)
            0x0010: RR, 0x0011: RR, 0x0012: RR, 0x0013: RR, 0x0014: RR, 0x0015: RR,
            # Aritmética RI (8 bytes)
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
            0x0095: RI, 0x0096: RI, 0x0097: RI, 0x0098: RI, 0x0099: RI, # CALL
            # I/O
            0x00A0: RI, 0x00A1: RI, 0x00A2: RI, 0x00A3: OP, 0x00A4: OP,
            
            # New size-suffixed arithmetic instructions (1 byte)
            0x0100: RR, 0x0101: RR, 0x0102: RR, 0x0103: RR, 0x0104: RR, 0x0105: RR,  # ADD1, SUB1, MUL1, MULS1, DIV1, MOD1
            0x0110: RI, 0x0111: RI,  # ADDV1, SUBV1
            
            # New size-suffixed arithmetic instructions (2 bytes)
            0x0200: RR, 0x0201: RR, 0x0202: RR, 0x0203: RR, 0x0204: RR, 0x0205: RR,  # ADD2, SUB2, MUL2, MULS2, DIV2, MOD2
            0x0210: RI, 0x0211: RI,  # ADDV2, SUBV2
            
            # New size-suffixed arithmetic instructions (4 bytes)
            0x0300: RR, 0x0301: RR, 0x0302: RR, 0x0303: RR, 0x0304: RR, 0x0305: RR,  # ADD4, SUB4, MUL4, MULS4, DIV4, MOD4
            0x0310: RI, 0x0311: RI,  # ADDV4, SUBV4
            
            # New size-suffixed arithmetic instructions (8 bytes)
            0x0312: RR, 0x0313: RR, 0x0314: RR, 0x0315: RR, 0x0316: RR, 0x0319: RR,  # ADD8, SUB8, MUL8, MULS8, DIV8, MOD8
            0x0317: RI, 0x0318: RI,  # ADDV8, SUBV8,

            # New MOV instructions for different sizes
            0x0400: RR, 0x0401: RR, 0x0402: RR, 0x0403: RR,  # MOV1, MOV2, MOV4, MOV8
            0x0410: RI, 0x0411: RI, 0x0412: RI, 0x0413: RI,  # MOVV1, MOVV2, MOVV4, MOVV8
            
            # New LOAD instructions for different sizes
            0x0500: RI, 0x0501: RI, 0x0502: RI, 0x0503: RI,  # LOAD1, LOAD2, LOAD4, LOAD8
            0x0510: RR, 0x0511: RR, 0x0512: RR, 0x0513: RR,  # LOADR1, LOADR2, LOADR4, LOADR8
            
            # New STORE instructions for different sizes
            0x0600: RI, 0x0601: RI, 0x0602: RI, 0x0603: RI,  # STORE1, STORE2, STORE4, STORE8
            0x0610: RR, 0x0611: RR, 0x0612: RR, 0x0613: RR,  # STORER1, STORER2, STORER4, STORER8
            
            # FPU instructions
            0x0700: RR, 0x0701: RR, 0x0702: RR, 0x0703: RR,  # FADD4, FSUB4, FMUL4, FDIV4
            0x0710: RR, 0x0711: RR, 0x0712: RR, 0x0713: RR,  # FADD8, FSUB8, FMUL8, FDIV8
            0x0720: R, 0x0721: R, 0x0722: R, 0x0723: R,      # FSQRT4, FSQRT8, FSIN4, FCOS4
            0x0724: R, 0x0725: R,  # FSIN8, FCOS8
            0x0730: RR, 0x0731: RR, 0x0732: RR, 0x0733: RR,  # CVTF2I8, CVTI2F8, CVTF2I4, CVTI2F4

            #INTFLOAT instructions
            0x0726: R, 0x0727: R,  # INTFLOAT4, INTFLOAT8

            # Stack instructions
            0x0800: OP,  # RET (return from subroutine)
            0x0810: R, 0x0811: R, 0x0812: R, 0x0813: R,  # POP1, POP2, POP4, POP8
            0x0820: R, 0x0821: R, 0x0822: R, 0x0823: R,  # PUSH1, PUSH2, PUSH4, PUSH8
            
            # Size-specific CMP instructions
            0x0830: RR, 0x0831: RR, 0x0832: RR, 0x0833: RR,  # CMP1, CMP2, CMP4, CMP8
            0x0840: RI, 0x0841: RI, 0x0842: RI, 0x0843: RI,  # CMPV1, CMPV2, CMPV4, CMPV8
        }

    # ---------------- Helpers ----------------
    def update_ZN(self, val: int):
        self.flags["Z"] = int((val & MASK64) == 0)
        self.flags["N"] = int(((val >> 63) & 1) == 1)
        #self.update_gui()
    
    def sync_flags_from_alu(self):
        """Sync flags from ALU to CPU flags"""
        alu_flags = self.alu.flags.as_dict()
        self.flags["C"] = alu_flags["C"]
        self.flags["V"] = alu_flags["V"]  # ALU uses O for overflow, CPU uses V
        self.flags["Z"] = alu_flags["Z"]
        self.flags["N"] = alu_flags["N"]
    
    def sync_flags_from_fpu(self):
        """Sync flags from FPU to CPU flags"""
        self.flags["C"] = self.fpu.flags["C"]
        self.flags["V"] = self.fpu.flags["V"]  # FPU uses O for overflow, CPU uses V
        self.flags["Z"] = self.fpu.flags["Z"]
        self.flags["N"] = self.fpu.flags["N"]

    @staticmethod
    def unsigned_add_carry(a: int, b: int) -> int:
        return int(a + b > MASK64)

    @staticmethod
    def unsigned_sub_borrow(a: int, b: int) -> int:
        return int(a < b) ###REVISAR

    @staticmethod
    def signed_overflow_add(a: int, b: int, r: int) -> int:
        return int(((a >= 0 and b >= 0 and r < 0) or (a < 0 and b < 0 and r >= 0)))

    @staticmethod
    def signed_overflow_sub(a: int, b: int, r: int) -> int:
        return int(((a >= 0 and b < 0 and r < 0) or (a < 0 and b >= 0 and r >= 0)))

    # ---------------- Fetch / Decode / Execute ----------------
    def fetch(self) -> None:
        if self.pc + 8 > len(self.memory):
            raise IndexError(f"PC fuera de rango: {self.pc:#x}")
        # little-endian: byte bajo primero
        word = int.from_bytes(self.memory.get_bytes(self.pc,8), "little")
        self.ir = word 
        self.pc += 8
        

    def decode(self) -> Instruction:
        instr = self.ir
        opcode = (instr >> 48) & 0xFFFF
        fmt = self.formats.get(opcode, None)

        if fmt == RR:
            rd = (instr >> 4) & 0xF
            rs = instr & 0xF
            return Instruction(opcode, fmt, rd=rd, rs=rs)


        ### pasar inmediato en siguiente palabra
        elif fmt == RI:
            rd = (instr >> 44) & 0xF
            #imm = instr & MASK64
            self.fetch()
            imm = self.ir
            return Instruction(opcode, fmt, rd=rd, imm=imm)

        elif fmt == R:
            rd = (instr >> 44) & 0xF
            return Instruction(opcode, fmt, rd=rd)

        elif fmt == OP:
            return Instruction(opcode, fmt)

        else:
            raise ValueError(f"ERROR en CPU.decode: Formato desconocido para opcode {hex(opcode)}, dir {self.pc-8}, ins = {self.ir:X}")

    def execute(self, ins: Instruction):
        op = ins.opcode

        # -------- Control --------
        if op == 0x0000:  # PARAR
            self.running = False
            return
        if op == 0x0001:  # NOP
            return

        # -------- Aritmética RR --------
        if op == 0x0010:  # ADD (8 bytes)
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.add(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0011:  # SUB (8 bytes)
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.sub(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0012:  # MULS (signed, 8 bytes)
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.mul(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0013:  # MUL (unsigned, 8 bytes)
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.mul(a, b, 8, signed=False)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0014:  # DIV (8 bytes)
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            try:
                r = self.alu.div(a, b, 8, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 8)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 8)
            return
        
        if op ==  0x0015: # MOD
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = a % b
            self.registers[ins.rd].write(r, 8)
           
        # -------- Aritmética RI --------
        if op == 0x0020:  # ADDV (8 bytes)
            a, b = self.registers[ins.rd].read(8), ins.imm
            r = self.alu.add(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0021:  # SUBV (8 bytes)
            a, b = self.registers[ins.rd].read(8), ins.imm
            r = self.alu.sub(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        # -------- Inc / Dec / Clr --------
        if op == 0x0030:  # INC
            a = self.registers[ins.rd].read(8)
            r = to_uint64(a + 1)
            self.flags["C"] = self.unsigned_add_carry(a, 1)
            self.flags["V"] = self.signed_overflow_add(to_int64(a), 1, to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0031:  # DEC
            a = self.registers[ins.rd].read(8)
            r = to_uint64(a - 1)
            self.flags["C"] = self.unsigned_sub_borrow(a, 1)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), 1, to_int64(r))
            self.update_ZN(r)
            self.registers[ins.rd].write(r, 8)
            return

        if op == 0x0064:  # CLR
            self.registers[ins.rd].write(0, 8)
            self.update_ZN(0)
            self.flags["C"] = self.flags["V"] = 0
            return

        # -------- Lógicas --------
        if op == 0x0040:  # NOT
            r = to_uint64(~self.registers[ins.rd].read(8))
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0041:  # AND
            r = to_uint64(self.registers[ins.rd].read(8) & self.registers[ins.rs].read(8))
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0042:  # ANDV
            r = to_uint64(self.registers[ins.rd].read(8) & ins.imm)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0043:  # OR
            r = to_uint64(self.registers[ins.rd].read(8) | self.registers[ins.rs].read(8))
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0044:  # ORV
            r = to_uint64(self.registers[ins.rd].read(8) | ins.imm)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0045:  # XOR
            r = to_uint64(self.registers[ins.rd].read(8) ^ self.registers[ins.rs].read(8))
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0046:  # XORV
            r = to_uint64(self.registers[ins.rd].read(8) ^ ins.imm)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        # -------- Shifts --------
        if op == 0x0050:  # SHI (left)
            amt = self.registers[ins.rd].read(8) & 0x3F
            r = to_uint64(self.registers[ins.rd].read(8) << amt)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0051:  # SHD (signed right)
            amt = self.registers[ins.rd].read(8) & 0x3F
            r = to_uint64(to_int64(self.registers[ins.rd].read(8)) >> amt)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0052:  # USHI (unsigned left)
            amt = self.registers[ins.rd].read(8) & 0x3F
            r = to_uint64(self.registers[ins.rd].read(8) << amt)
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        if op == 0x0053:  # USHD (unsigned right)
            amt = self.registers[ins.rd].read(8) & 0x3F
            r = self.registers[ins.rd].read(8) >> amt
            self.registers[ins.rd].write(r, 8)
            self.update_ZN(r)
            return

        # -------- Memoria --------
        if op == 0x0060:  # LOAD R, M
            self.registers[ins.rd].write(self.memory.read(ins.imm,8), 8)
            self.update_ZN(self.registers[ins.rd].read(8))
            return

        if op == 0x0061:  # LOADV R, v
            self.registers[ins.rd].write(to_uint64(ins.imm), 8)
            self.update_ZN(self.registers[ins.rd].read(8))
            return

        if op == 0x0062:  # LOADR R, R'
            addr = self.registers[ins.rs].read(8) & MASK64
            self.registers[ins.rd].write(self.memory[addr], 8)
            self.update_ZN(self.registers[ins.rd].read(8))
            return

        if op == 0x0063:  # STOREV M, R
            self.memory.write(ins.imm,self.registers[ins.rd].read(8),8)
            return

        # -------- Comparación --------
        if op == 0x0070:  # CMP R, R'
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0071:  # CMPV R, v
            a, b = self.registers[ins.rd].read(8), ins.imm
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        # -------- Size-specific CMP Instructions --------
        if op == 0x0830:  # CMP1 Rd, Rs
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0831:  # CMP2 Rd, Rs
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0832:  # CMP4 Rd, Rs
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0833:  # CMP8 Rd, Rs
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0840:  # CMPV1 Rd, v
            a, b = self.registers[ins.rd].read(1), ins.imm & 0xFF
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0841:  # CMPV2 Rd, v
            a, b = self.registers[ins.rd].read(2), ins.imm & 0xFFFF
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0842:  # CMPV4 Rd, v
            a, b = self.registers[ins.rd].read(4), ins.imm & 0xFFFFFFFF
            r = to_uint64(a - b)
            self.update_ZN(r)
            self.flags["C"] = int(a >= b)
            self.flags["V"] = self.signed_overflow_sub(to_int64(a), to_int64(b), to_int64(r))
            return

        if op == 0x0843:  # CMPV8 Rd, v
            a, b = self.registers[ins.rd].read(8), ins.imm
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
            value = self.registers[ins.rd].read(8)
            self.io.write(ins.imm,value)
            return
        if op == 0x00A1:  # LOADIO
            value = self.io.read(ins.imm)
            self.registers[ins.rd].write(value, 8)
            self.update_ZN(self.registers[ins.rd].read(8))
            return
        if op == 0x00A2:  # SHOWIO
            self.io.show(ins.imm)
            return
    

        # -------- Size-suffixed Arithmetic Instructions (1 byte) --------
        if op == 0x0100:  # ADD1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            r = self.alu.add(a, b, 1, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return
        if op == 0x0101:  # SUB1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            r = self.alu.sub(a, b, 1, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return
        if op == 0x0102:  # MUL1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            r = self.alu.mul(a, b, 1, signed=False)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return
        if op == 0x0103:  # MULS1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            r = self.alu.mul(a, b, 1, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return
        if op == 0x0104:  # DIV1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            try:
                r = self.alu.div(a, b, 1, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 1)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 1)
            return
        if op == 0x0105:  # MOD1
            a, b = self.registers[ins.rd].read(1), self.registers[ins.rs].read(1)
            try:
                r = self.alu.mod(a, b, 1, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 1)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 1)
            return
        if op == 0x0110:  # ADDV1
            a, b = self.registers[ins.rd].read(1), ins.imm & 0xFF
            r = self.alu.add(a, b, 1, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return
        if op == 0x0111:  # SUBV1
            a, b = self.registers[ins.rd].read(1), ins.imm & 0xFF
            r = self.alu.sub(a, b, 1, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 1)
            return

        # -------- Size-suffixed Arithmetic Instructions (2 bytes) --------
        if op == 0x0200:  # ADD2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            r = self.alu.add(a, b, 2, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return
        if op == 0x0201:  # SUB2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            r = self.alu.sub(a, b, 2, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return
        if op == 0x0202:  # MUL2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            r = self.alu.mul(a, b, 2, signed=False)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return
        if op == 0x0203:  # MULS2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            r = self.alu.mul(a, b, 2, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return
        if op == 0x0204:  # DIV2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            try:
                r = self.alu.div(a, b, 2, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 2)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 2)
            return
        if op == 0x0205:  # MOD2
            a, b = self.registers[ins.rd].read(2), self.registers[ins.rs].read(2)
            try:
                r = self.alu.mod(a, b, 2, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 2)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 2)
            return
        if op == 0x0210:  # ADDV2
            a, b = self.registers[ins.rd].read(2), ins.imm & 0xFFFF
            r = self.alu.add(a, b, 2, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return
        if op == 0x0211:  # SUBV2
            a, b = self.registers[ins.rd].read(2), ins.imm & 0xFFFF
            r = self.alu.sub(a, b, 2, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 2)
            return

        # -------- Size-suffixed Arithmetic Instructions (4 bytes) --------
        if op == 0x0300:  # ADD4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.alu.add(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0301:  # SUB4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.alu.sub(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0302:  # MUL4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.alu.mul(a, b, 4, signed=False)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0303:  # MULS4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.alu.mul(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0304:  # DIV4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            try:
                r = self.alu.div(a, b, 4, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 4)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 4)
            return
        if op == 0x0305:  # MOD4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            try:
                r = self.alu.mod(a, b, 4, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 4)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 4)
            return
        if op == 0x0310:  # ADDV4
            a, b = self.registers[ins.rd].read(4), ins.imm & 0xFFFFFFFF
            r = self.alu.add(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0311:  # SUBV4
            a, b = self.registers[ins.rd].read(4), ins.imm & 0xFFFFFFFF
            r = self.alu.sub(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 4)
            return


        # -------- Size-suffixed Arithmetic Instructions (8 bytes) --------
        if op == 0x0312:  # ADD8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.add(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0313:  # SUB8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.sub(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0314:  # MUL8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.mul(a, b, 8, signed=False)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0315:  # MULS8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.alu.mul(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0316:  # DIV8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            try:
                r = self.alu.div(a, b, 8, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 8)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 8)
            return
        if op == 0x0319:  # MOD8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            try:
                r = self.alu.mod(a, b, 8, signed=True)
                self.sync_flags_from_alu()
                self.registers[ins.rd].write(r, 8)
            except ZeroDivisionError:
                self.flags["V"] = 1
                self.registers[ins.rd].write(0, 8)
            return
        if op == 0x0317:  # ADDV8
            a, b = self.registers[ins.rd].read(8), ins.imm & 0xFFFFFFFF
            r = self.alu.add(a, b, 4, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0318:  # SUBV8
            a, b = self.registers[ins.rd].read(8), ins.imm & 0xFFFFFFFF
            r = self.alu.sub(a, b, 8, signed=True)
            self.sync_flags_from_alu()
            self.registers[ins.rd].write(r, 8)
            return

        # -------- MOV Instructions --------
        if op == 0x0400:  # MOV1
            self.registers[ins.rd].write(self.registers[ins.rs].read(1), 1)
            return
        if op == 0x0401:  # MOV2
            self.registers[ins.rd].write(self.registers[ins.rs].read(2), 2)
            return
        if op == 0x0402:  # MOV4
            self.registers[ins.rd].write(self.registers[ins.rs].read(4), 4)
            return
        if op == 0x0403:  # MOV8
            self.registers[ins.rd].write(self.registers[ins.rs].read(8), 8)
            return
        if op == 0x0410:  # MOVV1
            self.registers[ins.rd].write(ins.imm & 0xFF, 1)
            return
        if op == 0x0411:  # MOVV2
            self.registers[ins.rd].write(ins.imm & 0xFFFF, 2)
            return
        if op == 0x0412:  # MOVV4
            self.registers[ins.rd].write(ins.imm & 0xFFFFFFFF, 4)
            return
        if op == 0x0413:  # MOVV8
            self.registers[ins.rd].write(ins.imm, 8)
            return

        # -------- LOAD Instructions --------
        if op == 0x0500:  # LOAD1
            self.registers[ins.rd].write(self.memory.read(ins.imm, 1), 1)
            return
        if op == 0x0501:  # LOAD2
            self.registers[ins.rd].write(self.memory.read(ins.imm, 2), 2)
            return
        if op == 0x0502:  # LOAD4
            self.registers[ins.rd].write(self.memory.read(ins.imm, 4), 4)
            return
        if op == 0x0503:  # LOAD8
            self.registers[ins.rd].write(self.memory.read(ins.imm, 8), 8)
            return
        if op == 0x0510:  # LOADR1
            addr = self.registers[ins.rs].read(8) & MASK64
            self.registers[ins.rd].write(self.memory.read(addr, 1), 1)
            return
        if op == 0x0511:  # LOADR2
            addr = self.registers[ins.rs].read(8) & MASK64
            self.registers[ins.rd].write(self.memory.read(addr, 2), 2)
            return
        if op == 0x0512:  # LOADR4
            addr = self.registers[ins.rs].read(8) & MASK64
            self.registers[ins.rd].write(self.memory.read(addr, 4), 4)
            return
        if op == 0x0513:  # LOADR8
            addr = self.registers[ins.rs].read(8) & MASK64
            value = self.memory.read(addr, 8)
            self.registers[ins.rd].write(value, 8)
            return

        # -------- STORE Instructions --------
        if op == 0x0600:  # STORE1
            self.memory.write(ins.imm, self.registers[ins.rd].read(1), 1)
            return
        if op == 0x0601:  # STORE2
            self.memory.write(ins.imm, self.registers[ins.rd].read(2), 2)
            return
        if op == 0x0602:  # STORE4
            self.memory.write(ins.imm, self.registers[ins.rd].read(4), 4)
            return
        if op == 0x0603:  # STORE8
            self.memory.write(ins.imm, self.registers[ins.rd].read(8), 8)
            return
        if op == 0x0610:  # STORER1
            addr = self.registers[ins.rs].read(8) & MASK64
            self.memory.write(addr, self.registers[ins.rd].read(1), 1)
            return
        if op == 0x0611:  # STORER2
            addr = self.registers[ins.rs].read(8) & MASK64
            self.memory.write(addr, self.registers[ins.rd].read(2), 2)
            return
        if op == 0x0612:  # STORER4
            addr = self.registers[ins.rs].read(8) & MASK64
            self.memory.write(addr, self.registers[ins.rd].read(4), 4)
            return
        if op == 0x0613:  # STORER8
            addr = self.registers[ins.rs].read(8) & MASK64
            self.memory.write(addr, self.registers[ins.rd].read(8), 8)
            return

        # -------- FPU Instructions --------
        if op == 0x0700:  # FADD4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.fpu.add(a, b, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0701:  # FSUB4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.fpu.sub(a, b, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0702:  # FMUL4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.fpu.mul(a, b, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0703:  # FDIV4
            a, b = self.registers[ins.rd].read(4), self.registers[ins.rs].read(4)
            r = self.fpu.div(a, b, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0710:  # FADD8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.fpu.add(a, b, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0711:  # FSUB8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.fpu.sub(a, b, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0712:  # FMUL8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.fpu.mul(a, b, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0713:  # FDIV8
            a, b = self.registers[ins.rd].read(8), self.registers[ins.rs].read(8)
            r = self.fpu.div(a, b, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0720:  # FSQRT4
            a = self.registers[ins.rd].read(4)
            r = self.fpu.sqrt(a, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0721:  # FSQRT8
            a = self.registers[ins.rd].read(8)
            r = self.fpu.sqrt(a, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0722:  # FSIN4
            a = self.registers[ins.rd].read(4)
            r = self.fpu.sin(a, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0723:  # FCOS4
            a = self.registers[ins.rd].read(4)
            r = self.fpu.cos(a, 4)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 4)
            return
        if op == 0x0724:  # FSIN8
            a = self.registers[ins.rd].read(8)
            r = self.fpu.sin(a, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        if op == 0x0725:  # FCOS8
            a = self.registers[ins.rd].read(8)
            r = self.fpu.cos(a, 8)
            self.sync_flags_from_fpu()
            self.registers[ins.rd].write(r, 8)
            return
        
        # -------- Conversiones FPU --------
        if op == 0x0730:  # CVTF2I8 (float64 -> int64)
            float_bits = self.registers[ins.rs].read(8)
            float_val = self.fpu._bits_to_float(float_bits, 8)
            int_val = int(float_val)  # Truncar a entero
            # Ajustar para complemento a 2 si es necesario
            if int_val < 0:
                int_val = (1 << 64) + int_val
            self.registers[ins.rd].write(int_val, 8)
            return
        
        if op == 0x0731:  # CVTI2F8 (int64 -> float64)
            int_bits = self.registers[ins.rs].read(8)
            # Convertir de complemento a 2 si es negativo
            if int_bits & (1 << 63):
                int_val = int_bits - (1 << 64)
            else:
                int_val = int_bits
            float_val = float(int_val)
            float_bits = self.fpu._float_to_bits(float_val, 8)
            self.registers[ins.rd].write(float_bits, 8)
            return
        
        if op == 0x0732:  # CVTF2I4 (float32 -> int32)
            float_bits = self.registers[ins.rs].read(4)
            float_val = self.fpu._bits_to_float(float_bits, 4)
            int_val = int(float_val)
            if int_val < 0:
                int_val = (1 << 32) + int_val
            self.registers[ins.rd].write(int_val, 4)
            return
        
        if op == 0x0733:  # CVTI2F4 (int32 -> float32)
            int_bits = self.registers[ins.rs].read(4)
            if int_bits & (1 << 31):
                int_val = int_bits - (1 << 32)
            else:
                int_val = int_bits
            float_val = float(int_val)
            float_bits = self.fpu._float_to_bits(float_val, 4)
            self.registers[ins.rd].write(float_bits, 4)
            return


        # -------- Stack Instructions --------
        if op == 0x0099:  # CALL (call subroutine)
            # Push return address to stack (8 bytes)
            if self.sp.value + 8 > len(self.memory):
                raise IndexError("Stack overflow: cannot push return address")
            self.memory.write(self.sp.value, self.pc, 8)
            self.sp.value += 8
            self.pc = ins.imm & MASK64
            return

        if op == 0x0800:  # RET (return from subroutine)
            # Pop return address from stack (8 bytes)
            if self.sp.value < 8:
                raise IndexError("Stack underflow: cannot pop return address")
            return_addr = self.memory.read(self.sp.value - 8, 8)
            self.sp.value -= 8
            self.pc = return_addr & MASK64
            return

        if op == 0x0810:  # POP1
            if self.sp.value < 1:
                raise IndexError("Stack underflow: cannot pop 1 byte")
            value = self.memory.read(self.sp.value - 1, 1)
            self.sp.value -= 1
            self.registers[ins.rd].write(value, 1)
            self.update_ZN(value)
            return

        if op == 0x0811:  # POP2
            if self.sp.value < 2:
                raise IndexError("Stack underflow: cannot pop 2 bytes")
            value = self.memory.read(self.sp.value - 2, 2)
            self.sp.value -= 2
            self.registers[ins.rd].write(value, 2)
            self.update_ZN(value)
            return

        if op == 0x0812:  # POP4
            if self.sp.value < 4:
                raise IndexError("Stack underflow: cannot pop 4 bytes")
            value = self.memory.read(self.sp.value - 4, 4)
            self.sp.value -= 4
            self.registers[ins.rd].write(value, 4)
            self.update_ZN(value)
            return

        if op == 0x0813:  # POP8
            if self.sp.value < 8:
                raise IndexError("Stack underflow: cannot pop 8 bytes")
            value = self.memory.read(self.sp.value - 8, 8)
            self.sp.value -= 8
            self.registers[ins.rd].write(value, 8)
            self.update_ZN(value)
            return

        if op == 0x0820:  # PUSH1
            value = self.registers[ins.rd].read(1)
            if self.sp.value + 1 > len(self.memory):
                raise IndexError("Stack overflow: cannot push 1 byte")
            self.memory.write(self.sp.value, value, 1)
            self.sp.value += 1
            return

        if op == 0x0821:  # PUSH2
            value = self.registers[ins.rd].read(2)
            if self.sp.value + 2 > len(self.memory):
                raise IndexError("Stack overflow: cannot push 2 bytes")
            self.memory.write(self.sp.value, value, 2)
            self.sp.value += 2
            return

        if op == 0x0822:  # PUSH4
            value = self.registers[ins.rd].read(4)
            if self.sp.value + 4 > len(self.memory):
                raise IndexError("Stack overflow: cannot push 4 bytes")
            self.memory.write(self.sp.value, value, 4)
            self.sp.value += 4
            return

        if op == 0x0823:  # PUSH8
            value = self.registers[ins.rd].read(8)
            if self.sp.value + 8 > len(self.memory):
                raise IndexError("Stack overflow: cannot push 8 bytes")
            self.memory.write(self.sp.value, value, 8)
            self.sp.value += 8
            return

    def tick(self):
        """ Emulates excecution of one instrucction
        """
        self.fetch()
        ins = self.decode()
        self.execute(ins)


    # ---------------- Main Loop ----------------
    def run(self, max_cycles=10_000_000_000):
        self.running = 1
        cycles = 0
      
        while self.running and cycles < max_cycles:
            self.tick()
            cycles += 1
        if cycles >= max_cycles:
            raise RuntimeError("Max cycles reached")
        
    def set_pc(self,pc):
        self.pc = pc

    def set_sp(self, value):
        self.sp.write(value,8)

    def dump_state(self):
        print("=== ESTADO DEL CPU ===")
        print("PC:", self.pc)
        print("SP:", self.sp.read(8))
        for i, reg in enumerate(self.registers):
            v = reg.read(8)
            print(f"R{i:02d}: {v:#018x} ({to_int64(v)})")
        print("FLAGS:", self.flags)


if __name__ == "__main__":
    memoria = Memory(1024)
    cpu = CPU(memoria)
    program = []

    print("=== Testing Refactored CPU with ALU/FPU ===")
    
    # Test 1: Original program (sum of first n integers)
    print("\n1. Testing original program (sum of first 5 integers):")
    # R1 = n 
    program.append((0x0061 << 48) | (0x1 << 44) | 5) #n= 5
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

    for i, ins in enumerate(program):
        memoria.write64(i*8,ins)

    cpu.run()
    cpu.dump_state()
    
    # Test 2: New size-suffixed instructions
    print("\n2. Testing new size-suffixed instructions:")
    memoria2 = Memory(1024)
    cpu2 = CPU(memoria2)
    program2 = []
    
    # Test MOVV1 (move 1-byte value)
    program2.append((0x0410 << 48) | (0x1 << 44) | 0xFF)  # MOVV1 R1, 0xFF
    # Test ADD1 (add 1-byte values)
    program2.append((0x0100 << 48) | (0x1 << 4) | 0x1)    # ADD1 R1, R1
    # Test MOVV2 (move 2-byte value)
    program2.append((0x0411 << 48) | (0x2 << 44) | 0x1234)  # MOVV2 R2, 0x1234
    # Test ADD2 (add 2-byte values)
    program2.append((0x0200 << 48) | (0x2 << 4) | 0x2)    # ADD2 R2, R2
    # Test MOVV4 (move 4-byte value)
    program2.append((0x0412 << 48) | (0x3 << 44) | 0x12345678)  # MOVV4 R3, 0x12345678
    # Test ADD4 (add 4-byte values)
    program2.append((0x0300 << 48) | (0x3 << 4) | 0x3)    # ADD4 R3, R3
    # PARAR
    program2.append((0x0000 << 48))
    
    for i, ins in enumerate(program2):
        memoria2.write64(i*8,ins)
    
    cpu2.run()
    cpu2.dump_state()
    
    # Test 3: FPU instructions (COS and SIN)
    print("\n3. Testing FPU instructions (COS and SIN):")
    memoria3 = Memory(1024)
    cpu3 = CPU(memoria3)
    program3 = []
    
    # Load a float value (π/4) into R1 using IEEE 754 representation
    import struct
    pi_over_4 = 3.14159265359 / 4
    pi_over_4_bits = struct.unpack('!I', struct.pack('!f', pi_over_4))[0]
    
    # MOVV4 R1, π/4 (as IEEE 754 bits)
    program3.append((0x0412 << 48) | (0x1 << 44) | pi_over_4_bits)
    # FCOS4 R1 (cosine of R1)
    program3.append((0x0723 << 48) | (0x1 << 44))
    # MOVV4 R2, π/4 (as IEEE 754 bits)
    program3.append((0x0412 << 48) | (0x2 << 44) | pi_over_4_bits)
    # FSIN4 R2 (sine of R2)
    program3.append((0x0722 << 48) | (0x2 << 44))
    # PARAR
    program3.append((0x0000 << 48))
    
    for i, ins in enumerate(program3):
        memoria3.write64(i*8,ins)
    
    cpu3.run()
    cpu3.dump_state()
    
    # Test 4: Stack instructions (PUSH/POP/RET)
    print("\n4. Testing Stack instructions (PUSH/POP/RET):")
    memoria4 = Memory(1024)
    cpu4 = CPU(memoria4)
    program4 = []
    
    # Initialize stack pointer to end of memory (grows downward)
    cpu4.sp = 1024
    
    # Test PUSH8 and POP8
    program4.append((0x0413 << 48) | (0x1 << 44) | 0x123456789ABCDEF0)  # MOVV8 R1, 0x123456789ABCDEF0
    program4.append((0x0823 << 48) | (0x1 << 44))  # PUSH8 R1
    program4.append((0x0813 << 48) | (0x2 << 44))  # POP8 R2
    
    # Test PUSH4 and POP4
    program4.append((0x0412 << 48) | (0x3 << 44) | 0x12345678)  # MOVV4 R3, 0x12345678
    program4.append((0x0822 << 48) | (0x3 << 44))  # PUSH4 R3
    program4.append((0x0812 << 48) | (0x4 << 44))  # POP4 R4
    
    # Test PUSH2 and POP2
    program4.append((0x0411 << 48) | (0x5 << 44) | 0x1234)  # MOVV2 R5, 0x1234
    program4.append((0x0821 << 48) | (0x5 << 44))  # PUSH2 R5
    program4.append((0x0811 << 48) | (0x6 << 44))  # POP2 R6
    
    # Test PUSH1 and POP1
    program4.append((0x0410 << 48) | (0x7 << 44) | 0xAB)  # MOVV1 R7, 0xAB
    program4.append((0x0820 << 48) | (0x7 << 44))  # PUSH1 R7
    program4.append((0x0810 << 48) | (0x8 << 44))  # POP1 R8
    
    # Show results
    program4.append((0x00A0 << 48) | (0x2 << 44) | 0x700)  # SVIO R2, 0x700 (POP8 result)
    program4.append((0x00A2 << 48) | (0x0 << 44) | 0x700)  # SHOWIO 0x700
    program4.append((0x00A0 << 48) | (0x4 << 44) | 0x701)  # SVIO R4, 0x701 (POP4 result)
    program4.append((0x00A2 << 48) | (0x0 << 44) | 0x701)  # SHOWIO 0x701
    program4.append((0x00A0 << 48) | (0x6 << 44) | 0x702)  # SVIO R6, 0x702 (POP2 result)
    program4.append((0x00A2 << 48) | (0x0 << 44) | 0x702)  # SHOWIO 0x702
    program4.append((0x00A0 << 48) | (0x8 << 44) | 0x703)  # SVIO R8, 0x703 (POP1 result)
    program4.append((0x00A2 << 48) | (0x0 << 44) | 0x703)  # SHOWIO 0x703
    
    # PARAR
    program4.append((0x0000 << 48))
    
    for i, ins in enumerate(program4):
        memoria4.write64(i*8,ins)
    
    cpu4.run()
    cpu4.dump_state()
    
    print("\n=== All tests completed ===")
