from machine.IO.Devices import Device

class IOSystem:
    def __init__(self):
        self.devices: dict[int,Device] = {}

    def register(self, addr, device):
        """Registra un dispositivo en una dirección de IO"""
        self.devices[addr] = device

    def get_device(self, addr):
        return self.devices.get(addr)

    def write(self, addr, value):
        device = self.devices.get(addr)
        if device:
            device.write(value)
        else:
            print(f"[WARN] Dispositivo en {hex(addr)} no existe")

    def read(self, addr):
        device = self.devices.get(addr)
        if device:
            return device.read()
        print(f"[WARN] Dispositivo en {hex(addr)} no existe")
        return 0
