from database.conexao import get_connection

conn = get_connection()
with open("capas.sql", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.commit()

total = conn.execute("SELECT COUNT(*) FROM livros").fetchone()[0]
com_capa = conn.execute(
    "SELECT COUNT(*) FROM livros WHERE capa_url IS NOT NULL AND capa_url <> ''"
).fetchone()[0]
print(f"{com_capa} de {total} livros com capa.")
conn.close()