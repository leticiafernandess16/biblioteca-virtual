"""Exporta os dados do SQLite para o modo de demonstração estático.

O GitHub Pages não executa Python/Flask, então o site publicado usa uma
cópia dos dados do banco em JavaScript. Este script gera os arquivos:

    static/demo/dados.json  -> dados legíveis (referência)
    static/demo/dados.js    -> dados carregados pelo navegador

Execute a partir da raiz do projeto:

    python backend/exportar_demo.py
"""

import json
import os
import sys
from datetime import datetime

# Pasta do backend (onde ficam config, dao, models e routes).
BASE = os.path.dirname(os.path.abspath(__file__))

# Pasta principal do projeto (um nível acima de backend/).
RAIZ = os.path.dirname(BASE)

# Garante que os imports funcionem tanto com "python backend/exportar_demo.py"
# quanto com "python -m backend.exportar_demo" (executado a partir da raiz).
if BASE not in sys.path:
    sys.path.insert(0, BASE)
if RAIZ not in sys.path:
    sys.path.append(RAIZ)

import config
from database.conexao import get_connection


# Versão do formato dos dados. Ao alterar a estrutura exportada, aumente este
# número para que o navegador descarte dados antigos salvos no localStorage.
VERSAO_DEMO = 1

# Senhas usadas apenas na demonstração (os hashes reais nunca são exportados).
SENHAS_DEMO = {
    "admin@biblioteca.com": "admin123",
    "leitor@biblioteca.com": "leitor123",
    "ana@biblioteca.com": "demo123",
    "bruno@biblioteca.com": "demo123",
    "carla@biblioteca.com": "demo123",
}

# Pasta onde os arquivos do modo demonstração serão gravados.
PASTA_DEMO = os.path.join(RAIZ, "static", "demo")

# Pasta das capas locais dos livros.
PASTA_IMG = os.path.join(RAIZ, "static", "img")

# Extensões aceitas para localizar a capa de cada livro.
EXTENSOES = ("png", "jpg", "jpeg", "webp")


def consultar(conn, sql):
    """Executa uma consulta e devolve uma lista de dicionários."""

    return [dict(linha) for linha in conn.execute(sql)]


def capa_local(id_livro):
    """Devolve o caminho relativo da capa local do livro, se ela existir."""

    for ext in EXTENSOES:
        nome = f"{id_livro}.{ext}"
        if os.path.exists(os.path.join(PASTA_IMG, nome)):
            return f"static/img/{nome}"
    return ""


def montar_dados():
    """Lê o banco e monta o dicionário exportado para o modo demonstração."""

    if not os.path.exists(config.DB_PATH):
        raise SystemExit(
            "Banco de dados não encontrado em "
            f"{config.DB_PATH}. Rode 'python backend/criar_banco.py' primeiro."
        )

    conn = get_connection()

    try:
        usuarios = consultar(
            conn,
            "SELECT id_usuario, nome, email, tipo, data_cadastro "
            "FROM usuarios ORDER BY id_usuario",
        )

        # A senha em texto puro existe somente na demonstração. Contas criadas
        # pelo próprio visitante também guardam a senha no navegador.
        for usuario in usuarios:
            usuario["senha"] = SENHAS_DEMO.get(usuario["email"].lower(), "")

        livros = consultar(conn, "SELECT * FROM livros ORDER BY id_livro")
        for livro in livros:
            livro["capa_demo"] = capa_local(livro["id_livro"])

        return {
            "versao": VERSAO_DEMO,
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "dias_emprestimo": config.DIAS_EMPRESTIMO,
            "usuarios": usuarios,
            "autores": consultar(conn, "SELECT * FROM autores ORDER BY nome"),
            "generos": consultar(conn, "SELECT * FROM generos ORDER BY nome"),
            "livros": livros,
            "emprestimos": consultar(
                conn, "SELECT * FROM emprestimos ORDER BY id_emprestimo"
            ),
            "avaliacoes": consultar(
                conn, "SELECT * FROM avaliacoes ORDER BY id_avaliacao"
            ),
            "favoritos": consultar(
                conn, "SELECT * FROM favoritos ORDER BY id_favorito"
            ),
            "lista_leitura": consultar(
                conn, "SELECT * FROM lista_leitura ORDER BY id_lista"
            ),
            "metas_leitura": consultar(
                conn, "SELECT * FROM metas_leitura ORDER BY id_meta"
            ),
            "curiosidades": consultar(
                conn, "SELECT * FROM curiosidades ORDER BY id_curiosidade"
            ),
        }

    finally:
        conn.close()


def gravar_arquivos(dados):
    """Grava os dados em JSON e em JavaScript (para abrir até via file://)."""

    os.makedirs(PASTA_DEMO, exist_ok=True)

    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    caminho_json = os.path.join(PASTA_DEMO, "dados.json")

    with open(caminho_json, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(texto + "\n")

    # A versão .js permite carregar os dados com uma tag <script>, sem fetch.
    # Isso evita bloqueios de CORS quando o index.html é aberto via file://.
    texto_js = texto.replace("</", "<\\/")
    caminho_js = os.path.join(PASTA_DEMO, "dados.js")

    with open(caminho_js, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(
            "// Arquivo gerado automaticamente por backend/exportar_demo.py.\n"
            "// Não edite manualmente: altere o banco e rode o exportador de novo.\n"
            f"window.DADOS_DEMO = {texto_js};\n"
        )

    return caminho_json, caminho_js


def main():
    """Executa a exportação e mostra um resumo no terminal."""

    dados = montar_dados()
    caminho_json, caminho_js = gravar_arquivos(dados)

    print("Dados de demonstracao exportados:")
    print(f"  {caminho_json}")
    print(f"  {caminho_js}")
    print(
        "  "
        f"{len(dados['livros'])} livros, "
        f"{len(dados['usuarios'])} usuarios, "
        f"{len(dados['emprestimos'])} emprestimos, "
        f"{len(dados['avaliacoes'])} avaliacoes."
    )


if __name__ == "__main__":
    main()
