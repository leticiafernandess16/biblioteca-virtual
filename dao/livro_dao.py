# Importa o módulo sqlite3 para trabalhar com o banco de dados e tratar erros de integridade.
import sqlite3

# Importa date para trabalhar com datas e identificar o dia atual.
from datetime import date

# Importa a função responsável por criar a conexão com o banco de dados.
from database.conexao import get_connection

# Importa as classes que representam os dados dos livros, autores e gêneros.
from models.livro import Livro
from models.autor import Autor
from models.genero import Genero


# Consulta SQL base utilizada para buscar os livros junto com os nomes dos autores e gêneros,
# a média das avaliações, a quantidade de avaliações e o total de empréstimos.
SELECT_LIVRO = """
SELECT l.*, a.nome AS autor, g.nome AS genero,
  (SELECT ROUND(AVG(v.nota),1) FROM avaliacoes v WHERE v.id_livro = l.id_livro) AS nota_media,
  (SELECT COUNT(*) FROM avaliacoes v WHERE v.id_livro = l.id_livro) AS total_avaliacoes,
  (SELECT COUNT(*) FROM emprestimos e WHERE e.id_livro = l.id_livro) AS total_emprestimos
FROM livros l
JOIN autores a ON a.id_autor = l.id_autor
JOIN generos g ON g.id_genero = l.id_genero
"""


# Dicionário que define as opções de ordenação dos livros.
# Essa lista permite utilizar apenas opções previamente definidas,
# evitando que textos enviados pelo usuário sejam inseridos diretamente no ORDER BY.
ORDENS = {
    # Organiza os livros pelo título em ordem alfabética, ignorando diferenças entre maiúsculas e minúsculas.
    "titulo": "l.titulo COLLATE NOCASE",

    # Organiza os livros do mais emprestado para o menos emprestado.
    "popular": "total_emprestimos DESC, l.titulo",

    # Organiza os livros pela maior média de avaliações,
    # considerando também a quantidade de avaliações.
    "avaliacao": "COALESCE(nota_media,0) DESC, total_avaliacoes DESC, l.titulo",

    # Organiza os livros pelo ano de publicação, dos mais recentes para os mais antigos.
    "recentes": "l.ano_publicacao DESC, l.titulo",
}


