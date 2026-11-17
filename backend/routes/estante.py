# Importa a classe date do módulo datetime.
# Ela permite trabalhar com datas, como consultar o ano atual.
from datetime import date

# Importa os recursos necessários do Flask.
# Blueprint organiza as rotas da aplicação.
# request permite acessar os dados enviados pelo usuário.
# jsonify transforma os dados em respostas JSON.
# session permite acessar as informações do usuário conectado.
from flask import Blueprint, request, jsonify, session

# Importa as classes DAO responsáveis pelas operações
# de favoritos, lista de leitura e meta de leitura.
from dao.estante_dao import FavoritoDAO, ListaLeituraDAO, MetaLeituraDAO

# Importa a classe LivroDAO, responsável por buscar
# informações dos livros no banco de dados.
from dao.livro_dao import LivroDAO

# Importa a função get_connection, que permite obter
# uma conexão com o banco de dados.
from database.conexao import get_connection

# Importa o decorador que exige que o usuário esteja logado
# para acessar as rotas da estante.
from routes.auth import login_obrigatorio


# Cria um Blueprint chamado "estante".
# Todas as rotas deste Blueprint terão o prefixo "/api".
bp = Blueprint("estante", __name__, url_prefix="/api")

# Cria uma instância de cada classe DAO.
# fav_dao: gerencia os livros favoritos.
# lista_dao: gerencia a lista de leitura.
# meta_dao: gerencia as metas de leitura.
# livro_dao: busca os dados dos livros.
fav_dao, lista_dao, meta_dao, livro_dao = FavoritoDAO(), ListaLeituraDAO(), MetaLeituraDAO(), LivroDAO()


# Define uma rota GET para consultar os dados da estante do usuário.
# Endereço: /api/estante
@bp.get("/estante")

# Exige que o usuário esteja logado para acessar sua estante.
@login_obrigatorio
def estante():

    # Obtém o ID do usuário que está conectado,
    # utilizando as informações armazenadas na sessão.
    uid = session["id_usuario"]

    # Busca no banco de dados o mapa da lista de leitura do usuário.
    # Esse mapa relaciona os IDs dos livros aos seus status,
    # como "quero_ler" ou "lido".
    mapa = lista_dao.mapa(uid)

    # Busca os IDs dos livros favoritos do usuário.
    # set() transforma os resultados em um conjunto,
    # evitando IDs repetidos.
    favoritos = set(fav_dao.ids(uid))

    # Cria uma função interna para transformar uma lista de IDs
    # em uma lista com os dados completos dos livros.
    def com_status(ids):

        # Percorre cada ID recebido.
        # Busca o livro pelo ID e transforma seus dados em dicionário
        # utilizando to_dict().
        # O if verifica se o livro foi encontrado antes de adicioná-lo.
        return [livro_dao.buscar_por_id(i).to_dict() for i in ids if livro_dao.buscar_por_id(i)]

    # Busca a meta de leitura do usuário referente ao ano atual.
    # date.today().year obtém o ano atual do sistema.
    meta = meta_dao.buscar(uid, date.today().year)

    # Retorna os dados da estante em formato JSON.
    return jsonify(

        # Retorna os livros favoritos do usuário.
        # sorted() organiza os IDs em ordem crescente antes da busca.
        favoritos=com_status(sorted(favoritos)),

        # Retorna os livros que estão com o status "quero_ler".
        # O mapa é percorrido e são selecionados apenas
        # os livros com esse status.
        quero_ler=com_status([i for i, s in mapa.items() if s == "quero_ler"]),

        # Retorna os livros que estão com o status "lido".
        lidos=com_status([i for i, s in mapa.items() if s == "lido"]),

        # Retorna os IDs dos livros favoritos em ordem crescente.
        ids_favoritos=sorted(favoritos),

        # Retorna o mapa com os IDs dos livros e seus respectivos status.
        lista=mapa,

        # Se existir uma meta de leitura, transforma seus dados em dicionário.
        # Caso contrário, retorna None, indicando que não há meta cadastrada.
        meta=meta.to_dict() if meta else None,

        # Retorna o ano atual.
        ano=date.today().year
    )


# Define uma rota POST para adicionar ou remover um livro dos favoritos.
# O endereço recebe o ID do livro como número inteiro.
# Exemplo: /api/favoritos/5
@bp.post("/favoritos/<int:id_livro>")

