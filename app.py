<<<<<<< HEAD
from flask import Flask, render_template  # Importa Flask para criar a aplicação e render_template para carregar páginas HTML.
import config  # Importa o arquivo de configurações do projeto.
from database.conexao import init_db  # Importa a função responsável por inicializar o banco de dados.
from routes.livros import bp as livros_bp  # Importa as rotas relacionadas aos livros.
from routes.usuarios import bp as usuarios_bp  # Importa as rotas relacionadas aos usuários.
from routes.emprestimos import bp as emprestimos_bp  # Importa as rotas relacionadas aos empréstimos.
from routes.estante import bp as estante_bp  # Importa as rotas relacionadas à estante pessoal.
from routes.administracao import bp as admin_bp  # Importa as rotas da área de administração.

# Cria a aplicação Flask.
=======
from flask import Flask, send_from_directory
import config
from database.conexao import init_db
from routes.livros import bp as livros_bp
from routes.usuarios import bp as usuarios_bp
from routes.emprestimos import bp as emprestimos_bp
from routes.estante import bp as estante_bp
from routes.administracao import bp as admin_bp

init_db()  # garante o banco em qualquer forma de execução (python app.py, flask run, gunicorn)

>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414
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
<<<<<<< HEAD
    # Renderiza e exibe a página inicial do sistema.
    return render_template("index.html")
=======
    return send_from_directory(app.root_path, "index.html")
>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414


# Verifica se este arquivo está sendo executado diretamente.
if __name__ == "__main__":
<<<<<<< HEAD
    # Inicializa o banco de dados antes de iniciar o servidor.
    init_db()

    # Inicia o servidor Flask com o modo de depuração ativado.
=======
>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414
    app.run(debug=True)