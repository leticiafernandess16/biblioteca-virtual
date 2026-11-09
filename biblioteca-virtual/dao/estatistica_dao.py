from database.conexao import get_connection


class EstatisticaDAO:
    """Consultas agregadas para a página inicial e o painel administrativo."""

    def resumo(self):
        conn = get_connection()
        conn.execute("UPDATE emprestimos SET status='atrasado' WHERE status='ativo' AND data_prevista_devolucao < date('now')")
        conn.commit()
        r = conn.execute("""SELECT
            (SELECT COUNT(*) FROM livros) AS livros,
            (SELECT COALESCE(SUM(quantidade_total),0) FROM livros) AS exemplares,
            (SELECT COUNT(*) FROM usuarios) AS usuarios,
            (SELECT COUNT(*) FROM emprestimos) AS emprestimos_total,
            (SELECT COUNT(*) FROM emprestimos WHERE status IN ('ativo','atrasado')) AS emprestimos_ativos,
            (SELECT COUNT(*) FROM emprestimos WHERE status='atrasado') AS emprestimos_atrasados,
            (SELECT COUNT(*) FROM avaliacoes) AS avaliacoes,
            (SELECT COUNT(*) FROM generos) AS generos""").fetchone()
        conn.close()
        return dict(r)

    def painel(self):
        dados = self.resumo()
        conn = get_connection()
        dados["mais_emprestados"] = [dict(r) for r in conn.execute("""
            SELECT l.titulo, COUNT(e.id_emprestimo) AS total FROM livros l
            LEFT JOIN emprestimos e ON e.id_livro = l.id_livro
            GROUP BY l.id_livro ORDER BY total DESC, l.titulo LIMIT 5""")]
        dados["generos_populares"] = [dict(r) for r in conn.execute("""
            SELECT g.nome AS titulo, COUNT(e.id_emprestimo) AS total FROM generos g
            LEFT JOIN livros l ON l.id_genero = g.id_genero
            LEFT JOIN emprestimos e ON e.id_livro = l.id_livro
            GROUP BY g.id_genero ORDER BY total DESC, g.nome LIMIT 5""")]
        conn.close()
        return dados
