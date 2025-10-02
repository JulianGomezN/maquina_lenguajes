from GUI.GUI import *

root = tk.Tk()
mem = Memory(2**10*1000)
app = SimuladorGUI(root,CPU(mem),mem)
app.set_salida("Hola")
app.append_salida(" mundo")
root.mainloop()