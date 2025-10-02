from GUI.GUI import SimuladorGUI
from logic.Memory import Memory
from logic.CPU import CPU

mem = Memory(2**16)

cpu = CPU(mem)
app = SimuladorGUI(cpu)

app.mainloop()