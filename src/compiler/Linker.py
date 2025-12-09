from compiler.ensamblador import CodigoRelo

class Linker:

    def __init__(self):
        self.relocatables :list[CodigoRelo] = []


    def get_liked_code(self) -> CodigoRelo:
        """ Given .relo files return .relo with no extern_labels
        """

        global_labels = {}

        for relo in self.relocatables:
            print(relo)
            print()

        code = ""
        temp_address = 0
        for relo in self.relocatables:
            code += self._offset(relo.codigo, temp_address)

            for label in relo.labels:
                if label in global_labels.keys(): 
                    continue
                global_labels[label] = relo.labels[label]  + temp_address # assign dir to label with offset according to where is append

            for label in relo.extern_labels:
                for i in range(len(relo.extern_labels[label])):
                    relo.extern_labels[label][i] += temp_address # Update where to solve extern

            ## update temp to check next .relo appended to code
            temp_address += relo.size
        
        for relo in self.relocatables:
            print(global_labels)

            
        # Solve extern labels:
        lines = code.split('\n')

        for relo in self.relocatables:
            for label in relo.extern_labels:
                addr = global_labels.get(label) ## where is the actaul function

                if not addr:
                    raise ValueError(f"Linker: Cant solve label - {label}")
                    
                for dir in relo.extern_labels[label]:
                    lines[dir//8] = f"[{addr:016X}]"
        
        code = ""
        for line in lines:
            code += line + '\n'

        obj = CodigoRelo() 
        obj.codigo = code
        obj.labels = global_labels

        return obj
    
    
    def _offset(self,rel :str, offset: int) -> str:
        """ Helper to update rel addresses in appeended code
        """
        code = []
        lines = rel.split('\n')

        for line in lines:
            if line.startswith('['):
                address = int(line.strip("[]"),16) + offset
                code.append(f"[{address:016X}]\n")
            else:
                code.append(line + "\n")

        return "".join(code)

