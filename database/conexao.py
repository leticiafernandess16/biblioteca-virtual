import os
import sqlite3
from werkzeug.security import generate_password_hash
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
        with open(config.SEED_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        usuarios = [
            ("Administrador", "admin@biblioteca.com", generate_password_hash("admin123"), "admin"),
            ("Leitor Demo", "leitor@biblioteca.com", generate_password_hash("leitor123"), "leitor"),
            ("Ana Souza", "ana@biblioteca.com", generate_password_hash("demo123"), "leitor"),
            ("Bruno Lima", "bruno@biblioteca.com", generate_password_hash("demo123"), "leitor"),
            ("Carla Dias", "carla@biblioteca.com", generate_password_hash("demo123"), "leitor"),
        ]
        conn.executemany(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?,?,?,?)", usuarios)
        with open(config.DEMO_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        # ajusta a disponibilidade de acordo com os empréstimos em aberto
        conn.execute("""UPDATE livros SET quantidade_disponivel = quantidade_total -
            (SELECT COUNT(*) FROM emprestimos e WHERE e.id_livro = livros.id_livro
             AND e.status IN ('ativo','atrasado'))""")
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