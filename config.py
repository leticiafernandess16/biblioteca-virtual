import os  # Importa o módulo os para trabalhar com caminhos e diretórios do sistema.

# Define o caminho absoluto da pasta onde este arquivo Python está localizado.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define o caminho do banco de dados SQLite utilizado pela biblioteca.
DB_PATH = os.path.join(BASE_DIR, "database", "biblioteca.db")

# Define o caminho do arquivo SQL responsável pela criação da estrutura do banco de dados.
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Define o caminho do arquivo SQL que contém os dados iniciais do sistema.
SEED_PATH = os.path.join(BASE_DIR, "database", "seed.sql")

# Define a chave secreta utilizada para proteger sessões e outros recursos da aplicação.
# Em ambiente de produção, deve ser substituída por uma chave segura e privada.
SECRET_KEY = "troque-esta-chave-em-producao"

# Define a quantidade de dias permitida para cada empréstimo de livro.
DIAS_EMPRESTIMO = 14

# Define o caminho do arquivo SQL que contém os dados utilizados na demonstração do sistema.
DEMO_PATH = os.path.join(BASE_DIR, "database", "demo.sql")