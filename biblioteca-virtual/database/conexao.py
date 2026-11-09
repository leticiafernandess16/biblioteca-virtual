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


def init_db():
    """Cria o banco a partir do schema.sql e popula com seed.sql (só na 1ª vez)."""
    novo = not os.path.exists(config.DB_PATH)
    conn = get_connection()
    with open(config.SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    if novo:
        with open(config.SEED_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        usuarios = [
            ("Administrador", "admin@biblioteca.com", generate_password_hash("admin123"), "admin"),
            ("Leitor Demo", "leitor@biblioteca.com", generate_password_hash("leitor123"), "leitor"),
        ]
        usuarios += [
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
    conn.close()
