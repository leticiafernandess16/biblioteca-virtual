class Emprestimo:
    def __init__(self, id_emprestimo=None, data_emprestimo=None, data_prevista_devolucao=None,
                 data_devolucao=None, status="ativo", id_usuario=None, id_livro=None,
                 titulo=None, usuario=None):
        self.id_emprestimo = id_emprestimo
        self.data_emprestimo = data_emprestimo
        self.data_prevista_devolucao = data_prevista_devolucao
        self.data_devolucao = data_devolucao
        self.status = status
        self.id_usuario = id_usuario
        self.id_livro = id_livro
        self.titulo = titulo
        self.usuario = usuario

    def to_dict(self):
        return self.__dict__.copy()
