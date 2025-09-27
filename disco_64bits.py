class Disco:
    def __init__(self):
        # 16 registros de 4 bits
        self.registros = "0000" * 16
        # 65536 celdas de memoria de 64 bits
        self.memoria = "0" * (64 * 65536)

    """
    Este metodo lo usamos para poder saber si vamos a leer un registro o una celda de memoria,
    aparte de que nos avisa si colocamos un indice invalido
    """
    def get_index(self, nombre: str):
        tipo = nombre[0].upper()
        if tipo not in ("R", "M"):
            print("Nombre inválido, debe empezar con R o M")
            return None, None

        try:
            idx = int(nombre[1:])
        except ValueError:
            print("Formato inválido, debe ser Rxx o Mxxxx")
            return None, None

        if tipo == "R":
            if idx < 0 or idx >= 16:
                print("Registro fuera de rango (R00–R15)")
                return None, None
        elif tipo == "M":
            if idx < 0 or idx >= 65536:
                print("Celda de memoria fuera de rango (M0–M65535)")
                return None, None

        return tipo, idx

    """
    Para poder leer una celda toca especificar la celda (si es registro o memoria),
    y la dirección de la celda con la nomenclatura Rxx o Mxxxx.
    """
    def leer(self, nombre: str) -> str:
        tipo, idx = self.get_index(nombre)
        if tipo is None:
            return ""
        if tipo == "R":
            start = idx * 4
            return self.registros[start:start+4]
        else:
            start = idx * 64
            return self.memoria[start:start+64]

    """
    Lo mismo para escribir, pero está vez toca añadir que queremos escribir. Si
    el dato es menor a 64 bits, se guarda en los últimos bits
    """
    def escribir(self, nombre: str, valor: str):
        tipo, idx = self.get_index(nombre)
        if tipo is None:
            return

        if tipo == "R":
            if len(valor) != 4 or not all(c in "01" for c in valor):
                print("Registro debe ser un string de 4 bits")
                return
            start = idx * 4
            self.registros = (
                self.registros[:start] + valor + self.registros[start+4:]
            )
        else:
            if not all(c in "01" for c in valor):
                print("Celda de memoria debe ser un string de bits (0/1)")
                return
            if len(valor) > 64:
                print("Celda de memoria no puede exceder 64 bits")
                return
            # Alinear a la derecha con ceros delante si es menor de 64 bits
            valor = valor.zfill(64)
            start = idx * 64
            self.memoria = (
                self.memoria[:start] + valor + self.memoria[start+64:]
            )