# Exige que o usuário esteja logado.
@login_obrigatorio
def favoritar(id_livro):

    # Chama o método alternar() do FavoritoDAO.
    # Envia o ID do usuário conectado e o ID do livro.
    # Esse método alterna a situação do livro:
    # se não for favorito, adiciona; se já for, remove.
    r = fav_dao.alternar(session["id_usuario"], id_livro)

    # Verifica se o resultado é None.
    # Nesse código, None indica que o livro não foi encontrado.
    if r is None:

        # Retorna uma mensagem de erro com o código 404,
        # que indica que o recurso solicitado não foi encontrado.
        return jsonify(erro="Livro não encontrado."), 404

    # Retorna o resultado da operação e uma mensagem.
    # Se r for verdadeiro, informa que o livro foi adicionado.
    # Se r for falso, informa que o livro foi removido.
    return jsonify(favoritado=r, mensagem="Adicionado aos favoritos." if r else "Removido dos favoritos.")


# Define uma rota POST para adicionar ou atualizar
# o status de um livro na lista de leitura.
# O endereço recebe o ID do livro.
# Exemplo: /api/lista/5
@bp.post("/lista/<int:id_livro>")

# Exige que o usuário esteja logado.
@login_obrigatorio
def lista(id_livro):

    # Obtém os dados enviados pelo usuário em formato JSON.
    # get_json(silent=True) tenta interpretar os dados como JSON.
    # Se não houver dados ou ocorrer algum problema na leitura,
    # utiliza um dicionário vazio.
    # get("status", "quero_ler") busca o status enviado.
    # Se nenhum status for informado, utiliza "quero_ler" como padrão.
    status = (request.get_json(silent=True) or {}).get("status", "quero_ler")

    # Chama definir_status() para registrar ou atualizar
    # o status do livro na lista do usuário.
    # Envia o ID do usuário, o ID do livro e o status escolhido.
    # Se a operação falhar, o método retorna False.
    if not lista_dao.definir_status(session["id_usuario"], id_livro, status):

        # Retorna uma mensagem de erro com o código 400,
        # indicando que não foi possível processar a solicitação.
        return jsonify(erro="Não foi possível atualizar a lista."), 400

    # Se a operação for realizada, retorna uma mensagem de sucesso.
    # Se o status for "lido", informa que o livro foi marcado como lido.
    # Caso contrário, informa que foi adicionado à lista de leitura.
    return jsonify(mensagem="Marcado como lido!" if status == "lido" else "Adicionado à lista de leitura.")


# Define uma rota DELETE para remover um livro da lista de leitura.
# O endereço recebe o ID do livro como número inteiro.
# Exemplo: /api/lista/5
@bp.delete("/lista/<int:id_livro>")

# Exige que o usuário esteja logado.
@login_obrigatorio
def remover_lista(id_livro):

    # Chama o método remover() do ListaLeituraDAO.
    # Envia o ID do usuário conectado e o ID do livro
    # para remover esse livro da lista de leitura.
    lista_dao.remover(session["id_usuario"], id_livro)

    # Retorna uma mensagem informando que o livro foi removido.
    return jsonify(mensagem="Removido da lista.")


# Define uma rota PUT para cadastrar ou atualizar a meta de leitura.
# Endereço: /api/meta
@bp.put("/meta")

# Exige que o usuário esteja logado.
@login_obrigatorio
def meta():

    # Inicia um bloco try para tentar converter
    # a quantidade da meta recebida em um número inteiro.
    try:

        # Lê os dados enviados em JSON.
        # Busca o campo "quantidade_meta" e converte seu valor
        # para inteiro utilizando int().
        qtd = int((request.get_json(silent=True) or {}).get("quantidade_meta"))

    # Captura erros que podem acontecer durante a conversão.
    # TypeError ocorre quando o valor não pode ser convertido
    # por causa do tipo recebido.
    # ValueError ocorre quando o conteúdo não representa
    # um número inteiro válido.
    except (TypeError, ValueError):

        # Retorna uma mensagem de erro com o código 400,
        # informando que o usuário precisa fornecer um número.
        return jsonify(erro="Informe um número."), 400

    # Verifica se a quantidade informada está dentro do intervalo permitido.
    # A meta precisa ser de pelo menos 1 livro e no máximo 365 livros.
    if not 1 <= qtd <= 365:

        # Se o valor estiver fora do intervalo,
        # retorna uma mensagem de erro com o código 400.
        return jsonify(erro="A meta deve ficar entre 1 e 365 livros."), 400

    # Chama o método definir() do MetaLeituraDAO.
    # Envia o ID do usuário, o ano atual e a quantidade escolhida.
    # Assim, a meta fica vinculada ao usuário e ao ano correspondente.
    meta_dao.definir(session["id_usuario"], date.today().year, qtd)

    # Retorna uma mensagem confirmando que a meta foi salva.
    return jsonify(mensagem="Meta de leitura salva!")