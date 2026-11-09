class Genero:
    def __init__(self, id_genero=None, nome="", descricao=""):
        self.id_genero = id_genero
        self.nome = nome
        self.descricao = descricao

    def to_dict(self):
        return self.__dict__.copy()
