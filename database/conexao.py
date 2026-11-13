import os
import sqlite3
import config


def get_connection():
    """Abre uma conexão SQLite com chaves estrangeiras ativas."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _banco_vazio(conn):
    return (conn.execute("SELECT COUNT(*) FROM livros").fetchone()[0] == 0
            and conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0)


def init_db():
    """Cria as tabelas (schema.sql) e, se o banco estiver vazio, insere os dados iniciais.
    Pode ser chamada quantas vezes quiser: não duplica dados. Se algo falhar no meio,
    o arquivo .db é apagado para não ficar um banco pela metade."""
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = get_connection()
    try:
        with open(config.SCHEMA_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        if not _banco_vazio(conn):
            return
        with open(config.DADOS_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception:
        conn.close()
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass