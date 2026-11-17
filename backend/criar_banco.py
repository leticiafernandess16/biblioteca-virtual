"""Cria (ou recria) o banco de dados.

    python criar_banco.py          -> cria o banco se ainda não existir
    python criar_banco.py --reset  -> apaga e recria do zero com os dados iniciais
"""

import os
import sys

# Pasta do backend (onde ficam config, dao, models e routes).
BASE = os.path.dirname(os.path.abspath(__file__))

# Pasta principal do projeto (um nível acima de backend/).
# Permite importar a pasta database/, que fica fora do backend.
RAIZ = os.path.dirname(BASE)

# Garante que os imports funcionem tanto com "python backend/criar_banco.py"
# quanto com "python -m backend.criar_banco" (executado a partir da raiz).
# O backend tem prioridade; a raiz fica como fallback para a pasta database/.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
if RAIZ not in sys.path:
    sys.path.append(RAIZ)

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