# Classe responsável por representar uma curiosidade cadastrada no sistema.
class Curiosidade:

    # Método construtor que recebe os dados da curiosidade e inicializa seus atributos.
    def __init__(self, id_curiosidade=None, titulo="", texto=""):

        # Armazena o identificador único da curiosidade.
        self.id_curiosidade = id_curiosidade

        # Armazena o título da curiosidade.
        self.titulo = titulo

        # Armazena o texto com as informações da curiosidade.
        self.texto = texto

    # Método que transforma os dados da curiosidade em um dicionário.
    def to_dict(self):

        # Retorna uma cópia dos atributos da curiosidade no formato de dicionário.
        return self.__dict__.copy()