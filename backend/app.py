import os
import sys

# Pasta do backend (onde ficam config, dao, models e routes).
BASE = os.path.dirname(os.path.abspath(__file__))

# Pasta principal do projeto (um nível acima de backend/).
# Permite importar a pasta database/ e encontrar o static e o index.html.
RAIZ = os.path.dirname(BASE)

# Garante que os imports funcionem tanto com "python backend/app.py"
# quanto com "python -m backend.app" (executado a partir da raiz).
# O backend tem prioridade; a raiz fica como fallback para a pasta database/.
if BASE not in sys.path:
    sys.path.insert(0, BASE)
if RAIZ not in sys.path:
    sys.path.append(RAIZ)

# Importa as ferramentas necessárias do Flask
from flask import Flask, send_from_directory, abort

# Importa as configurações do projeto
import config

# Importa a função responsável por inicializar o banco de dados
from database.conexao import init_db

# Importa as rotas de cada funcionalidade do sistema
from routes.livros import bp as livros_bp
from routes.usuarios import bp as usuarios_bp
from routes.emprestimos import bp as emprestimos_bp
from routes.estante import bp as estante_bp
from routes.administracao import bp as admin_bp


# Inicializa o banco de dados antes de iniciar a aplicação
# Garante que as tabelas e os dados iniciais estejam disponíveis
# Independentemente da forma como o sistema for executado
init_db()


# Cria a aplicação Flask
# static_folder aponta para a pasta static, que fica fora do backend
app = Flask(__name__, static_folder=os.path.join(RAIZ, "static"))

# Define a chave secreta utilizada pelo Flask para proteger sessões
app.secret_key = config.SECRET_KEY


# Registra as rotas de cada parte do sistema na aplicação
app.register_blueprint(livros_bp)       # Rotas relacionadas aos livros
app.register_blueprint(usuarios_bp)     # Rotas relacionadas aos usuários
app.register_blueprint(emprestimos_bp)  # Rotas relacionadas aos empréstimos
app.register_blueprint(estante_bp)      # Rotas relacionadas à estante do usuário
app.register_blueprint(admin_bp)        # Rotas da área administrativa


# ===== Rota da página inicial =====

@app.route("/")
def index():
    # Envia o arquivo index.html (que fica na pasta principal) quando o usuário acessa a página inicial
    return send_from_directory(RAIZ, "index.html")


# ===== Rota para exibir as capas dos livros =====

@app.route("/capa/<int:id_livro>")
def capa(id_livro):
    """Entrega a imagem da capa do livro de acordo com seu ID."""

    # Define o caminho da pasta onde as imagens das capas estão armazenadas
    pasta = os.path.join(RAIZ, "static", "img")

    # Verifica se existe uma imagem com o ID do livro
    # Aceita os formatos PNG, JPG, JPEG e WEBP
    for ext in ("png", "jpg", "jpeg", "webp"):

        # Monta o caminho completo da imagem
        if os.path.exists(os.path.join(pasta, f"{id_livro}.{ext}")):

            # Envia a imagem encontrada para o navegador
            return send_from_directory(pasta, f"{id_livro}.{ext}")

    # Caso nenhuma imagem seja encontrada, retorna o erro 404
    abort(404)


# ===== Execução da aplicação =====

if __name__ == "__main__":

    # Inicia o servidor Flask em modo de depuração
    # O modo debug facilita encontrar erros durante o desenvolvimento
    app.run(debug=True)