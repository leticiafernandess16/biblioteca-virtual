class Avaliacao:
    def __init__(self, id_avaliacao=None, nota=5, comentario="", data_avaliacao=None,
                 id_usuario=None, id_livro=None):
        self.id_avaliacao = id_avaliacao
        self.nota = nota
        self.comentario = comentario
        self.data_avaliacao = data_avaliacao
        self.id_usuario = id_usuario
        self.id_livro = id_livro

    def to_dict(self):
        return self.__dict__.copy()
