import os  # Importa o módulo os para trabalhar com caminhos e diretórios do sistema.

# Pasta onde este arquivo está (backend/).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Pasta principal do projeto (um nível acima de backend/).
RAIZ_DIR = os.path.dirname(BASE_DIR)

# Pasta do banco de dados (fica fora do backend, na pasta principal).
DATABASE_DIR = os.path.join(RAIZ_DIR, "database")

# Caminho do banco de dados SQLite utilizado pela biblioteca.
DATABASE_PATH = os.path.join(DATABASE_DIR, "biblioteca.db")
DB_PATH = DATABASE_PATH  # apelido, caso algum arquivo ainda use o nome antigo

# Arquivo SQL responsável pela criação da estrutura (tabelas) do banco de dados.
SCHEMA_PATH = os.path.join(DATABASE_DIR, "schema.sql")

# Arquivo SQL que contém os dados iniciais do sistema (livros, autores, usuários...).
SEED_PATH = os.path.join(DATABASE_DIR, "seed.sql")

# Front-end: index.html solto na pasta principal e a pasta static ao lado dele.
TEMPLATES_DIR = RAIZ_DIR
STATIC_DIR = os.path.join(RAIZ_DIR, "static")

# Chave secreta utilizada para proteger as sessões (login).
# Em ambiente de produção, deve ser substituída por uma chave segura e privada.
SECRET_KEY = "troque-esta-chave-em-producao"

# Quantidade de dias permitida para cada empréstimo de livro.
DIAS_EMPRESTIMO = 14