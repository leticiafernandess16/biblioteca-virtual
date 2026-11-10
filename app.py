from flask import Flask, render_template  # Importa Flask para criar a aplicação e render_template para carregar páginas HTML.
import config  # Importa o arquivo de configurações do projeto.
from database.conexao import init_db  # Importa a função responsável por inicializar o banco de dados.
from routes.livros import bp as livros_bp  # Importa as rotas relacionadas aos livros.
from routes.usuarios import bp as usuarios_bp  # Importa as rotas relacionadas aos usuários.
from routes.emprestimos import bp as emprestimos_bp  # Importa as rotas relacionadas aos empréstimos.
from routes.estante import bp as estante_bp  # Importa as rotas relacionadas à estante pessoal.
from routes.administracao import bp as admin_bp  # Importa as rotas da área de administração.

# Cria a aplicação Flask.
app = Flask(__name__)

# Define a chave secreta da aplicação, utilizada para proteger sessões.
app.secret_key = config.SECRET_KEY

# Registra o conjunto de rotas responsável pelas operações com livros.
app.register_blueprint(livros_bp)

# Registra o conjunto de rotas responsável pelas operações com usuários.
app.register_blueprint(usuarios_bp)

# Registra o conjunto de rotas responsável pelos empréstimos.
app.register_blueprint(emprestimos_bp)

# Registra o conjunto de rotas responsável pela estante pessoal dos usuários.
app.register_blueprint(estante_bp)

# Registra o conjunto de rotas da área administrativa.
app.register_blueprint(admin_bp)


# Define a rota principal do sistema, acessada pelo endereço "/".
@app.route("/")
def index():
    # Renderiza e exibe a página inicial do sistema.
    return render_template("index.html")


# Verifica se este arquivo está sendo executado diretamente.
if __name__ == "__main__":
    # Inicializa o banco de dados antes de iniciar o servidor.
    init_db()

    # Inicia o servidor Flask com o modo de depuração ativado.
    app.run(debug=True)