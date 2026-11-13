"""Cria (ou recria) o banco de dados.

    python criar_banco.py          -> cria o banco se ainda não existir
    python criar_banco.py --reset  -> apaga e recria do zero com os dados iniciais
"""

import os
import sys
import config
from database.conexao import init_db


# Verifica se o comando --reset foi informado ao executar o arquivo
# Também verifica se o arquivo do banco de dados já existe
if "--reset" in sys.argv and os.path.exists(config.DB_PATH):

    # Apaga o banco de dados antigo para permitir sua recriação
    os.remove(config.DB_PATH)

    # Informa que o banco anterior foi removido
    print("Banco antigo removido.")


# Inicializa o banco de dados
# Cria as tabelas e insere os dados iniciais, se necessário
init_db()

# Exibe o caminho onde o banco de dados está armazenado
print("Banco pronto em:", config.DB_PATH)