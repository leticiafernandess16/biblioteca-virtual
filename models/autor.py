class Autor:
    def __init__(self, id_autor=None, nome="", nacionalidade="", biografia=""):
        self.id_autor = id_autor
        self.nome = nome
        self.nacionalidade = nacionalidade
        self.biografia = biografia

    def to_dict(self):
        return self.__dict__.copy()
