import sqlite3

import config


def get_connection():
    """Abre uma conexão com o banco SQLite (as linhas podem ser lidas pelo nome da coluna)."""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # ativa as chaves estrangeiras no SQLite
    return conn