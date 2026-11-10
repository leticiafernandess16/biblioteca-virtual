# Importa date para trabalhar com datas e timedelta para calcular períodos de tempo.
from datetime import date, timedelta

# Importa a função responsável por criar a conexão com o banco de dados.
from database.conexao import get_connection

# Importa a classe Emprestimo, que representa os dados de um empréstimo.
from models.emprestimo import Emprestimo

# Importa o arquivo de configurações do sistema.
import config


# Consulta SQL base que busca os empréstimos junto com os títulos dos livros
# e os nomes dos usuários relacionados a cada empréstimo.
BASE = """SELECT e.*, l.titulo, u.nome AS usuario FROM emprestimos e
          JOIN livros l ON l.id_livro = e.id_livro
          JOIN usuarios u ON u.id_usuario = e.id_usuario"""


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas aos empréstimos.
class EmprestimoDAO:

    # Método responsável por atualizar o status dos empréstimos que estão atrasados.
    def _atualizar_atrasados(self, conn):

        # Altera o status para "atrasado" quando a data prevista de devolução já passou
        # e o empréstimo ainda está com o status "ativo".
        conn.execute("UPDATE emprestimos SET status='atrasado' WHERE status='ativo' AND data_prevista_devolucao < date('now')")

        # Salva a alteração realizada no banco de dados.
        conn.commit()

    # Método responsável por realizar um empréstimo de livro para um usuário.
    def realizar(self, id_usuario, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Busca a quantidade de exemplares disponíveis do livro informado.
            livro = conn.execute("SELECT quantidade_disponivel FROM livros WHERE id_livro=?", (id_livro,)).fetchone()

            # Verifica se o livro existe no banco de dados.
            if not livro:
                return False, "Livro não encontrado."

            # Verifica se ainda existem exemplares disponíveis para empréstimo.
            if livro["quantidade_disponivel"] <= 0:
                return False, "Não há exemplares disponíveis."

            # Verifica se o usuário já possui o mesmo livro emprestado
            # com status ativo ou atrasado.
            dup = conn.execute("SELECT 1 FROM emprestimos WHERE id_usuario=? AND id_livro=? AND status IN ('ativo','atrasado')",
                               (id_usuario, id_livro)).fetchone()

            # Impede que o usuário realize outro empréstimo do mesmo livro
            # enquanto ainda não devolver o exemplar anterior.
            if dup:
                return False, "Você já possui este livro emprestado."

            # Calcula a data prevista para a devolução,
            # utilizando a quantidade de dias definida nas configurações.
            prevista = (date.today() + timedelta(days=config.DIAS_EMPRESTIMO)).isoformat()

            # Insere um novo empréstimo no banco de dados com a data prevista,
            # o ID do usuário e o ID do livro.
            conn.execute("INSERT INTO emprestimos (data_prevista_devolucao, id_usuario, id_livro) VALUES (?,?,?)",
                         (prevista, id_usuario, id_livro))

            # Diminui em uma unidade a quantidade de exemplares disponíveis do livro.
            conn.execute("UPDATE livros SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id_livro=?", (id_livro,))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True e uma mensagem informando que o empréstimo foi realizado
            # e indicando a data limite para devolução.
            return True, f"Empréstimo realizado! Devolução até {prevista}."

        # Captura qualquer erro que aconteça durante a realização do empréstimo.
        except Exception:

            # Desfaz as alterações realizadas caso ocorra algum erro.
            conn.rollback()

            # Retorna False e uma mensagem informando que houve um erro.
            return False, "Erro ao realizar empréstimo."

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por registrar a devolução de um livro emprestado.
    def devolver(self, id_emprestimo, id_usuario=None):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Busca os dados do empréstimo utilizando seu identificador.
            e = conn.execute("SELECT * FROM emprestimos WHERE id_emprestimo=?", (id_emprestimo,)).fetchone()

            # Verifica se o empréstimo existe no banco de dados.
            if not e:
                return False, "Empréstimo não encontrado."

            # Verifica se foi informado um usuário e se ele é o responsável pelo empréstimo.
            if id_usuario is not None and e["id_usuario"] != id_usuario:
                return False, "Este empréstimo não é seu."

            # Verifica se o livro já foi devolvido anteriormente.
            if e["status"] == "devolvido":
                return False, "Livro já devolvido."

            # Atualiza o status do empréstimo para "devolvido"
            # e registra a data atual como data da devolução.
            conn.execute("UPDATE emprestimos SET status='devolvido', data_devolucao=date('now') WHERE id_emprestimo=?",
                         (id_emprestimo,))

            # Aumenta em uma unidade a quantidade de exemplares disponíveis do livro devolvido.
            conn.execute("UPDATE livros SET quantidade_disponivel = quantidade_disponivel + 1 WHERE id_livro=?",
                         (e["id_livro"],))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True e uma mensagem confirmando o registro da devolução.
            return True, "Devolução registrada."

        # Captura qualquer erro que aconteça durante o registro da devolução.
        except Exception:

            # Desfaz as alterações realizadas caso ocorra algum erro.
            conn.rollback()

            # Retorna False e uma mensagem informando que houve um erro.
            return False, "Erro ao registrar devolução."

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por listar todos os empréstimos de um usuário específico.
    def listar_por_usuario(self, id_usuario):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Atualiza o status dos empréstimos que já passaram da data prevista de devolução.
        self._atualizar_atrasados(conn)

        # Busca os empréstimos do usuário informado,
        # organizando os resultados do mais recente para o mais antigo.
        rows = conn.execute(BASE + " WHERE e.id_usuario=? ORDER BY e.id_emprestimo DESC", (id_usuario,)).fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados em objetos da classe Emprestimo e retorna uma lista.
        return [Emprestimo(**dict(r)) for r in rows]

    # Método responsável por listar todos os empréstimos cadastrados no sistema.
    def listar_todos(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Atualiza o status dos empréstimos que já passaram da data prevista de devolução.
        self._atualizar_atrasados(conn)

        # Busca todos os empréstimos cadastrados,
        # organizando os resultados do mais recente para o mais antigo.
        rows = conn.execute(BASE + " ORDER BY e.id_emprestimo DESC").fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados em objetos da classe Emprestimo e retorna uma lista.
        return [Emprestimo(**dict(r)) for r in rows]