# Classe responsável por representar um usuário cadastrado no sistema.
class Usuario:

    # Método construtor que recebe os dados do usuário e inicializa seus atributos.
    def __init__(self, id_usuario=None, nome="", email="", senha_hash="", tipo="leitor", data_cadastro=None):

        # Armazena o identificador único do usuário.
        self.id_usuario = id_usuario

        # Armazena o nome do usuário.
        self.nome = nome

        # Armazena o endereço de e-mail utilizado pelo usuário.
        self.email = email

        # Armazena a senha criptografada (hash) do usuário.
        self.senha_hash = senha_hash

        # Armazena o tipo de usuário, que pode ser "leitor" ou "admin".
        self.tipo = tipo

        # Armazena a data em que o usuário foi cadastrado no sistema.
        self.data_cadastro = data_cadastro

    # Método que verifica se o usuário possui acesso de administrador.
    def eh_admin(self):

        # Retorna True se o tipo do usuário for "admin"; caso contrário, retorna False.
        return self.tipo == "admin"

    # Método que transforma os dados do usuário em um dicionário.
    def to_dict(self):  # Nunca expõe a senha

        # Retorna os dados do usuário sem incluir a senha criptografada,
        # protegendo as informações de acesso.
        return {"id_usuario": self.id_usuario, "nome": self.nome, "email": self.email,
                "tipo": self.tipo, "data_cadastro": self.data_cadastro}