import sqlite3
from database.conexao import get_connection
from models.usuario import Usuario


class UsuarioDAO:
    @staticmethod
    def _montar(row):
        return Usuario(**dict(row)) if row else None

    def inserir(self, usuario):
        conn = get_connection()
        try:
            cur = conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?,?,?,?)",
                (usuario.nome, usuario.email, usuario.senha_hash, usuario.tipo))
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None  # e-mail já cadastrado
        finally:
            conn.close()

    def buscar_por_email(self, email):
        conn = get_connection()
        row = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        conn.close()
        return self._montar(row)

    def buscar_por_id(self, id_usuario):
        conn = get_connection()
        row = conn.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,)).fetchone()
        conn.close()
        return self._montar(row)

    def listar(self):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM usuarios ORDER BY nome").fetchall()
        conn.close()
        return [self._montar(r) for r in rows]

    def atualizar(self, id_usuario, nome, senha_hash=None):
        conn = get_connection()
        if senha_hash:
            conn.execute("UPDATE usuarios SET nome=?, senha_hash=? WHERE id_usuario=?", (nome, senha_hash, id_usuario))
        else:
            conn.execute("UPDATE usuarios SET nome=? WHERE id_usuario=?", (nome, id_usuario))
        conn.commit()
        conn.close()
