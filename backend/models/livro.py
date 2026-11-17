# Classe responsável por representar um livro cadastrado no sistema.
class Livro:

    # Método construtor que recebe os dados do livro e inicializa seus atributos.
    def __init__(self, id_livro=None, titulo="", isbn=None, ano_publicacao=None, editora="",
                 quantidade_total=1, quantidade_disponivel=1, capa_url="",
                 classificacao_indicativa="", sinopse="", data_cadastro=None,
                 id_autor=None, id_genero=None, autor=None, genero=None,
                 nota_media=None, total_avaliacoes=0, total_emprestimos=0):

        # Armazena o identificador único do livro.
        self.id_livro = id_livro

        # Armazena o título do livro.
        self.titulo = titulo

        # Armazena o código ISBN utilizado para identificar o livro.
        self.isbn = isbn

        # Armazena o ano em que o livro foi publicado.
        self.ano_publicacao = ano_publicacao

        # Armazena o nome da editora responsável pela publicação.
        self.editora = editora

        # Armazena a quantidade total de exemplares do livro.
        self.quantidade_total = quantidade_total

        # Armazena a quantidade de exemplares disponíveis para empréstimo.
        self.quantidade_disponivel = quantidade_disponivel

        # Armazena o endereço da imagem da capa do livro.
        self.capa_url = capa_url

        # Armazena a classificação indicativa do livro.
        self.classificacao_indicativa = classificacao_indicativa

        # Armazena o resumo ou a sinopse do livro.
        self.sinopse = sinopse

        # Armazena a data em que o livro foi cadastrado no sistema.
        self.data_cadastro = data_cadastro

        # Armazena o ID do autor relacionado ao livro.
        self.id_autor = id_autor

        # Armazena o ID do gênero literário relacionado ao livro.
        self.id_genero = id_genero

        # Armazena o nome do autor para exibição no sistema.
        self.autor = autor

        # Armazena o nome do gênero literário para exibição no sistema.
        self.genero = genero

        # Armazena a média das notas recebidas nas avaliações.
        self.nota_media = nota_media

        # Armazena a quantidade total de avaliações recebidas pelo livro.
        self.total_avaliacoes = total_avaliacoes

        # Armazena a quantidade de empréstimos realizados do livro, indicando sua popularidade.
        self.total_emprestimos = total_emprestimos

    # Método que verifica se o livro possui exemplares disponíveis para empréstimo.
    def disponivel(self):

        # Retorna True se houver pelo menos um exemplar disponível; caso contrário, retorna False.
        return self.quantidade_disponivel > 0

    # Método que transforma os dados do livro em um dicionário.
    def to_dict(self):

        # Cria uma cópia dos atributos do livro no formato de dicionário.
        d = self.__dict__.copy()

        # Adiciona ao dicionário a informação sobre a disponibilidade do livro.
        d["disponivel"] = self.disponivel()

        # Retorna o dicionário com todos os dados do livro.
        return d