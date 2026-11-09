from flask import Blueprint, jsonify
from dao.estatistica_dao import EstatisticaDAO
from routes.auth import admin_obrigatorio

bp = Blueprint("administracao", __name__, url_prefix="/api/admin")


@bp.get("/painel")
@admin_obrigatorio
def painel():
    return jsonify(EstatisticaDAO().painel())
