import sqlite3
from datetime import date
from database.conexao import get_connection
from models.favorito import Favorito
from models.lista_leitura import ListaLeitura
from models.meta_leitura import MetaLeitura
from models.curiosidade import Curiosidade


class FavoritoDAO:
    def alternar(self, id_usuario, id_livro):
        """Adiciona se não existe, remove se existe. Retorna True se ficou favoritado."""
        conn = get_connection()
        try:
            existe = conn.execute("SELECT id_favorito FROM favoritos WHERE id_usuario=? AND id_livro=?",
                                  (id_usuario, id_livro)).fetchone()
            if existe:
                conn.execute("DELETE FROM favoritos WHERE id_favorito=?", (existe["id_favorito"],))
                favoritado = False
            else:
                conn.execute("INSERT INTO favoritos (id_usuario, id_livro) VALUES (?,?)", (id_usuario, id_livro))
                favoritado = True
            conn.commit()
            return favoritado
        except sqlite3.IntegrityError:
            return None  # livro inexistente
        finally:
            conn.close()

    def ids(self, id_usuario):
        conn = get_connection()
        r = [x[0] for x in conn.execute("SELECT id_livro FROM favoritos WHERE id_usuario=?", (id_usuario,))]
        conn.close()
        return r


class ListaLeituraDAO:
    def definir_status(self, id_usuario, id_livro, status):
        """Cria ou atualiza o item da lista. 'lido' registra a data de leitura."""
        if status not in ("quero_ler", "lido"):
            return False
        data = date.today().isoformat() if status == "lido" else None
        conn = get_connection()
        try:
            conn.execute("""INSERT INTO lista_leitura (status, data_leitura, id_usuario, id_livro) VALUES (?,?,?,?)
                            ON CONFLICT(id_usuario, id_livro) DO UPDATE SET status=excluded.status,
                            data_leitura=excluded.data_leitura""", (status, data, id_usuario, id_livro))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def remover(self, id_usuario, id_livro):
        conn = get_connection()
        cur = conn.execute("DELETE FROM lista_leitura WHERE id_usuario=? AND id_livro=?", (id_usuario, id_livro))
        conn.commit()
        conn.close()
        return cur.rowcount > 0

    def mapa(self, id_usuario):
        conn = get_connection()
        r = {x["id_livro"]: x["status"] for x in conn.execute(
            "SELECT id_livro, status FROM lista_leitura WHERE id_usuario=?", (id_usuario,))}
        conn.close()
        return r


class MetaLeituraDAO:
    def definir(self, id_usuario, ano, quantidade):
        conn = get_connection()
        conn.execute("""INSERT INTO metas_leitura (ano, quantidade_meta, id_usuario) VALUES (?,?,?)
                        ON CONFLICT(id_usuario, ano) DO UPDATE SET quantidade_meta=excluded.quantidade_meta""",
                     (ano, quantidade, id_usuario))
        conn.commit()
        conn.close()

    def buscar(self, id_usuario, ano):
        conn = get_connection()
        row = conn.execute("SELECT * FROM metas_leitura WHERE id_usuario=? AND ano=?", (id_usuario, ano)).fetchone()
        if not row:
            conn.close()
            return None
        lidos = conn.execute("""SELECT COUNT(*) FROM lista_leitura WHERE id_usuario=? AND status='lido'
                                AND strftime('%Y', data_leitura)=?""", (id_usuario, str(ano))).fetchone()[0]
        conn.close()
        return MetaLeitura(lidos=lidos, **dict(row))


class CuriosidadeDAO:
    def sortear(self, excluir=None):
        conn = get_connection()
        if excluir:
            row = conn.execute("SELECT * FROM curiosidades WHERE id_curiosidade != ? ORDER BY RANDOM() LIMIT 1",
                               (excluir,)).fetchone()
        else:
            row = conn.execute("SELECT * FROM curiosidades ORDER BY RANDOM() LIMIT 1").fetchone()
        conn.close()
        return Curiosidade(**dict(row)) if row else None
