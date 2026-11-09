class Livro:
    def __init__(self, id_livro=None, titulo="", isbn=None, ano_publicacao=None, editora="",
                 quantidade_total=1, quantidade_disponivel=1, capa_url="",
                 classificacao_indicativa="", sinopse="", data_cadastro=None,
                 id_autor=None, id_genero=None, autor=None, genero=None,
                 nota_media=None, total_avaliacoes=0, total_emprestimos=0):
        self.id_livro = id_livro
        self.titulo = titulo
        self.isbn = isbn
        self.ano_publicacao = ano_publicacao
        self.editora = editora
        self.quantidade_total = quantidade_total
        self.quantidade_disponivel = quantidade_disponivel
        self.capa_url = capa_url
        self.classificacao_indicativa = classificacao_indicativa
        self.sinopse = sinopse
        self.data_cadastro = data_cadastro
        self.id_autor = id_autor
        self.id_genero = id_genero
        self.autor = autor            # nome do autor (exibição)
        self.genero = genero          # nome do gênero (exibição)
        self.nota_media = nota_media  # média das avaliações
        self.total_avaliacoes = total_avaliacoes
        self.total_emprestimos = total_emprestimos  # popularidade

    def disponivel(self):
        return self.quantidade_disponivel > 0

    def to_dict(self):
        d = self.__dict__.copy()
        d["disponivel"] = self.disponivel()
        return d
