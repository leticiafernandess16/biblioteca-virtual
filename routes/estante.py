from datetime import date
from flask import Blueprint, request, jsonify, session
from dao.estante_dao import FavoritoDAO, ListaLeituraDAO, MetaLeituraDAO
from dao.livro_dao import LivroDAO
from database.conexao import get_connection
from routes.auth import login_obrigatorio

bp = Blueprint("estante", __name__, url_prefix="/api")
fav_dao, lista_dao, meta_dao, livro_dao = FavoritoDAO(), ListaLeituraDAO(), MetaLeituraDAO(), LivroDAO()


@bp.get("/estante")
@login_obrigatorio
def estante():
    uid = session["id_usuario"]
    mapa = lista_dao.mapa(uid)
    favoritos = set(fav_dao.ids(uid))

    def com_status(ids):
        return [livro_dao.buscar_por_id(i).to_dict() for i in ids if livro_dao.buscar_por_id(i)]

    meta = meta_dao.buscar(uid, date.today().year)
    return jsonify(
        favoritos=com_status(sorted(favoritos)),
        quero_ler=com_status([i for i, s in mapa.items() if s == "quero_ler"]),
        lidos=com_status([i for i, s in mapa.items() if s == "lido"]),
        ids_favoritos=sorted(favoritos), lista=mapa,
        meta=meta.to_dict() if meta else None, ano=date.today().year)


@bp.post("/favoritos/<int:id_livro>")
@login_obrigatorio
def favoritar(id_livro):
    r = fav_dao.alternar(session["id_usuario"], id_livro)
    if r is None:
        return jsonify(erro="Livro não encontrado."), 404
    return jsonify(favoritado=r, mensagem="Adicionado aos favoritos." if r else "Removido dos favoritos.")


@bp.post("/lista/<int:id_livro>")
@login_obrigatorio
def lista(id_livro):
    status = (request.get_json(silent=True) or {}).get("status", "quero_ler")
    if not lista_dao.definir_status(session["id_usuario"], id_livro, status):
        return jsonify(erro="Não foi possível atualizar a lista."), 400
    return jsonify(mensagem="Marcado como lido!" if status == "lido" else "Adicionado à lista de leitura.")


@bp.delete("/lista/<int:id_livro>")
@login_obrigatorio
def remover_lista(id_livro):
    lista_dao.remover(session["id_usuario"], id_livro)
    return jsonify(mensagem="Removido da lista.")


@bp.put("/meta")
@login_obrigatorio
def meta():
    try:
        qtd = int((request.get_json(silent=True) or {}).get("quantidade_meta"))
    except (TypeError, ValueError):
        return jsonify(erro="Informe um número."), 400
    if not 1 <= qtd <= 365:
        return jsonify(erro="A meta deve ficar entre 1 e 365 livros."), 400
    meta_dao.definir(session["id_usuario"], date.today().year, qtd)
    return jsonify(mensagem="Meta de leitura salva!")
