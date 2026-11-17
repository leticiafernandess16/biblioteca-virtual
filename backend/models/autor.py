# Cria a classe Autor, que representa um autor cadastrado no sistema.
class Autor:

    # Método construtor: é executado automaticamente quando um objeto
    # da classe Autor é criado.
    # Os parâmetros possuem valores padrão para facilitar a criação
    # de objetos mesmo quando algumas informações não são fornecidas.
    def __init__(self, id_autor=None, nome="", nacionalidade="", biografia=""):

        # Armazena o identificador do autor.
        # None significa que nenhum ID foi informado.
        self.id_autor = id_autor

        # Armazena o nome do autor.
        self.nome = nome

        # Armazena a nacionalidade do autor.
        self.nacionalidade = nacionalidade

        # Armazena a biografia do autor.
        self.biografia = biografia

    # Método responsável por transformar os dados do objeto
    # em um dicionário.
    def to_dict(self):

        # __dict__ contém os atributos do objeto e seus respectivos valores.
        # copy() cria uma cópia desse dicionário para ser retornada.
        return self.__dict__.copy()