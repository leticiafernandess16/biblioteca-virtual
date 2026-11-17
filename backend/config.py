import os  # Importa o módulo os para trabalhar com caminhos e diretórios do sistema.

# Define o caminho absoluto da pasta principal do projeto.
# Este arquivo está dentro de backend/, então sobe um nível para chegar na pasta principal.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define o caminho do banco de dados SQLite utilizado pela biblioteca.
DB_PATH = os.path.join(BASE_DIR, "database", "biblioteca.db")

# Define o caminho do arquivo SQL responsável pela criação da estrutura do banco de dados.
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Define o caminho do arquivo SQL que contém os dados gerais do sistema.
DADOS_PATH = os.path.join(BASE_DIR, "database", "dados.sql")

# Define a chave secreta utilizada para proteger sessões e outros recursos da aplicação.
# Em ambiente de produção, deve ser substituída por uma chave segura e privada.
SECRET_KEY = "troque-esta-chave-em-producao"

# Define a quantidade de dias permitida para cada empréstimo de livro.
DIAS_EMPRESTIMO = 14