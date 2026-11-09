class Favorito:
    def __init__(self, id_favorito=None, data_adicao=None, id_usuario=None, id_livro=None):
        self.id_favorito = id_favorito
        self.data_adicao = data_adicao
        self.id_usuario = id_usuario
        self.id_livro = id_livro

    def to_dict(self):
        return self.__dict__.copy()
