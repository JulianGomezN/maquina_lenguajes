from machine.Memory.Memory import Memory

class Loader :

    def __init__(self, memory: Memory):
        self.memory = memory

    def _get_absolute_code(self, code: str, start_address: int):
        """
            Retorna el codigo absoluto para cargarlo en memoria
            
            Args:
                code: Código fuente a cargar
            
            Returns:
                codigo en absoluto numerico
            """

        lines = code.split('\n')
        out = []
        for line in lines:
            if not line:
                continue
            if line.startswith('['):
                temp = line.strip('[]')
                address = int(temp,16)
                address += start_address
                out.append(address)

            else:
                ins = int(line,16)
                out.append(ins)
        return out
    
    def load_in_memory(self, rel_src : str, start_address : int):
        program = self._get_absolute_code(rel_src,start_address)

        address = start_address
        absoluto = ""
        for ins in program:
            self.memory.write(address,ins,8)
            address += 8
            absoluto += f"{ins:016X}\n"
        
        return absoluto
        
# -----------------------------
# Prueba (Powershell)
# cat {codigo relativo path} | python -m compiler.ensamblador | python -m compiler.loader
# -----------------------------
if __name__ == '__main__':
    import sys
    relativo = sys.stdin.read()

    loader = Loader(None)

    absoluto = loader._get_absolute_code(relativo,0)

    for i in absoluto:
        print(f"{i:016X}")