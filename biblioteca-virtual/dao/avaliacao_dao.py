import sqlite3
from database.conexao import get_connection
from models.avaliacao import Avaliacao


class AvaliacaoDAO:
    def salvar(self, av):
        """Insere ou atualiza a avaliação do usuário para o livro."""
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO avaliacoes (nota, comentario, id_usuario, id_livro) VALUES (?,?,?,?)
                   ON CONFLICT(id_usuario, id_livro) DO UPDATE SET nota=excluded.nota,
                   comentario=excluded.comentario, data_avaliacao=date('now')""",
                (av.nota, av.comentario, av.id_usuario, av.id_livro))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def listar_por_livro(self, id_livro):
        conn = get_connection()
        rows = conn.execute(
            """SELECT a.*, u.nome AS usuario FROM avaliacoes a JOIN usuarios u ON u.id_usuario=a.id_usuario
               WHERE a.id_livro=? ORDER BY a.id_avaliacao DESC""", (id_livro,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def media(self, id_livro):
        conn = get_connection()
        r = conn.execute("SELECT ROUND(AVG(nota),1) AS m, COUNT(*) AS n FROM avaliacoes WHERE id_livro=?", (id_livro,)).fetchone()
        conn.close()
        return {"media": r["m"], "total": r["n"]}
