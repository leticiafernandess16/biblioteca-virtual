# Importa o módulo re, utilizado para trabalhar com expressões regulares.
# Ele será usado para verificar se o e-mail possui um formato válido.
import re

# Importa os recursos necessários do Flask.
# Blueprint organiza as rotas da aplicação.
# request permite acessar os dados enviados pelo usuário.
# jsonify transforma os dados em respostas JSON.
# session armazena informações do usuário durante sua navegação.
from flask import Blueprint, request, jsonify, session

# Importa as funções responsáveis por proteger as senhas.
# generate_password_hash() transforma a senha em um hash,
# evitando armazenar a senha original diretamente no banco de dados.
# check_password_hash() verifica se uma senha corresponde ao hash armazenado.
from werkzeug.security import generate_password_hash, check_password_hash

# Importa a classe UsuarioDAO, responsável pelas operações
# relacionadas aos usuários no banco de dados.
from dao.usuario_dao import UsuarioDAO

# Importa a classe Usuario, que representa os dados de um usuário.
from models.usuario import Usuario

# Importa os decoradores que controlam o acesso às rotas.
# admin_obrigatorio exige que o usuário seja administrador.
# login_obrigatorio exige que o usuário esteja conectado.
from routes.auth import admin_obrigatorio, login_obrigatorio


# Cria um Blueprint chamado "usuarios".
# Todas as rotas deste Blueprint terão o prefixo "/api".
bp = Blueprint("usuarios", __name__, url_prefix="/api")

# Cria uma instância de UsuarioDAO.
# Ela será utilizada para cadastrar, consultar e atualizar usuários.
dao = UsuarioDAO()

# Cria uma expressão regular para verificar o formato dos e-mails.
# ^ indica o início do texto.
# [^@\s]+ exige um ou mais caracteres que não sejam @ ou espaços.
# @ exige a presença do símbolo de arroba.
# \. exige um ponto antes da parte final do endereço.
# $ indica o final do texto.
# O padrão verifica formatos como usuario@email.com.
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# Define uma rota POST para cadastrar uma nova conta.
# Endereço: /api/cadastro
@bp.post("/cadastro")
def cadastro():

    # Obtém os dados enviados pelo usuário em formato JSON.
    # Se não houver dados ou eles não puderem ser interpretados,
    # utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Obtém o nome, o e-mail e a senha enviados.
    # strip() remove espaços em branco do início e do final do nome e do e-mail.
    # lower() transforma o e-mail em letras minúsculas.
    # A senha é mantida como foi digitada pelo usuário.
    nome, email, senha = d.get("nome", "").strip(), d.get("email", "").strip().lower(), d.get("senha", "")

    # Verifica se o nome possui pelo menos 2 caracteres.
    if len(nome) < 2:

        # Se o nome for muito curto ou estiver vazio,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="Informe o nome."), 400

    # Verifica se o e-mail corresponde ao formato definido
    # na expressão regular EMAIL_RE.
    if not EMAIL_RE.match(email):

        # Se o formato estiver incorreto,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="E-mail inválido."), 400

    # Verifica se a senha possui pelo menos 6 caracteres.
    if len(senha) < 6:

        # Se a senha for muito curta,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="A senha deve ter ao menos 6 caracteres."), 400

    # Cria um objeto Usuario com o nome, o e-mail e o hash da senha.
    # generate_password_hash() protege a senha antes de armazená-la.
    # Em seguida, dao.inserir() tenta cadastrar o usuário no banco de dados.
    novo = dao.inserir(Usuario(nome=nome, email=email, senha_hash=generate_password_hash(senha)))

    # Verifica se o cadastro não foi realizado.
    if novo is None:

        # Retorna uma mensagem de erro com o código 409 (conflito).
        # Nesse caso, significa que o e-mail já está cadastrado.
        return jsonify(erro="E-mail já cadastrado."), 409

    # Se o cadastro funcionar, retorna uma mensagem de sucesso
    # e o código 201, que indica que uma nova conta foi criada.
    return jsonify(mensagem="Conta criada! Faça login."), 201


