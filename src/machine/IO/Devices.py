class Device:
    def read(self):
        raise NotImplementedError("read() no implementado")

    def write(self, value):
        raise NotImplementedError("write() no implementado")

class Screen(Device):
    def __init__(self):
        self.buffer = ""  # guarda lo que se imprimió

    def write(self, value):
        self.buffer += chr(value & 0xFF)
    
class Keyboard(Device):

    def __init__(self):
        self.buffer = []

    def read(self):
        if len(self.buffer) == 0 :
            return 0xFF
        ch = self.buffer[0]
        self.buffer.remove(ch)
        return ch

    def write(self, value:int):
        self.buffer.append(value & 0xFF) # solo un byte (0–255)


if __name__ == "__main__":
    print("Testing devices")
    k = Keyboard()
    s = Screen()

    while 1:
        k.write(ord(input(">")))
        ascii = k.read()
        s.write(ascii)
        print("Contenido de pantalla: ",s.buffer)
