from GUI.GUI import SimuladorGUI
from machine.Memory.Memory import Memory
from machine.CPU.CPU import CPU
from machine.IO.Devices import Screen,Keyboard
from machine.IO.IOsystem import IOSystem
import os

# Usar una ruta explícita para evitar archivos duplicados de RAM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAM_FILE = os.path.join(BASE_DIR, "memory_ram.txt")

mem = Memory(2**16, memory_file=RAM_FILE)

io = IOSystem()


screen = Screen()
keyboard = Keyboard()


io.register(0x100,screen)
io.register(0x200,keyboard)

### Esto emula el input falta implementarlo en la GUI
s = "Hello World!"
for i in s:
    keyboard.write(ord(i))
keyboard.write(0)



cpu = CPU(mem,io)
app = SimuladorGUI(cpu)

app.mainloop()