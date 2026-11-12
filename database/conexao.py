# Importa o módulo os, utilizado para verificar se o arquivo do banco de dados existe.
import os

# Importa o módulo sqlite3, responsável por trabalhar com o banco de dados SQLite.
import sqlite3
<<<<<<< HEAD

# Importa a função utilizada para gerar senhas criptografadas (hash).
from werkzeug.security import generate_password_hash

# Importa o arquivo de configurações do projeto.
=======
>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414
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


<<<<<<< HEAD
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
=======
def _banco_vazio(conn):
    return (conn.execute("SELECT COUNT(*) FROM livros").fetchone()[0] == 0
            and conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0)


def init_db():
    """Cria as tabelas (schema.sql) e, se o banco estiver vazio, insere os dados iniciais.
    Pode ser chamada quantas vezes quiser: não duplica dados. Se algo falhar no meio,
    o arquivo .db é apagado para não ficar um banco pela metade."""
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = get_connection()
    try:
        with open(config.SCHEMA_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        if not _banco_vazio(conn):
            return
        with open(config.DADOS_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    except Exception:
        conn.close()
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass
>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414
