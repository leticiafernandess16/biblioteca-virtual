from flask import Blueprint, request, jsonify
from dao.livro_dao import LivroDAO, AutorDAO, GeneroDAO
from dao.avaliacao_dao import AvaliacaoDAO
from dao.estatistica_dao import EstatisticaDAO
from dao.estante_dao import CuriosidadeDAO
from models.livro import Livro
from models.autor import Autor
from models.genero import Genero
from models.avaliacao import Avaliacao
from routes.auth import admin_obrigatorio, login_obrigatorio
from flask import session

bp = Blueprint("livros", __name__, url_prefix="/api")
dao, autor_dao, genero_dao, av_dao = LivroDAO(), AutorDAO(), GeneroDAO(), AvaliacaoDAO()
est_dao, cur_dao = EstatisticaDAO(), CuriosidadeDAO()


def _livro_do_json(d, id_livro=None):
    """Valida o JSON e devolve (Livro, erro)."""
    titulo = str(d.get("titulo", "")).strip()
    if not titulo:
        return None, "Informe o título."
    try:
        total = int(d.get("quantidade_total", 1))
        ano = int(d["ano_publicacao"]) if d.get("ano_publicacao") not in (None, "") else None
        id_autor, id_genero = int(d["id_autor"]), int(d["id_genero"])
    except (ValueError, KeyError, TypeError):
        return None, "Dados inválidos (autor, gênero, ano ou quantidade)."
    if total < 0:
        return None, "Quantidade inválida."
    return Livro(id_livro=id_livro, titulo=titulo, isbn=(d.get("isbn") or "").strip() or None,
                 ano_publicacao=ano, editora=d.get("editora", ""), quantidade_total=total,
                 capa_url=d.get("capa_url", ""), classificacao_indicativa=d.get("classificacao_indicativa", ""),
                 sinopse=d.get("sinopse", ""), id_autor=id_autor, id_genero=id_genero), None


@bp.get("/livros")
def listar():
    livros = dao.listar(busca=request.args.get("busca", "").strip(),
                        id_genero=request.args.get("genero", type=int),
                        somente_disponiveis=request.args.get("disponiveis") == "1",
                        ordem=request.args.get("ordem", "titulo"),
                        nota_min=request.args.get("nota_min", type=float),
                        limite=request.args.get("limite", type=int))
    return jsonify([l.to_dict() for l in livros])


@bp.get("/livros/<int:id_livro>")
def detalhe(id_livro):
    l = dao.buscar_por_id(id_livro)
    if not l:
        return jsonify(erro="Livro não encontrado."), 404
    return jsonify(livro=l.to_dict(), avaliacoes=av_dao.listar_por_livro(id_livro), nota=av_dao.media(id_livro))


@bp.post("/livros")
@admin_obrigatorio
def cadastrar():
    livro, erro = _livro_do_json(request.get_json(silent=True) or {})
    if erro:
        return jsonify(erro=erro), 400
    novo = dao.inserir(livro)
    if novo is None:
        return jsonify(erro="Não foi possível cadastrar (ISBN repetido ou autor/gênero inexistente)."), 409
    return jsonify(id_livro=novo, mensagem="Livro cadastrado."), 201


@bp.put("/livros/<int:id_livro>")
@admin_obrigatorio
def editar(id_livro):
    livro, erro = _livro_do_json(request.get_json(silent=True) or {}, id_livro)
    if erro:
        return jsonify(erro=erro), 400
    if not dao.atualizar(livro):
        return jsonify(erro="Não foi possível editar o livro."), 409
    return jsonify(mensagem="Livro atualizado.")


@bp.delete("/livros/<int:id_livro>")
@admin_obrigatorio
def excluir(id_livro):
    if not dao.excluir(id_livro):
        return jsonify(erro="Não foi possível excluir (livro inexistente ou com empréstimos)."), 409
    return jsonify(mensagem="Livro excluído.")


@bp.get("/generos")
def generos():
    return jsonify(genero_dao.listar_com_contagem())


@bp.post("/generos")
@admin_obrigatorio
def novo_genero():
    d = request.get_json(silent=True) or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify(erro="Informe o nome do gênero."), 400
    novo = genero_dao.inserir(Genero(nome=nome, descricao=d.get("descricao", "")))
    if novo is None:
        return jsonify(erro="Gênero já existe."), 409
    return jsonify(id_genero=novo), 201


@bp.get("/autores")
def autores():
    return jsonify([a.to_dict() for a in autor_dao.listar()])


@bp.post("/autores")
@admin_obrigatorio
def novo_autor():
    d = request.get_json(silent=True) or {}
    nome = d.get("nome", "").strip()
    if not nome:
        return jsonify(erro="Informe o nome do autor."), 400
    novo = autor_dao.inserir(Autor(nome=nome, nacionalidade=d.get("nacionalidade", ""), biografia=d.get("biografia", "")))
    return jsonify(id_autor=novo), 201


@bp.post("/livros/<int:id_livro>/avaliacoes")
@login_obrigatorio
def avaliar(id_livro):
    d = request.get_json(silent=True) or {}
    try:
        nota = int(d.get("nota"))
    except (TypeError, ValueError):
        return jsonify(erro="Nota inválida."), 400
    if not 1 <= nota <= 5:
        return jsonify(erro="A nota deve ser de 1 a 5."), 400
    if not dao.buscar_por_id(id_livro):
        return jsonify(erro="Livro não encontrado."), 404
    av_dao.salvar(Avaliacao(nota=nota, comentario=d.get("comentario", "")[:500],
                            id_usuario=session["id_usuario"], id_livro=id_livro))
    return jsonify(mensagem="Avaliação registrada.")


@bp.get("/estatisticas")
def estatisticas():
    return jsonify(est_dao.resumo())


@bp.get("/home")
def home():
    """Tudo que a página inicial precisa em uma única requisição."""
    dia = dao.livro_do_dia()
    cur = cur_dao.sortear()
    return jsonify(
        livro_do_dia=dia.to_dict() if dia else None,
        destaques=[l.to_dict() for l in dao.listar(ordem="avaliacao", limite=8)],
        populares=[l.to_dict() for l in dao.listar(ordem="popular", limite=8)],
        lancamentos=[l.to_dict() for l in dao.listar(ordem="recentes", limite=8)],
        generos=genero_dao.listar_com_contagem(),
        curiosidade=cur.to_dict() if cur else None,
        estatisticas=est_dao.resumo())


@bp.get("/curiosidade")
def curiosidade():
    cur = cur_dao.sortear(request.args.get("excluir", type=int))
    return jsonify(cur.to_dict() if cur else None)


@bp.get("/recomendacoes")
@login_obrigatorio
def recomendacoes():
    return jsonify([l.to_dict() for l in dao.recomendar(session["id_usuario"])])
