from GUI.GUI import SimuladorGUI
from machine.Memory.Memory import Memory
from machine.CPU.CPU import CPU
from machine.IO.Devices import Screen,Keyboard
from machine.IO.IOsystem import IOSystem
import os
import logging

# Usar una ruta explícita para evitar archivos duplicados de RAM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAM_FILE = os.path.join(BASE_DIR, "memory_ram.txt")

logging.basicConfig(level=logging.WARNING)
# Keep loader .DATA init messages visible
logging.getLogger("compiler.loader").setLevel(logging.INFO)
# Keep CPU variable-store messages visible
logging.getLogger("machine.cpu").setLevel(logging.INFO)
# By default keep debug logging hidden. To see detailed memory/CPU traces set logging to DEBUG.
# Memory size increased from 2**16 (64KB) to 2**17 (128KB) to support larger programs and additional features that require more RAM.
mem = Memory(2**17, memory_file=RAM_FILE, debug_writes=False, debug_stack_writes=False)

io = IOSystem()

screen = Screen()
keyboard = Keyboard()

io.register(0x100,screen)
io.register(0x200,keyboard)

# ### Esto emula el input falta implementarlo en la GUI
# s = "Hello World!"
# for i in s:
#     keyboard.write(ord(i))
# keyboard.write(0)

cpu = CPU(mem,io)
app = SimuladorGUI(cpu,screen,keyboard)

app.mainloop()