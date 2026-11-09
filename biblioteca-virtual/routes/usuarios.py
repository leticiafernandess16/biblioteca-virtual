import re
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from dao.usuario_dao import UsuarioDAO
from models.usuario import Usuario
from routes.auth import admin_obrigatorio, login_obrigatorio

bp = Blueprint("usuarios", __name__, url_prefix="/api")
dao = UsuarioDAO()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.post("/cadastro")
def cadastro():
    d = request.get_json(silent=True) or {}
    nome, email, senha = d.get("nome", "").strip(), d.get("email", "").strip().lower(), d.get("senha", "")
    if len(nome) < 2:
        return jsonify(erro="Informe o nome."), 400
    if not EMAIL_RE.match(email):
        return jsonify(erro="E-mail inválido."), 400
    if len(senha) < 6:
        return jsonify(erro="A senha deve ter ao menos 6 caracteres."), 400
    novo = dao.inserir(Usuario(nome=nome, email=email, senha_hash=generate_password_hash(senha)))
    if novo is None:
        return jsonify(erro="E-mail já cadastrado."), 409
    return jsonify(mensagem="Conta criada! Faça login."), 201


@bp.post("/login")
def login():
    d = request.get_json(silent=True) or {}
    u = dao.buscar_por_email(d.get("email", "").strip().lower())
    if not u or not check_password_hash(u.senha_hash, d.get("senha", "")):
        return jsonify(erro="E-mail ou senha incorretos."), 401
    session["id_usuario"], session["tipo"] = u.id_usuario, u.tipo
    return jsonify(usuario=u.to_dict())


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify(mensagem="Sessão encerrada.")


@bp.get("/me")
def me():
    if "id_usuario" not in session:
        return jsonify(usuario=None)
    u = dao.buscar_por_id(session["id_usuario"])
    return jsonify(usuario=u.to_dict() if u else None)


@bp.get("/usuarios")
@admin_obrigatorio
def listar():
    return jsonify([u.to_dict() for u in dao.listar()])


@bp.put("/perfil")
@login_obrigatorio
def editar_perfil():
    d = request.get_json(silent=True) or {}
    nome, senha = d.get("nome", "").strip(), d.get("senha", "")
    if len(nome) < 2:
        return jsonify(erro="Informe o nome."), 400
    if senha and len(senha) < 6:
        return jsonify(erro="A nova senha deve ter ao menos 6 caracteres."), 400
    dao.atualizar(session["id_usuario"], nome, generate_password_hash(senha) if senha else None)
    return jsonify(mensagem="Perfil atualizado.", usuario=dao.buscar_por_id(session["id_usuario"]).to_dict())
