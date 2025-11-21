""" Test a assembly program + Linker + Loader
"""

from logic.Memory import Memory
from logic.CPU import CPU
from logic.io.Devices import Screen,Keyboard
from logic.io.IOsystem import IOSystem

from compiler.ensamblador import Ensamblador
from compiler.Loader import Loader

mem = Memory(2**16)


screen = Screen()
keyboard = Keyboard()

io = IOSystem()
io.register(0x100,screen)
io.register(0x200,keyboard)

s = "Hello World"
for i in s:
    keyboard.write(ord(i))
keyboard.write(0)

cpu = CPU(mem,io)

if __name__ == '__main__':
    import sys
    source = sys.stdin.read()
    
    ens = Ensamblador()
    codigo_relativo = ens.assemble(source)
    print("ENSAMBLADO: (relativo)")

    print(codigo_relativo)

    loader = Loader(mem)
    loader.load_in_memory(codigo_relativo,0)

    cpu.set_pc(0)
    cpu.set_sp(mem.size//2)
    cpu.run()
    cpu.dump_state()

    print("Salida: ")
    print(screen.buffer)