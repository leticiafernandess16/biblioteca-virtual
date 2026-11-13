# Importa o módulo sqlite3 para trabalhar com erros e operações do banco de dados SQLite.
import sqlite3

# Importa a função responsável por criar a conexão com o banco de dados.
from database.conexao import get_connection

# Importa a classe Avaliacao, que representa os dados de uma avaliação.
from models.avaliacao import Avaliacao


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas às avaliações.
class AvaliacaoDAO:

    # Método responsável por salvar uma avaliação no banco de dados.
    def salvar(self, av):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Insere uma nova avaliação ou atualiza uma avaliação já existente
            # para o mesmo usuário e livro.
            conn.execute(
                """INSERT INTO avaliacoes (nota, comentario, id_usuario, id_livro) VALUES (?,?,?,?)
                   ON CONFLICT(id_usuario, id_livro) DO UPDATE SET nota=excluded.nota,
                   comentario=excluded.comentario, data_avaliacao=date('now')""",

                # Envia os dados da avaliação para preencher os campos da consulta SQL.
                (av.nota, av.comentario, av.id_usuario, av.id_livro))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True indicando que a avaliação foi salva com sucesso.
            return True

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna False indicando que não foi possível salvar a avaliação.
            return False

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por listar todas as avaliações de um determinado livro.
    def listar_por_livro(self, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca as avaliações do livro e os nomes dos usuários que fizeram cada avaliação.
        # O JOIN relaciona as tabelas avaliacoes e usuarios pelo ID do usuário.
        # Os resultados são organizados da avaliação mais recente para a mais antiga.
        rows = conn.execute(
            """SELECT a.*, u.nome AS usuario FROM avaliacoes a JOIN usuarios u ON u.id_usuario=a.id_usuario
               WHERE a.id_livro=? ORDER BY a.id_avaliacao DESC""", (id_livro,)).fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados da consulta em uma lista de dicionários e retorna os dados.
        return [dict(r) for r in rows]

    # Método responsável por calcular a média das notas de um determinado livro.
    def media(self, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Calcula a média das notas do livro, arredondando para uma casa decimal.
        # Também conta quantas avaliações foram realizadas.
        r = conn.execute("SELECT ROUND(AVG(nota),1) AS m, COUNT(*) AS n FROM avaliacoes WHERE id_livro=?", (id_livro,)).fetchone()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna um dicionário contendo a média das avaliações e a quantidade total.
        return {"media": r["m"], "total": r["n"]}