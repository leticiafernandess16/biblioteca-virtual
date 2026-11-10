from flask import Flask, send_from_directory
import config
from database.conexao import init_db
from routes.livros import bp as livros_bp
from routes.usuarios import bp as usuarios_bp
from routes.emprestimos import bp as emprestimos_bp
from routes.estante import bp as estante_bp
from routes.administracao import bp as admin_bp

init_db()  # garante o banco em qualquer forma de execução (python app.py, flask run, gunicorn)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(livros_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(emprestimos_bp)
app.register_blueprint(estante_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def index():
    return send_from_directory(app.root_path, "index.html")


if __name__ == "__main__":
    app.run(debug=True)