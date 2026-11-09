class ListaLeitura:
    def __init__(self, id_lista=None, data_adicao=None, data_leitura=None,
                 status="quero_ler", id_usuario=None, id_livro=None):
        self.id_lista = id_lista
        self.data_adicao = data_adicao
        self.data_leitura = data_leitura
        self.status = status  # 'quero_ler' ou 'lido'
        self.id_usuario = id_usuario
        self.id_livro = id_livro

    def to_dict(self):
        return self.__dict__.copy()
