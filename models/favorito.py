# Classe responsável por representar um livro adicionado aos favoritos de um usuário.
class Favorito:

    # Método construtor que recebe os dados do favorito e inicializa seus atributos.
    def __init__(self, id_favorito=None, data_adicao=None, id_usuario=None, id_livro=None):

        # Armazena o identificador único do favorito.
        self.id_favorito = id_favorito

        # Armazena a data em que o livro foi adicionado aos favoritos.
        self.data_adicao = data_adicao

        # Armazena o ID do usuário que adicionou o livro aos favoritos.
        self.id_usuario = id_usuario

        # Armazena o ID do livro que foi marcado como favorito.
        self.id_livro = id_livro

    # Método que transforma os dados do favorito em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos do favorito no formato de dicionário.
        return self.__dict__.copy()