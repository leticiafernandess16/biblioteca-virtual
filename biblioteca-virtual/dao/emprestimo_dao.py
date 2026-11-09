from datetime import date, timedelta
from database.conexao import get_connection
from models.emprestimo import Emprestimo
import config

BASE = """SELECT e.*, l.titulo, u.nome AS usuario FROM emprestimos e
          JOIN livros l ON l.id_livro = e.id_livro
          JOIN usuarios u ON u.id_usuario = e.id_usuario"""


class EmprestimoDAO:
    def _atualizar_atrasados(self, conn):
        conn.execute("UPDATE emprestimos SET status='atrasado' WHERE status='ativo' AND data_prevista_devolucao < date('now')")
        conn.commit()

    def realizar(self, id_usuario, id_livro):
        """Retorna (ok, mensagem). Controla estoque e duplicidade numa transação."""
        conn = get_connection()
        try:
            livro = conn.execute("SELECT quantidade_disponivel FROM livros WHERE id_livro=?", (id_livro,)).fetchone()
            if not livro:
                return False, "Livro não encontrado."
            if livro["quantidade_disponivel"] <= 0:
                return False, "Não há exemplares disponíveis."
            dup = conn.execute("SELECT 1 FROM emprestimos WHERE id_usuario=? AND id_livro=? AND status IN ('ativo','atrasado')",
                               (id_usuario, id_livro)).fetchone()
            if dup:
                return False, "Você já possui este livro emprestado."
            prevista = (date.today() + timedelta(days=config.DIAS_EMPRESTIMO)).isoformat()
            conn.execute("INSERT INTO emprestimos (data_prevista_devolucao, id_usuario, id_livro) VALUES (?,?,?)",
                         (prevista, id_usuario, id_livro))
            conn.execute("UPDATE livros SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id_livro=?", (id_livro,))
            conn.commit()
            return True, f"Empréstimo realizado! Devolução até {prevista}."
        except Exception:
            conn.rollback()
            return False, "Erro ao realizar empréstimo."
        finally:
            conn.close()

    def devolver(self, id_emprestimo, id_usuario=None):
        conn = get_connection()
        try:
            e = conn.execute("SELECT * FROM emprestimos WHERE id_emprestimo=?", (id_emprestimo,)).fetchone()
            if not e:
                return False, "Empréstimo não encontrado."
            if id_usuario is not None and e["id_usuario"] != id_usuario:
                return False, "Este empréstimo não é seu."
            if e["status"] == "devolvido":
                return False, "Livro já devolvido."
            conn.execute("UPDATE emprestimos SET status='devolvido', data_devolucao=date('now') WHERE id_emprestimo=?",
                         (id_emprestimo,))
            conn.execute("UPDATE livros SET quantidade_disponivel = quantidade_disponivel + 1 WHERE id_livro=?",
                         (e["id_livro"],))
            conn.commit()
            return True, "Devolução registrada."
        except Exception:
            conn.rollback()
            return False, "Erro ao registrar devolução."
        finally:
            conn.close()

    def listar_por_usuario(self, id_usuario):
        conn = get_connection()
        self._atualizar_atrasados(conn)
        rows = conn.execute(BASE + " WHERE e.id_usuario=? ORDER BY e.id_emprestimo DESC", (id_usuario,)).fetchall()
        conn.close()
        return [Emprestimo(**dict(r)) for r in rows]

    def listar_todos(self):
        conn = get_connection()
        self._atualizar_atrasados(conn)
        rows = conn.execute(BASE + " ORDER BY e.id_emprestimo DESC").fetchall()
        conn.close()
        return [Emprestimo(**dict(r)) for r in rows]
