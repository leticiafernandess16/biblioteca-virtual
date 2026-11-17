# Importa a função wraps do módulo functools.
# Ela preserva as informações originais da função decorada,
# como o nome e a documentação.
from functools import wraps

# Importa session e jsonify do Flask.
# session permite acessar os dados da sessão do usuário,
# como o ID e o tipo de conta.
# jsonify transforma os dados em uma resposta no formato JSON.
from flask import session, jsonify


# Cria um decorador que exige que o usuário esteja logado
# para acessar determinada rota.
def login_obrigatorio(f):

    # O wraps preserva as informações da função original.
    @wraps(f)
    def inner(*a, **kw):

        # Verifica se o ID do usuário não está armazenado na sessão.
        # Se não estiver, significa que o usuário não fez login.
        if "id_usuario" not in session:

            # Retorna uma mensagem de erro em JSON
            # e o código HTTP 401 (não autorizado).
            return jsonify(erro="Faça login para continuar."), 401

        # Se o usuário estiver logado, permite que a função original
        # seja executada normalmente.
        return f(*a, **kw)

    # Retorna a função interna, que passa a controlar
    # o acesso à função original.
    return inner


# Cria um decorador que exige que o usuário seja administrador.
def admin_obrigatorio(f):

    # Preserva as informações da função original.
    @wraps(f)
    def inner(*a, **kw):

        # Primeiro, verifica se o usuário está logado.
        if "id_usuario" not in session:

            # Se não estiver logado, retorna erro 401.
            return jsonify(erro="Faça login para continuar."), 401

        # Verifica se o tipo de usuário armazenado na sessão
        # é diferente de "admin".
        if session.get("tipo") != "admin":

            # Se não for administrador, bloqueia o acesso
            # e retorna o código HTTP 403 (acesso proibido).
            return jsonify(erro="Acesso restrito ao administrador."), 403

        # Se o usuário estiver logado e for administrador,
        # permite a execução da função original.
        return f(*a, **kw)

    # Retorna a função interna, que controla
    # o acesso à função original.
    return inner