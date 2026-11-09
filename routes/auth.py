from functools import wraps
from flask import session, jsonify


def login_obrigatorio(f):
    @wraps(f)
    def inner(*a, **kw):
        if "id_usuario" not in session:
            return jsonify(erro="Faça login para continuar."), 401
        return f(*a, **kw)
    return inner


def admin_obrigatorio(f):
    @wraps(f)
    def inner(*a, **kw):
        if "id_usuario" not in session:
            return jsonify(erro="Faça login para continuar."), 401
        if session.get("tipo") != "admin":
            return jsonify(erro="Acesso restrito ao administrador."), 403
        return f(*a, **kw)
    return inner
