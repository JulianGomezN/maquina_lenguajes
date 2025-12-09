import logging
import struct
from machine.Memory.Memory import Memory
from compiler.Loader import Loader
from compiler.instructions import IS_INV


def test_memory_write_little_endian():
    mem = Memory(0x2000)
    addr = 0x100
    val = 0x01020304
    mem.write(addr, val, 4)
    # little-endian storage expected
    stored = bytes(mem.mem[addr:addr+4])
    assert stored == bytes([0x04, 0x03, 0x02, 0x01])


def test_loader_consumes_data_directive(tmp_path):
    # Create memory and loader
    mem = Memory(0x20000)
    loader = Loader(mem, init_data_on_load=True)

    # craft a relocatable text that includes a .DATA directive
    addr = 0x0010000
    size = 8
    val = 123456789
    b = (val & ((1 << (size*8)) - 1)).to_bytes(size, 'little')
    hexbytes = b.hex().upper()

    rel_text = f".DATA {addr:08X} {size} {hexbytes}\n"

    absoluto, end = loader.load_in_memory(rel_text, 0)

    # verify memory was written
    stored = bytes(mem.mem[addr:addr+size])
    assert stored == b
