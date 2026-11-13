# Classe responsável por representar uma lista de leitura de um usuário.
class ListaLeitura:

    # Método construtor que recebe os dados da lista e inicializa seus atributos.
    def __init__(self, id_lista=None, data_adicao=None, data_leitura=None,
                 status="quero_ler", id_usuario=None, id_livro=None):

        # Armazena o identificador único da lista de leitura.
        self.id_lista = id_lista

        # Armazena a data em que o livro foi adicionado à lista.
        self.data_adicao = data_adicao

        # Armazena a data em que o usuário terminou de ler o livro.
        self.data_leitura = data_leitura

        # Armazena a situação da leitura: 'quero_ler' ou 'lido'.
        self.status = status

        # Armazena o ID do usuário responsável pela lista.
        self.id_usuario = id_usuario

        # Armazena o ID do livro adicionado à lista de leitura.
        self.id_livro = id_livro

    # Método que transforma os dados da lista de leitura em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos da lista no formato de dicionário.
        return self.__dict__.copy()