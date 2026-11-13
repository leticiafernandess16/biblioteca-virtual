import os
import sqlite3
import config


def get_connection():
    """Abre uma conexão com o banco de dados SQLite."""

    # Conecta ao banco de dados usando o caminho definido no arquivo config
    conn = sqlite3.connect(config.DB_PATH)

    # Permite acessar os dados pelo nome das colunas
    conn.row_factory = sqlite3.Row

    # Ativa a verificação das chaves estrangeiras
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def _banco_vazio(conn):
    # Verifica se as tabelas livros e usuarios estão vazias
    # Retorna True somente se as duas tabelas não tiverem registros
    return (conn.execute("SELECT COUNT(*) FROM livros").fetchone()[0] == 0
            and conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0)


def init_db():
    """Cria as tabelas e insere os dados iniciais, caso o banco esteja vazio."""

    # Cria a pasta onde o banco de dados será armazenado, caso ela não exista
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)

    # Abre a conexão com o banco de dados
    conn = get_connection()

    try:
        # Abre o arquivo schema.sql, que contém a criação das tabelas
        with open(config.SCHEMA_PATH, encoding="utf-8") as f:

            # Executa os comandos SQL do arquivo
            conn.executescript(f.read())

        # Verifica se o banco já possui dados
        # Se não estiver vazio, encerra a função para evitar duplicações
        if not _banco_vazio(conn):
            return

        # Abre o arquivo que contém os dados iniciais
        with open(config.DADOS_PATH, encoding="utf-8") as f:

            # Executa os comandos SQL para inserir os dados
            conn.executescript(f.read())

        # Salva as alterações realizadas no banco
        conn.commit()

    except Exception:
        # Fecha a conexão caso aconteça algum erro
        conn.close()

        # Verifica se o arquivo do banco existe
        if os.path.exists(config.DB_PATH):

            # Apaga o banco para evitar que fique incompleto
            os.remove(config.DB_PATH)

        # Mostra novamente o erro que aconteceu
        raise

    finally:
        # Garante que a conexão seja fechada ao final da execução
        try:
            conn.close()
        except Exception:
            pass