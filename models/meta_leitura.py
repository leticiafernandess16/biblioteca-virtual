# Classe responsável por representar uma meta de leitura definida por um usuário.
class MetaLeitura:

    # Método construtor que recebe os dados da meta e inicializa seus atributos.
    def __init__(self, id_meta=None, ano=None, quantidade_meta=0, id_usuario=None, lidos=0):

        # Armazena o identificador único da meta de leitura.
        self.id_meta = id_meta

        # Armazena o ano em que a meta de leitura deve ser cumprida.
        self.ano = ano

        # Armazena a quantidade de livros que o usuário pretende ler no ano.
        self.quantidade_meta = quantidade_meta

        # Armazena o ID do usuário que criou a meta.
        self.id_usuario = id_usuario

        # Armazena a quantidade de livros já lidos pelo usuário, calculada a partir da lista de leitura.
        self.lidos = lidos

    # Método que calcula o percentual de conclusão da meta de leitura.
    def percentual(self):

        # Verifica se a quantidade da meta é zero para evitar divisão por zero.
        if not self.quantidade_meta:
            return 0

        # Calcula a porcentagem de livros lidos em relação à meta,
        # arredonda o resultado e limita o valor máximo a 100%.
        return min(100, round(self.lidos * 100 / self.quantidade_meta))

    # Método que transforma os dados da meta de leitura em um dicionário.
    def to_dict(self):

        # Cria uma cópia dos atributos da meta no formato de dicionário.
        d = self.__dict__.copy()

        # Adiciona ao dicionário o percentual de conclusão da meta.
        d["percentual"] = self.percentual()

        # Retorna o dicionário com todos os dados da meta.
        return d