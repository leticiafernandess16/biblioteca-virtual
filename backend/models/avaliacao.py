# Classe responsável por representar uma avaliação feita por um usuário sobre um livro.
class Avaliacao:

    # Método construtor que recebe os dados da avaliação e inicializa seus atributos.
    def __init__(self, id_avaliacao=None, nota=5, comentario="", data_avaliacao=None,
                 id_usuario=None, id_livro=None):

        # Armazena o identificador único da avaliação.
        self.id_avaliacao = id_avaliacao

        # Armazena a nota atribuída ao livro (o valor padrão é 5).
        self.nota = nota

        # Armazena o comentário escrito pelo usuário sobre o livro.
        self.comentario = comentario

        # Armazena a data em que a avaliação foi realizada.
        self.data_avaliacao = data_avaliacao

        # Armazena o ID do usuário que fez a avaliação.
        self.id_usuario = id_usuario

        # Armazena o ID do livro que recebeu a avaliação.
        self.id_livro = id_livro

    # Método que transforma os dados da avaliação em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos da avaliação no formato de dicionário.
        return self.__dict__.copy()