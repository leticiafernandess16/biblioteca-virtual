# Importa o módulo os, utilizado para verificar se o arquivo do banco de dados existe.
import os

# Importa o módulo sqlite3, responsável por trabalhar com o banco de dados SQLite.
import sqlite3

# Importa a função utilizada para gerar senhas criptografadas (hash).
from werkzeug.security import generate_password_hash

# Importa o arquivo de configurações do projeto.
import config


# Função responsável por abrir e configurar uma conexão com o banco de dados.
def get_connection():

    # Abre uma conexão com o banco de dados utilizando o caminho definido nas configurações.
    conn = sqlite3.connect(config.DB_PATH)

    # Permite acessar os resultados das consultas pelo nome das colunas.
    conn.row_factory = sqlite3.Row

    # Ativa a verificação das chaves estrangeiras no SQLite.
    conn.execute("PRAGMA foreign_keys = ON")

    # Retorna a conexão configurada para ser utilizada em outras funções.
    return conn


# Função responsável por criar e inicializar o banco de dados.
def init_db():

    # Verifica se o banco de dados ainda não existe.
    # Se não existir, considera que será a primeira inicialização.
    novo = not os.path.exists(config.DB_PATH)

    # Abre uma conexão com o banco de dados.
    conn = get_connection()

    # Abre o arquivo schema.sql, que contém a estrutura das tabelas do banco.
    with open(config.SCHEMA_PATH, encoding="utf-8") as f:

        # Executa os comandos SQL responsáveis por criar a estrutura do banco de dados.
        conn.executescript(f.read())

    # Verifica se o banco está sendo criado pela primeira vez.
    if novo:

        # Abre o arquivo seed.sql, que contém os dados iniciais do sistema.
        with open(config.SEED_PATH, encoding="utf-8") as f:

            # Executa os comandos SQL para inserir os dados iniciais no banco.
            conn.executescript(f.read())

        # Cria uma lista com os dados do administrador e de um usuário de demonstração.
        # As senhas são armazenadas em formato de hash para maior segurança.
        usuarios = [
            ("Administrador", "admin@biblioteca.com", generate_password_hash("admin123"), "admin"),
            ("Leitor Demo", "leitor@biblioteca.com", generate_password_hash("leitor123"), "leitor"),
        ]

        # Adiciona outros três usuários de demonstração à lista.
        usuarios += [
            ("Ana Souza", "ana@biblioteca.com", generate_password_hash("demo123"), "leitor"),
            ("Bruno Lima", "bruno@biblioteca.com", generate_password_hash("demo123"), "leitor"),
            ("Carla Dias", "carla@biblioteca.com", generate_password_hash("demo123"), "leitor"),
        ]

        # Insere todos os usuários da lista na tabela usuarios.
        # Os pontos de interrogação são substituídos pelos valores de cada usuário.
        conn.executemany(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?,?,?,?)", usuarios)

        # Abre o arquivo demo.sql, que contém dados utilizados para demonstração do sistema.
        with open(config.DEMO_PATH, encoding="utf-8") as f:

            # Executa os comandos SQL para inserir os dados de demonstração no banco.
            conn.executescript(f.read())

        # Ajusta a quantidade de livros disponíveis de acordo com os empréstimos que ainda estão abertos.
        conn.execute("""UPDATE livros SET quantidade_disponivel = quantidade_total -
            (SELECT COUNT(*) FROM emprestimos e WHERE e.id_livro = livros.id_livro
             AND e.status IN ('ativo','atrasado'))""")

        # Salva todas as alterações realizadas no banco de dados.
        conn.commit()

    # Fecha a conexão com o banco de dados após finalizar as operações.
    conn.close()