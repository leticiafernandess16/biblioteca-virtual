# Importa os recursos necessários do Flask.
# Blueprint permite organizar as rotas em arquivos separados.
# jsonify transforma os dados em respostas no formato JSON.
# session permite acessar as informações do usuário que está conectado.
from flask import Blueprint, jsonify, session

# Importa a classe EmprestimoDAO, responsável pelas operações
# relacionadas aos empréstimos de livros no banco de dados.
from dao.emprestimo_dao import EmprestimoDAO

# Importa os decoradores que controlam o acesso às rotas.
# login_obrigatorio exige que o usuário esteja logado.
# admin_obrigatorio exige que o usuário seja administrador.
from routes.auth import login_obrigatorio, admin_obrigatorio


# Cria um Blueprint chamado "emprestimos".
# O prefixo "/api" será adicionado ao início de todas as rotas
# registradas neste Blueprint.
bp = Blueprint("emprestimos", __name__, url_prefix="/api")

# Cria uma instância de EmprestimoDAO.
# Ela será utilizada pelas funções abaixo para realizar
# operações de empréstimo, devolução e consulta.
dao = EmprestimoDAO()


# Define uma rota POST para realizar o empréstimo de um livro.
# O endereço recebe o ID do livro como um número inteiro.
# Exemplo: /api/emprestimos/5
@bp.post("/emprestimos/<int:id_livro>")

# Exige que o usuário esteja logado para realizar o empréstimo.
@login_obrigatorio
def emprestar(id_livro):

    # Chama o método realizar() do DAO.
    # Envia o ID do usuário que está logado e o ID do livro desejado.
    # O método retorna duas informações:
    # ok: indica se o empréstimo foi realizado com sucesso.
    # msg: contém uma mensagem explicando o resultado.
    ok, msg = dao.realizar(session["id_usuario"], id_livro)

    # Verifica se a operação foi realizada com sucesso.
    # Se ok for verdadeiro, retorna a mensagem com o código 201 (criado).
    # Caso contrário, retorna o erro com o código 409 (conflito).
    return (jsonify(mensagem=msg), 201) if ok else (jsonify(erro=msg), 409)


# Define uma rota GET para consultar os empréstimos
# do usuário que está logado.
# Endereço: /api/emprestimos/meus
@bp.get("/emprestimos/meus")

# Exige que o usuário esteja logado.
@login_obrigatorio
def meus():

    # Chama listar_por_usuario() para buscar os empréstimos
    # vinculados ao ID do usuário que está na sessão.
    # O método to_dict() transforma cada empréstimo em um dicionário.
    # A lista de dicionários é convertida em uma resposta JSON.
    return jsonify([e.to_dict() for e in dao.listar_por_usuario(session["id_usuario"])])


# Define uma rota POST para devolver um empréstimo.
# O endereço recebe o ID do empréstimo como um número inteiro.
# Exemplo: /api/emprestimos/3/devolver
@bp.post("/emprestimos/<int:id_emprestimo>/devolver")

# Exige que o usuário esteja logado.
@login_obrigatorio
def devolver(id_emprestimo):

    # Verifica o tipo de usuário que está logado.
    # Se for administrador, dono recebe None.
    # Isso indica que a devolução não ficará limitada
    # aos empréstimos pertencentes ao próprio administrador.
    # Se não for administrador, dono recebe o ID do usuário logado,
    # permitindo verificar se o empréstimo pertence a ele.
    dono = None if session.get("tipo") == "admin" else session["id_usuario"]

    # Chama o método devolver() do DAO.
    # Envia o ID do empréstimo e a identificação do responsável
    # que poderá realizar a devolução.
    # Retorna ok, indicando o resultado, e msg, com a mensagem.
    ok, msg = dao.devolver(id_emprestimo, dono)

    # Se a devolução for realizada, retorna a mensagem com o código 200.
    # Se não for possível, retorna uma mensagem de erro com o código 409.
    return (jsonify(mensagem=msg), 200) if ok else (jsonify(erro=msg), 409)


# Define uma rota GET para consultar todos os empréstimos cadastrados.
# Endereço: /api/emprestimos
@bp.get("/emprestimos")

# Permite o acesso somente a usuários administradores.
@admin_obrigatorio
def todos():

    # Chama listar_todos() para buscar todos os empréstimos.
    # O método to_dict() transforma cada empréstimo em um dicionário.
    # jsonify converte a lista resultante em uma resposta JSON.
    return jsonify([e.to_dict() for e in dao.listar_todos()])