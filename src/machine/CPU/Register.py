MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1
MASK16 = (1 << 16) - 1
MASK8  = (1 << 8) - 1

class Register:
    def __init__(self, name) -> None:
        self.name = name
        self.value = 0
    
    def write(self,value,size=8):
        if size not in [1,2,4,8]:
            raise ValueError(f"Cannot write {size} bytes on register {self.name}\nSizes supported: [1,2,4,8]")

        self.value = value & ((1 << 8*size) - 1)

    def read(self,size):
        """Reads the register and returns its value in size of bytes"""
        value = self.value & ((1 << 8*size) - 1)
        return value

    def print_bits(self):
        binary_representation = "{0:0{1}b}".format(self.value,8)
        print(binary_representation)

if __name__ == "__main__":
    r = Register("R")
    r.write(-1,1)
    print(r.read(1))
    r.print_bits()