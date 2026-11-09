import sqlite3
from datetime import date
from database.conexao import get_connection
from models.livro import Livro
from models.autor import Autor
from models.genero import Genero

SELECT_LIVRO = """
SELECT l.*, a.nome AS autor, g.nome AS genero,
  (SELECT ROUND(AVG(v.nota),1) FROM avaliacoes v WHERE v.id_livro = l.id_livro) AS nota_media,
  (SELECT COUNT(*) FROM avaliacoes v WHERE v.id_livro = l.id_livro) AS total_avaliacoes,
  (SELECT COUNT(*) FROM emprestimos e WHERE e.id_livro = l.id_livro) AS total_emprestimos
FROM livros l
JOIN autores a ON a.id_autor = l.id_autor
JOIN generos g ON g.id_genero = l.id_genero
"""

ORDENS = {  # whitelist: nunca concatenar texto do usuário no ORDER BY
    "titulo": "l.titulo COLLATE NOCASE",
    "popular": "total_emprestimos DESC, l.titulo",
    "avaliacao": "COALESCE(nota_media,0) DESC, total_avaliacoes DESC, l.titulo",
    "recentes": "l.ano_publicacao DESC, l.titulo",
}


class LivroDAO:
    @staticmethod
    def _montar(row):
        return Livro(**dict(row)) if row else None

    def listar(self, busca="", id_genero=None, somente_disponiveis=False,
               ordem="titulo", nota_min=None, limite=None):
        sql = SELECT_LIVRO + " WHERE 1=1"
        params = []
        if busca:
            sql += " AND (l.titulo LIKE ? OR a.nome LIKE ? OR g.nome LIKE ?)"
            params += [f"%{busca}%"] * 3
        if id_genero:
            sql += " AND l.id_genero = ?"
            params.append(id_genero)
        if somente_disponiveis:
            sql += " AND l.quantidade_disponivel > 0"
        if nota_min:
            sql += " AND COALESCE((SELECT AVG(v.nota) FROM avaliacoes v WHERE v.id_livro = l.id_livro),0) >= ?"
            params.append(nota_min)
        sql += " ORDER BY " + ORDENS.get(ordem, ORDENS["titulo"])
        if limite:
            sql += " LIMIT ?"
            params.append(int(limite))
        conn = get_connection()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [self._montar(r) for r in rows]

    def buscar_por_id(self, id_livro):
        conn = get_connection()
        row = conn.execute(SELECT_LIVRO + " WHERE l.id_livro = ?", (id_livro,)).fetchone()
        conn.close()
        return self._montar(row)

    def livro_do_dia(self):
        """Um livro diferente a cada dia (rotação pelos ids cadastrados)."""
        conn = get_connection()
        ids = [r[0] for r in conn.execute("SELECT id_livro FROM livros ORDER BY id_livro")]
        conn.close()
        if not ids:
            return None
        return self.buscar_por_id(ids[date.today().toordinal() % len(ids)])

    def recomendar(self, id_usuario, limite=6):
        """Livros dos gêneros que o usuário mais favorita/empresta/lista, ainda não vistos por ele."""
        conn = get_connection()
        generos = [r[0] for r in conn.execute("""
            SELECT id_genero FROM (
              SELECT l.id_genero FROM favoritos f JOIN livros l ON l.id_livro=f.id_livro WHERE f.id_usuario=?
              UNION ALL SELECT l.id_genero FROM emprestimos e JOIN livros l ON l.id_livro=e.id_livro WHERE e.id_usuario=?
              UNION ALL SELECT l.id_genero FROM lista_leitura s JOIN livros l ON l.id_livro=s.id_livro WHERE s.id_usuario=?)
            GROUP BY id_genero ORDER BY COUNT(*) DESC LIMIT 3""", (id_usuario,) * 3)]
        conn.close()
        if not generos:
            return self.listar(ordem="avaliacao", limite=limite)
        vistos = self._ids_vistos(id_usuario)
        candidatos = []
        for g in generos:
            candidatos += self.listar(id_genero=g, ordem="avaliacao")
        return [l for l in candidatos if l.id_livro not in vistos][:limite]

    @staticmethod
    def _ids_vistos(id_usuario):
        conn = get_connection()
        ids = {r[0] for r in conn.execute("""
            SELECT id_livro FROM favoritos WHERE id_usuario=?
            UNION SELECT id_livro FROM emprestimos WHERE id_usuario=?
            UNION SELECT id_livro FROM lista_leitura WHERE id_usuario=?""", (id_usuario,) * 3)}
        conn.close()
        return ids

    def inserir(self, livro):
        conn = get_connection()
        try:
            cur = conn.execute(
                """INSERT INTO livros (titulo, isbn, ano_publicacao, editora, quantidade_total,
                   quantidade_disponivel, capa_url, classificacao_indicativa, sinopse, id_autor, id_genero)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (livro.titulo, livro.isbn or None, livro.ano_publicacao, livro.editora,
                 livro.quantidade_total, livro.quantidade_total, livro.capa_url,
                 livro.classificacao_indicativa, livro.sinopse, livro.id_autor, livro.id_genero))
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def atualizar(self, livro):
        conn = get_connection()
        try:
            atual = conn.execute("SELECT quantidade_total, quantidade_disponivel FROM livros WHERE id_livro=?",
                                 (livro.id_livro,)).fetchone()
            if not atual:
                return False
            emprestados = atual["quantidade_total"] - atual["quantidade_disponivel"]
            nova_disp = livro.quantidade_total - emprestados
            if nova_disp < 0:
                return False  # total menor que o nº de exemplares emprestados
            conn.execute(
                """UPDATE livros SET titulo=?, isbn=?, ano_publicacao=?, editora=?, quantidade_total=?,
                   quantidade_disponivel=?, capa_url=?, classificacao_indicativa=?, sinopse=?,
                   id_autor=?, id_genero=? WHERE id_livro=?""",
                (livro.titulo, livro.isbn or None, livro.ano_publicacao, livro.editora,
                 livro.quantidade_total, nova_disp, livro.capa_url, livro.classificacao_indicativa,
                 livro.sinopse, livro.id_autor, livro.id_genero, livro.id_livro))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def excluir(self, id_livro):
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM livros WHERE id_livro = ?", (id_livro,))
            conn.commit()
            return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False  # possui empréstimos vinculados
        finally:
            conn.close()


class AutorDAO:
    def listar(self):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM autores ORDER BY nome").fetchall()
        conn.close()
        return [Autor(**dict(r)) for r in rows]

    def inserir(self, autor):
        conn = get_connection()
        cur = conn.execute("INSERT INTO autores (nome, nacionalidade, biografia) VALUES (?,?,?)",
                           (autor.nome, autor.nacionalidade, autor.biografia))
        conn.commit()
        novo = cur.lastrowid
        conn.close()
        return novo


class GeneroDAO:
    def listar(self):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM generos ORDER BY nome").fetchall()
        conn.close()
        return [Genero(**dict(r)) for r in rows]

    def listar_com_contagem(self):
        conn = get_connection()
        rows = conn.execute("""SELECT g.*, COUNT(l.id_livro) AS total_livros FROM generos g
                               LEFT JOIN livros l ON l.id_genero = g.id_genero
                               GROUP BY g.id_genero ORDER BY g.nome""").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def inserir(self, genero):
        conn = get_connection()
        try:
            cur = conn.execute("INSERT INTO generos (nome, descricao) VALUES (?,?)",
                               (genero.nome, genero.descricao))
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
