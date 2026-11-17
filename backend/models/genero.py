# Classe responsável por representar um gênero literário no sistema.
class Genero:

    # Método construtor que recebe os dados do gênero e inicializa seus atributos.
    def __init__(self, id_genero=None, nome="", descricao=""):

        # Armazena o identificador único do gênero.
        self.id_genero = id_genero

        # Armazena o nome do gênero literário.
        self.nome = nome

        # Armazena a descrição do gênero literário.
        self.descricao = descricao

    # Método que transforma os dados do gênero em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos do gênero no formato de dicionário.
        return self.__dict__.copy()