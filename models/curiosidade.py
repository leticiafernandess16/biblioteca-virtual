class Curiosidade:
    def __init__(self, id_curiosidade=None, titulo="", texto=""):
        self.id_curiosidade = id_curiosidade
        self.titulo = titulo
        self.texto = texto

    def to_dict(self):
        return self.__dict__.copy()