# Classe responsável pelas operações de acesso ao banco de dados relacionadas aos livros.
class LivroDAO:

    # Método estático que transforma os resultados de uma consulta em um objeto Livro.
    @staticmethod
    def _montar(row):

        # Se existir um resultado, transforma seus dados em um objeto da classe Livro.
        # Caso contrário, retorna None.
        return Livro(**dict(row)) if row else None

    # Método responsável por listar os livros de acordo com os filtros informados.
    def listar(self, busca="", id_genero=None, somente_disponiveis=False,
               ordem="titulo", nota_min=None, limite=None):

        # Inicia a consulta utilizando a consulta SQL base e uma condição verdadeira.
        # Isso facilita a adição de outros filtros posteriormente.
        sql = SELECT_LIVRO + " WHERE 1=1"

        # Cria uma lista vazia para armazenar os valores utilizados na consulta SQL.
        params = []

        # Verifica se foi informado algum texto para pesquisar.
        if busca:

            # Filtra os livros pelo título, nome do autor ou nome do gênero.
            # O LIKE permite encontrar resultados que contenham o texto informado.
            sql += " AND (l.titulo LIKE ? OR a.nome LIKE ? OR g.nome LIKE ?)"

            # Adiciona o texto de busca aos três campos da consulta.
            params += [f"%{busca}%"] * 3

        # Verifica se foi informado um gênero específico.
        if id_genero:

            # Filtra os livros pelo ID do gênero informado.
            sql += " AND l.id_genero = ?"

            # Adiciona o ID do gênero aos parâmetros da consulta.
            params.append(id_genero)

        # Verifica se a busca deve mostrar somente livros disponíveis.
        if somente_disponiveis:

            # Exibe apenas os livros que possuem pelo menos um exemplar disponível.
            sql += " AND l.quantidade_disponivel > 0"

        # Verifica se foi informada uma nota mínima para os livros.
        if nota_min:

            # Filtra os livros que possuem média de avaliações igual ou superior à nota informada.
            # COALESCE considera como zero a média dos livros que ainda não possuem avaliações.
            sql += " AND COALESCE((SELECT AVG(v.nota) FROM avaliacoes v WHERE v.id_livro = l.id_livro),0) >= ?"

            # Adiciona a nota mínima aos parâmetros da consulta.
            params.append(nota_min)

        # Define a ordenação dos resultados utilizando as opções permitidas no dicionário ORDENS.
        # Caso a opção informada não exista, utiliza a ordenação pelo título.
        sql += " ORDER BY " + ORDENS.get(ordem, ORDENS["titulo"])

        # Verifica se foi definido um limite de resultados.
        if limite:

            # Limita a quantidade de livros retornados pela consulta.
            sql += " LIMIT ?"

            # Adiciona o limite aos parâmetros da consulta, convertendo o valor para inteiro.
            params.append(int(limite))

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Executa a consulta SQL com os parâmetros informados e busca todos os resultados.
        rows = conn.execute(sql, params).fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma cada resultado em um objeto Livro e retorna a lista de livros.
        return [self._montar(r) for r in rows]

    # Método responsável por buscar um livro específico utilizando seu ID.
    def buscar_por_id(self, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os dados do livro correspondente ao ID informado,
        # utilizando a consulta que também retorna autor, gênero e estatísticas.
        row = conn.execute(SELECT_LIVRO + " WHERE l.id_livro = ?", (id_livro,)).fetchone()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma o resultado em um objeto Livro e retorna os dados.
        # Se o livro não for encontrado, retorna None.
        return self._montar(row)

    # Método responsável por selecionar um livro diferente a cada dia.
    def livro_do_dia(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca todos os IDs dos livros cadastrados, organizados em ordem crescente.
        ids = [r[0] for r in conn.execute("SELECT id_livro FROM livros ORDER BY id_livro")]

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Verifica se existem livros cadastrados.
        if not ids:
            return None

        # Utiliza o número do dia atual para selecionar um livro da lista.
        # Dessa forma, o livro é escolhido de maneira diferente conforme o dia.
        return self.buscar_por_id(ids[date.today().toordinal() % len(ids)])

    # Método responsável por recomendar livros com base nas atividades do usuário.
    def recomendar(self, id_usuario, limite=6):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os gêneros relacionados aos livros que o usuário mais favoritou,
        # emprestou ou adicionou à sua lista de leitura.
        # UNION ALL reúne os resultados das três consultas.
        # GROUP BY agrupa os gêneros e COUNT contabiliza suas ocorrências.
        # LIMIT 3 seleciona os três gêneros mais frequentes.
        generos = [r[0] for r in conn.execute("""
            SELECT id_genero FROM (
              SELECT l.id_genero FROM favoritos f JOIN livros l ON l.id_livro=f.id_livro WHERE f.id_usuario=?
              UNION ALL SELECT l.id_genero FROM emprestimos e JOIN livros l ON l.id_livro=e.id_livro WHERE e.id_usuario=?
              UNION ALL SELECT l.id_genero FROM lista_leitura s JOIN livros l ON l.id_livro=s.id_livro WHERE s.id_usuario=?)
            GROUP BY id_genero ORDER BY COUNT(*) DESC LIMIT 3""", (id_usuario,) * 3)]

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Verifica se o usuário ainda não possui atividades suficientes para identificar seus gêneros preferidos.
        if not generos:

            # Caso não existam gêneros identificados, recomenda os livros com melhores avaliações.
            return self.listar(ordem="avaliacao", limite=limite)

        # Busca os IDs dos livros que o usuário já visualizou por meio de favoritos,
        # empréstimos ou lista de leitura.
        vistos = self._ids_vistos(id_usuario)

        # Cria uma lista vazia para armazenar os livros recomendados.
        candidatos = []

        # Percorre os três gêneros mais relacionados às atividades do usuário.
        for g in generos:

            # Busca os livros de cada gênero, organizados pelas melhores avaliações,
            # e adiciona os resultados à lista de candidatos.
            candidatos += self.listar(id_genero=g, ordem="avaliacao")

        # Retorna somente os livros que ainda não foram vistos pelo usuário,
        # respeitando a quantidade máxima de recomendações definida pelo limite.
        return [l for l in candidatos if l.id_livro not in vistos][:limite]

    # Método estático responsável por buscar os IDs dos livros já relacionados ao usuário.
    @staticmethod
    def _ids_vistos(id_usuario):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os IDs dos livros presentes nos favoritos, empréstimos e lista de leitura.
        # UNION elimina IDs repetidos entre as três consultas.
        # O resultado é armazenado em um conjunto (set).
        ids = {r[0] for r in conn.execute("""
            SELECT id_livro FROM favoritos WHERE id_usuario=?
            UNION SELECT id_livro FROM emprestimos WHERE id_usuario=?
            UNION SELECT id_livro FROM lista_leitura WHERE id_usuario=?""", (id_usuario,) * 3)}

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna o conjunto com os IDs dos livros já relacionados ao usuário.
        return ids

    # Método responsável por cadastrar um novo livro no banco de dados.
    def inserir(self, livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Insere os dados do livro na tabela livros.
            # A quantidade disponível começa igual à quantidade total de exemplares cadastrados.
            cur = conn.execute(
                """INSERT INTO livros (titulo, isbn, ano_publicacao, editora, quantidade_total,
                   quantidade_disponivel, capa_url, classificacao_indicativa, sinopse, id_autor, id_genero)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",

                # Envia os valores dos atributos do objeto Livro para preencher os campos da consulta.
                # Caso o ISBN não seja informado, utiliza None.
                (livro.titulo, livro.isbn or None, livro.ano_publicacao, livro.editora,
                 livro.quantidade_total, livro.quantidade_total, livro.capa_url,
                 livro.classificacao_indicativa, livro.sinopse, livro.id_autor, livro.id_genero))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna o ID gerado automaticamente para o novo livro cadastrado.
            return cur.lastrowid

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna None caso não seja possível cadastrar o livro.
            return None

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por atualizar os dados de um livro já cadastrado.
    def atualizar(self, livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Busca a quantidade total e disponível do livro atualmente cadastrado.
            atual = conn.execute("SELECT quantidade_total, quantidade_disponivel FROM livros WHERE id_livro=?",
                                 (livro.id_livro,)).fetchone()

            # Verifica se o livro existe no banco de dados.
            if not atual:
                return False

            # Calcula quantos exemplares do livro estão atualmente emprestados.
            # O cálculo utiliza a diferença entre a quantidade total e a disponível.
            emprestados = atual["quantidade_total"] - atual["quantidade_disponivel"]

            # Calcula a nova quantidade disponível considerando o novo total informado
            # e mantendo a quantidade de exemplares que continuam emprestados.
            nova_disp = livro.quantidade_total - emprestados

            # Verifica se a nova quantidade total é suficiente para manter os empréstimos existentes.
            if nova_disp < 0:
                return False

            # Atualiza as informações do livro no banco de dados.
            conn.execute(
                """UPDATE livros SET titulo=?, isbn=?, ano_publicacao=?, editora=?, quantidade_total=?,
                   quantidade_disponivel=?, capa_url=?, classificacao_indicativa=?, sinopse=?,
                   id_autor=?, id_genero=? WHERE id_livro=?""",

                # Envia os novos valores dos atributos do livro para preencher os campos da atualização.
                # O ID do livro é utilizado para identificar qual registro será alterado.
                (livro.titulo, livro.isbn or None, livro.ano_publicacao, livro.editora,
                 livro.quantidade_total, nova_disp, livro.capa_url, livro.classificacao_indicativa,
                 livro.sinopse, livro.id_autor, livro.id_genero, livro.id_livro))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True indicando que o livro foi atualizado com sucesso.
            return True

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna False indicando que não foi possível atualizar o livro.
            return False

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por excluir um livro do banco de dados.
    def excluir(self, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar a operação e tratar possíveis erros.
        try:

            # Exclui o livro que possui o ID informado.
            cur = conn.execute("DELETE FROM livros WHERE id_livro = ?", (id_livro,))

            # Salva a alteração realizada no banco de dados.
            conn.commit()

            # Retorna True se algum registro foi excluído ou False se nenhum foi encontrado.
            return cur.rowcount > 0

        # Trata erros de integridade, como quando existem empréstimos vinculados ao livro.
        except sqlite3.IntegrityError:

            # Retorna False indicando que o livro não pôde ser excluído.
            return False

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()


# Classe responsável pelas operações de acesso ao banco de dados relacionadas aos autores.
class AutorDAO:

    # Método responsável por listar todos os autores cadastrados.
    def listar(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca todos os autores, organizando os resultados em ordem alfabética pelo nome.
        rows = conn.execute("SELECT * FROM autores ORDER BY nome").fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados em objetos da classe Autor e retorna uma lista.
        return [Autor(**dict(r)) for r in rows]

    # Método responsável por cadastrar um novo autor.
    def inserir(self, autor):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Insere o nome, a nacionalidade e a biografia do autor na tabela autores.
        cur = conn.execute("INSERT INTO autores (nome, nacionalidade, biografia) VALUES (?,?,?)",
                           (autor.nome, autor.nacionalidade, autor.biografia))

        # Salva as alterações realizadas no banco de dados.
        conn.commit()

        # Armazena o ID gerado automaticamente para o novo autor.
        novo = cur.lastrowid

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna o ID do autor cadastrado.
        return novo


# Classe responsável pelas operações de acesso ao banco de dados relacionadas aos gêneros literários.
class GeneroDAO:

    # Método responsável por listar todos os gêneros cadastrados.
    def listar(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca todos os gêneros, organizando os resultados em ordem alfabética pelo nome.
        rows = conn.execute("SELECT * FROM generos ORDER BY nome").fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados em objetos da classe Genero e retorna uma lista.
        return [Genero(**dict(r)) for r in rows]

    # Método responsável por listar os gêneros e a quantidade de livros relacionados a cada um.
    def listar_com_contagem(self):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os dados dos gêneros e conta quantos livros estão relacionados a cada gênero.
        # O LEFT JOIN permite mostrar também os gêneros que ainda não possuem livros cadastrados.
        rows = conn.execute("""SELECT g.*, COUNT(l.id_livro) AS total_livros FROM generos g
                               LEFT JOIN livros l ON l.id_genero = g.id_genero
                               GROUP BY g.id_genero ORDER BY g.nome""").fetchall()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Transforma os resultados em uma lista de dicionários e retorna os dados.
        return [dict(r) for r in rows]

    # Método responsável por cadastrar um novo gênero literário.
    def inserir(self, genero):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar a operação e tratar possíveis erros.
        try:

            # Insere o nome e a descrição do gênero na tabela generos.
            cur = conn.execute("INSERT INTO generos (nome, descricao) VALUES (?,?)",
                               (genero.nome, genero.descricao))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna o ID gerado automaticamente para o novo gênero cadastrado.
            return cur.lastrowid

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna None caso não seja possível cadastrar o gênero.
            return None

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()