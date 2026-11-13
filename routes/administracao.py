# Importa o Blueprint e o jsonify do Flask.
# Blueprint permite organizar as rotas da aplicação em arquivos separados.
# jsonify transforma os dados retornados em uma resposta no formato JSON.
from flask import Blueprint, jsonify

# Importa a classe EstatisticaDAO, responsável por buscar os dados
# estatísticos utilizados no painel de administração.
from dao.estatistica_dao import EstatisticaDAO

# Importa o decorador que verifica se o usuário possui permissão de administrador.
from routes.auth import admin_obrigatorio


# Cria um Blueprint chamado "administracao".
# O prefixo "/api/admin" será adicionado ao início de todas as rotas
# registradas neste Blueprint.
bp = Blueprint("administracao", __name__, url_prefix="/api/admin")


# Define uma rota que aceita requisições do tipo GET no endereço "/painel".
# Como o Blueprint possui o prefixo "/api/admin",
# o endereço completo da rota será "/api/admin/painel".
@bp.get("/painel")

# Exige que o usuário seja administrador para acessar essa rota.
# Caso não tenha a permissão necessária, o acesso será bloqueado.
@admin_obrigatorio
def painel():
    # Cria uma instância de EstatisticaDAO e chama o método painel().
    # Esse método busca ou organiza os dados estatísticos do sistema.
    # jsonify transforma esses dados em uma resposta JSON,
    # que poderá ser utilizada pelo site, por exemplo, para exibir
    # as informações no painel administrativo.
    return jsonify(EstatisticaDAO().painel())