# Define uma rota POST para realizar o login do usuário.
# Endereço: /api/login
@bp.post("/login")
def login():

    # Obtém os dados enviados pelo usuário em formato JSON.
    # Se não houver dados válidos, utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Busca no banco de dados um usuário com o e-mail informado.
    # strip() remove espaços extras e lower() transforma o e-mail
    # em letras minúsculas para facilitar a comparação.
    u = dao.buscar_por_email(d.get("email", "").strip().lower())

    # Verifica duas condições:
    # 1. Se o usuário não foi encontrado.
    # 2. Se a senha informada não corresponde ao hash armazenado.
    # check_password_hash() realiza essa verificação de forma segura.
    if not u or not check_password_hash(u.senha_hash, d.get("senha", "")):

        # Se alguma das condições for verdadeira,
        # retorna uma mensagem de erro com o código 401 (não autorizado).
        return jsonify(erro="E-mail ou senha incorretos."), 401

    # Armazena na sessão o ID e o tipo do usuário conectado.
    # Essas informações serão utilizadas para identificar o usuário
    # e controlar o acesso às funcionalidades do sistema.
    session["id_usuario"], session["tipo"] = u.id_usuario, u.tipo

    # Retorna os dados do usuário em formato JSON.
    # to_dict() transforma o objeto Usuario em um dicionário.
    return jsonify(usuario=u.to_dict())


# Define uma rota POST para encerrar a sessão do usuário.
# Endereço: /api/logout
@bp.post("/logout")
def logout():

    # Limpa todas as informações armazenadas na sessão.
    # Assim, os dados de login deixam de estar disponíveis.
    session.clear()

    # Retorna uma mensagem confirmando o encerramento da sessão.
    return jsonify(mensagem="Sessão encerrada.")


# Define uma rota GET para consultar os dados do usuário conectado.
# Endereço: /api/me
@bp.get("/me")
def me():

    # Verifica se o ID do usuário está armazenado na sessão.
    # Se não estiver, significa que não existe um usuário conectado.
    if "id_usuario" not in session:

        # Retorna usuario=None para indicar que não há usuário conectado.
        return jsonify(usuario=None)

    # Busca no banco de dados o usuário que possui o ID armazenado na sessão.
    u = dao.buscar_por_id(session["id_usuario"])

    # Retorna os dados do usuário em formato JSON.
    # Se o usuário for encontrado, transforma seus dados em dicionário.
    # Caso contrário, retorna None.
    return jsonify(usuario=u.to_dict() if u else None)


# Define uma rota GET para listar todos os usuários cadastrados.
# Endereço: /api/usuarios
@bp.get("/usuarios")

# Permite que somente administradores acessem essa rota.
@admin_obrigatorio
def listar():

    # Chama o método listar() do UsuarioDAO para buscar os usuários.
    # to_dict() transforma cada objeto Usuario em um dicionário.
    # jsonify retorna a lista completa em formato JSON.
    return jsonify([u.to_dict() for u in dao.listar()])


# Define uma rota PUT para editar o perfil do usuário conectado.
# Endereço: /api/perfil
@bp.put("/perfil")

# Exige que o usuário esteja logado para editar o próprio perfil.
@login_obrigatorio
def editar_perfil():

    # Obtém os dados enviados pelo usuário em formato JSON.
    # Se não houver dados válidos, utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Obtém o nome e a nova senha informados.
    # strip() remove espaços extras do início e do final do nome.
    # Se a senha não for informada, utiliza uma string vazia.
    nome, senha = d.get("nome", "").strip(), d.get("senha", "")

    # Verifica se o nome possui pelo menos 2 caracteres.
    if len(nome) < 2:

        # Se o nome estiver vazio ou for muito curto,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="Informe o nome."), 400

    # Verifica se uma nova senha foi informada.
    # Se foi informada, ela precisa possuir pelo menos 6 caracteres.
    if senha and len(senha) < 6:

        # Se a nova senha for muito curta,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="A nova senha deve ter ao menos 6 caracteres."), 400

    # Chama o método atualizar() do UsuarioDAO para modificar o perfil.
    # Envia o ID do usuário conectado e o novo nome.
    # Se uma nova senha tiver sido informada, ela será transformada
    # em hash antes de ser armazenada.
    # Se nenhuma senha for informada, envia None para indicar
    # que a senha atual deve ser mantida.
    dao.atualizar(session["id_usuario"], nome, generate_password_hash(senha) if senha else None)

    # Retorna uma mensagem confirmando a atualização do perfil.
    # Também busca novamente os dados do usuário atualizado
    # e os envia em formato JSON.
    return jsonify(mensagem="Perfil atualizado.", usuario=dao.buscar_por_id(session["id_usuario"]).to_dict())