class Usuario:
    def __init__(self, id_usuario=None, nome="", email="", senha_hash="", tipo="leitor", data_cadastro=None):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.tipo = tipo
        self.data_cadastro = data_cadastro

    def eh_admin(self):
        return self.tipo == "admin"

    def to_dict(self):  # nunca expõe a senha
        return {"id_usuario": self.id_usuario, "nome": self.nome, "email": self.email,
                "tipo": self.tipo, "data_cadastro": self.data_cadastro}
