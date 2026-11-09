"""Cria (ou recria) o banco de dados.

    python criar_banco.py          -> cria o banco se ainda não existir
    python criar_banco.py --reset  -> apaga e recria do zero com os dados iniciais
"""
import os
import sys
import config
from database.conexao import init_db

if "--reset" in sys.argv and os.path.exists(config.DB_PATH):
    os.remove(config.DB_PATH)
    print("Banco antigo removido.")

init_db()
print("Banco pronto em:", config.DB_PATH)