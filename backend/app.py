import os

# Importa as ferramentas necessárias do Flask
from flask import Flask, render_template, send_from_directory, abort

# Importa as configurações do projeto
import config

# Importa a função responsável por inicializar o banco de dados
from criar_banco import init_db

# Importa as rotas de cada funcionalidade do sistema
from routes.livros import bp as livros_bp
from routes.usuarios import bp as usuarios_bp
from routes.emprestimos import bp as emprestimos_bp
from routes.estante import bp as estante_bp
from routes.admin import bp as admin_bp


# Inicializa o banco de dados antes de iniciar a aplicação
# Garante que as tabelas e os dados iniciais estejam disponíveis
init_db()


# Cria a aplicação Flask
# template_folder: onde está o index.html | static_folder: onde estão css/ e js/
app = Flask(__name__,
            template_folder=config.TEMPLATES_DIR,
            static_folder=config.STATIC_DIR)

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
    # Renderiza o index.html (ele usa url_for para ligar o CSS e o JS)
    return render_template("index.html")


# ===== Rota para exibir as capas dos livros (opcional) =====

@app.route("/capa/<int:id_livro>")
def capa(id_livro):
    """Entrega a imagem da capa do livro de acordo com seu ID."""

    # Pasta das imagens: static/img (fora do backend)
    pasta = os.path.join(config.STATIC_DIR, "img")

    # Aceita os formatos PNG, JPG, JPEG e WEBP
    for ext in ("png", "jpg", "jpeg", "webp"):
        if os.path.exists(os.path.join(pasta, f"{id_livro}.{ext}")):
            return send_from_directory(pasta, f"{id_livro}.{ext}")

    # Caso nenhuma imagem seja encontrada, retorna o erro 404
    abort(404)


# ===== Execução da aplicação =====

if __name__ == "__main__":
    # O modo debug facilita encontrar erros durante o desenvolvimento
    app.run(debug=True)