class MetaLeitura:
    def __init__(self, id_meta=None, ano=None, quantidade_meta=0, id_usuario=None, lidos=0):
        self.id_meta = id_meta
        self.ano = ano
        self.quantidade_meta = quantidade_meta
        self.id_usuario = id_usuario
        self.lidos = lidos  # calculado a partir da lista de leitura

    def percentual(self):
        if not self.quantidade_meta:
            return 0
        return min(100, round(self.lidos * 100 / self.quantidade_meta))

    def to_dict(self):
        d = self.__dict__.copy()
        d["percentual"] = self.percentual()
        return d
