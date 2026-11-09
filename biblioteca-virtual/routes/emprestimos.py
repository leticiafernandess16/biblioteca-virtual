from flask import Blueprint, jsonify, session
from dao.emprestimo_dao import EmprestimoDAO
from routes.auth import login_obrigatorio, admin_obrigatorio

bp = Blueprint("emprestimos", __name__, url_prefix="/api")
dao = EmprestimoDAO()


@bp.post("/emprestimos/<int:id_livro>")
@login_obrigatorio
def emprestar(id_livro):
    ok, msg = dao.realizar(session["id_usuario"], id_livro)
    return (jsonify(mensagem=msg), 201) if ok else (jsonify(erro=msg), 409)


@bp.get("/emprestimos/meus")
@login_obrigatorio
def meus():
    return jsonify([e.to_dict() for e in dao.listar_por_usuario(session["id_usuario"])])


@bp.post("/emprestimos/<int:id_emprestimo>/devolver")
@login_obrigatorio
def devolver(id_emprestimo):
    dono = None if session.get("tipo") == "admin" else session["id_usuario"]
    ok, msg = dao.devolver(id_emprestimo, dono)
    return (jsonify(mensagem=msg), 200) if ok else (jsonify(erro=msg), 409)


@bp.get("/emprestimos")
@admin_obrigatorio
def todos():
    return jsonify([e.to_dict() for e in dao.listar_todos()])
