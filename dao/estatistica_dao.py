# Importa a função responsável por criar a conexão com o banco de dados.
from database.conexao import get_connection


# Classe responsável por realizar consultas de estatísticas do sistema,
# utilizadas na página inicial e no painel administrativo.
class EstatisticaDAO:

    # Método responsável por buscar um resumo geral das informações do sistema.
    def resumo(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Atualiza o status dos empréstimos para "atrasado"
        # quando a data prevista de devolução já passou e o empréstimo ainda está ativo.
        conn.execute("UPDATE emprestimos SET status='atrasado' WHERE status='ativo' AND data_prevista_devolucao < date('now')")

        # Salva a atualização dos status no banco de dados.
        conn.commit()

        # Executa uma consulta SQL para buscar diferentes informações e quantidades do sistema.
        r = conn.execute("""SELECT

            -- Conta a quantidade de livros cadastrados no sistema.
            (SELECT COUNT(*) FROM livros) AS livros,

            -- Soma a quantidade total de exemplares de todos os livros.
            -- COALESCE retorna 0 caso não existam valores para somar.
            (SELECT COALESCE(SUM(quantidade_total),0) FROM livros) AS exemplares,

            -- Conta a quantidade de usuários cadastrados.
            (SELECT COUNT(*) FROM usuarios) AS usuarios,

            -- Conta todos os empréstimos registrados no sistema.
            (SELECT COUNT(*) FROM emprestimos) AS emprestimos_total,

            -- Conta os empréstimos que estão ativos ou atrasados.
            (SELECT COUNT(*) FROM emprestimos WHERE status IN ('ativo','atrasado')) AS emprestimos_ativos,

            -- Conta a quantidade de empréstimos que estão atrasados.
            (SELECT COUNT(*) FROM emprestimos WHERE status='atrasado') AS emprestimos_atrasados,

            -- Conta a quantidade de avaliações cadastradas.
            (SELECT COUNT(*) FROM avaliacoes) AS avaliacoes,

            -- Conta a quantidade de gêneros literários cadastrados.
            (SELECT COUNT(*) FROM generos) AS generos""").fetchone()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados da consulta em um dicionário e retorna as estatísticas.
        return dict(r)

    # Método responsável por montar os dados exibidos no painel administrativo.
    def painel(self):

        # Chama o método resumo() para obter as estatísticas gerais do sistema.
        dados = self.resumo()

        # Abre uma nova conexão com o banco de dados.
        conn = get_connection()

        # Busca os cinco livros que possuem a maior quantidade de empréstimos.
        # O LEFT JOIN permite incluir livros que ainda não foram emprestados.
        # Os resultados são organizados do mais emprestado para o menos emprestado.
        dados["mais_emprestados"] = [dict(r) for r in conn.execute("""
            SELECT l.titulo, COUNT(e.id_emprestimo) AS total FROM livros l
            LEFT JOIN emprestimos e ON e.id_livro = l.id_livro
            GROUP BY l.id_livro ORDER BY total DESC, l.titulo LIMIT 5""")]

        # Busca os cinco gêneros literários com maior quantidade de empréstimos.
        # Relaciona os gêneros aos livros e os livros aos empréstimos.
        # O LEFT JOIN permite incluir gêneros que ainda não possuem empréstimos.
        dados["generos_populares"] = [dict(r) for r in conn.execute("""
            SELECT g.nome AS titulo, COUNT(e.id_emprestimo) AS total FROM generos g
            LEFT JOIN livros l ON l.id_genero = g.id_genero
            LEFT JOIN emprestimos e ON e.id_livro = l.id_livro
            GROUP BY g.id_genero ORDER BY total DESC, g.nome LIMIT 5""")]

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna o dicionário com as estatísticas gerais,
        # os livros mais emprestados e os gêneros mais populares.
        return dados
