from urllib.parse import quote_plus
from database.conexao import get_connection

PASTA = "/static/img/"

# Quando tiver os PNGs, preencha: id do livro -> nome do arquivo em static/IMG
# Exemplo: 1: "dom-casmurro.png"
CAPAS_LOCAIS = {
    # 1: "dom-casmurro.png",
    # 2: "harry-potter.png",
}

conn = get_connection()
livros = conn.execute("SELECT id_livro, titulo, capa_url FROM livros").fetchall()

for l in livros:
    id_livro, titulo, atual = l["id_livro"], l["titulo"], l["capa_url"] or ""

    if id_livro in CAPAS_LOCAIS:
        novo = PASTA + CAPAS_LOCAIS[id_livro]
    elif not atual or "placehold.co" in atual:
        # link provisório: imagem com o título, para você trocar depois
        novo = f"https://placehold.co/300x450/png?text={quote_plus(titulo)}"
    else:
        continue  # já tem um link próprio, não mexe

    conn.execute("UPDATE livros SET capa_url = ? WHERE id_livro = ?", (novo, id_livro))
    print(f"{id_livro} - {titulo}: {novo}")

conn.commit()
conn.close()