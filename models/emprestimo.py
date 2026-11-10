# Classe responsável por representar um empréstimo de livro no sistema.
class Emprestimo:

    # Método construtor que recebe os dados do empréstimo e inicializa seus atributos.
    def __init__(self, id_emprestimo=None, data_emprestimo=None, data_prevista_devolucao=None,
                 data_devolucao=None, status="ativo", id_usuario=None, id_livro=None,
                 titulo=None, usuario=None):

        # Armazena o identificador único do empréstimo.
        self.id_emprestimo = id_emprestimo

        # Armazena a data em que o livro foi emprestado.
        self.data_emprestimo = data_emprestimo

        # Armazena a data prevista para a devolução do livro.
        self.data_prevista_devolucao = data_prevista_devolucao

        # Armazena a data em que o livro foi realmente devolvido.
        self.data_devolucao = data_devolucao

        # Armazena a situação atual do empréstimo (o padrão é "ativo").
        self.status = status

        # Armazena o ID do usuário que realizou o empréstimo.
        self.id_usuario = id_usuario

        # Armazena o ID do livro que foi emprestado.
        self.id_livro = id_livro

        # Armazena o título do livro emprestado.
        self.titulo = titulo

        # Armazena o nome ou os dados do usuário responsável pelo empréstimo.
        self.usuario = usuario

    # Método que transforma os dados do empréstimo em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos do empréstimo no formato de dicionário.
        return self.__dict__.copy()