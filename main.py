from GUI.GUI import SimuladorGUI
from logic.Memory import Memory
from logic.CPU import CPU
from logic.io.Devices import Screen,Keyboard
from logic.io.IOsystem import IOSystem
import os

# Usar una ruta explícita para evitar archivos duplicados de RAM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAM_FILE = os.path.join(BASE_DIR, "memory_ram.txt")

mem = Memory(2**16, memory_file=RAM_FILE)

io = IOSystem()
io.register(1,Screen())
io.register(2,Keyboard())

cpu = CPU(mem,io)
app = SimuladorGUI(cpu)

app.mainloop()