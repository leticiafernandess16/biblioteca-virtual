# Importa o módulo sqlite3 para trabalhar com o banco de dados e tratar erros de integridade.
import sqlite3

# Importa date para trabalhar com datas.
from datetime import date

# Importa a função responsável por criar a conexão com o banco de dados.
from database.conexao import get_connection

# Importa as classes que representam os dados utilizados pelos métodos deste arquivo.
from models.favorito import Favorito
from models.lista_leitura import ListaLeitura
from models.meta_leitura import MetaLeitura
from models.curiosidade import Curiosidade


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas aos favoritos.
class FavoritoDAO:

    # Método responsável por adicionar ou remover um livro dos favoritos do usuário.
    def alternar(self, id_usuario, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Verifica se o livro já está na lista de favoritos do usuário.
            existe = conn.execute("SELECT id_favorito FROM favoritos WHERE id_usuario=? AND id_livro=?",
                                  (id_usuario, id_livro)).fetchone()

            # Verifica se o livro já está favoritado.
            if existe:

                # Remove o livro da lista de favoritos utilizando seu identificador.
                conn.execute("DELETE FROM favoritos WHERE id_favorito=?", (existe["id_favorito"],))

                # Indica que o livro não está mais favoritado.
                favoritado = False

            # Caso o livro ainda não esteja nos favoritos.
            else:

                # Adiciona o livro à lista de favoritos do usuário.
                conn.execute("INSERT INTO favoritos (id_usuario, id_livro) VALUES (?,?)", (id_usuario, id_livro))

                # Indica que o livro foi adicionado aos favoritos.
                favoritado = True

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True se o livro ficou favoritado ou False se foi removido.
            return favoritado

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna None caso ocorra um erro, como a tentativa de favoritar um livro inexistente.
            return None

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por buscar os IDs dos livros favoritados por um usuário.
    def ids(self, id_usuario):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os IDs dos livros que estão na lista de favoritos do usuário.
        r = [x[0] for x in conn.execute("SELECT id_livro FROM favoritos WHERE id_usuario=?", (id_usuario,))]

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna uma lista contendo os IDs dos livros favoritados.
        return r


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas à lista de leitura.
class ListaLeituraDAO:

    # Método responsável por definir ou atualizar o status de leitura de um livro.
    def definir_status(self, id_usuario, id_livro, status):

        # Verifica se o status informado é válido.
        # Os únicos valores aceitos são "quero_ler" e "lido".
        if status not in ("quero_ler", "lido"):
            return False

        # Se o status for "lido", registra a data atual.
        # Caso contrário, não registra uma data de leitura.
        data = date.today().isoformat() if status == "lido" else None

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Inicia um bloco para executar as operações e tratar possíveis erros.
        try:

            # Insere o livro na lista de leitura ou atualiza seu status caso já esteja cadastrado.
            # Quando o status é alterado para "lido", também atualiza a data de leitura.
            conn.execute("""INSERT INTO lista_leitura (status, data_leitura, id_usuario, id_livro) VALUES (?,?,?,?)
                            ON CONFLICT(id_usuario, id_livro) DO UPDATE SET status=excluded.status,
                            data_leitura=excluded.data_leitura""", (status, data, id_usuario, id_livro))

            # Salva as alterações realizadas no banco de dados.
            conn.commit()

            # Retorna True indicando que o status foi definido com sucesso.
            return True

        # Trata erros relacionados às restrições de integridade do banco de dados.
        except sqlite3.IntegrityError:

            # Retorna False indicando que não foi possível definir o status.
            return False

        # Executa este bloco independentemente de ocorrer um erro ou não.
        finally:

            # Fecha a conexão com o banco de dados.
            conn.close()

    # Método responsável por remover um livro da lista de leitura de um usuário.
    def remover(self, id_usuario, id_livro):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Remove da lista de leitura o livro relacionado ao usuário informado.
        cur = conn.execute("DELETE FROM lista_leitura WHERE id_usuario=? AND id_livro=?", (id_usuario, id_livro))

        # Salva a alteração realizada no banco de dados.
        conn.commit()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna True se algum registro foi removido ou False se nenhum registro foi encontrado.
        return cur.rowcount > 0

    # Método responsável por buscar os livros da lista de leitura e seus respectivos status.
    def mapa(self, id_usuario):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca os IDs dos livros e seus status, organizando os dados em um dicionário.
        # Cada ID de livro será associado ao seu respectivo status de leitura.
        r = {x["id_livro"]: x["status"] for x in conn.execute(
            "SELECT id_livro, status FROM lista_leitura WHERE id_usuario=?", (id_usuario,))}

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Retorna o dicionário com os livros e seus status de leitura.
        return r


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas às metas de leitura.
class MetaLeituraDAO:

    # Método responsável por cadastrar ou atualizar a meta de leitura de um usuário.
    def definir(self, id_usuario, ano, quantidade):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Insere uma nova meta de leitura ou atualiza a quantidade da meta
        # caso o usuário já possua uma meta cadastrada para o mesmo ano.
        conn.execute("""INSERT INTO metas_leitura (ano, quantidade_meta, id_usuario) VALUES (?,?,?)
                        ON CONFLICT(id_usuario, ano) DO UPDATE SET quantidade_meta=excluded.quantidade_meta""",
                     (ano, quantidade, id_usuario))

        # Salva as alterações realizadas no banco de dados.
        conn.commit()

        # Fecha a conexão com o banco de dados.
        conn.close()

    # Método responsável por buscar a meta de leitura de um usuário em determinado ano.
    def buscar(self, id_usuario, ano):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Busca a meta cadastrada para o usuário e o ano informados.
        row = conn.execute("SELECT * FROM metas_leitura WHERE id_usuario=? AND ano=?", (id_usuario, ano)).fetchone()

        # Verifica se existe uma meta cadastrada.
        if not row:

            # Fecha a conexão com o banco de dados.
            conn.close()

            # Retorna None caso nenhuma meta seja encontrada.
            return None

        # Conta quantos livros o usuário marcou como lidos no ano informado.
        # A consulta considera apenas os livros com status "lido"
        # cuja data de leitura pertence ao ano da meta.
        lidos = conn.execute("""SELECT COUNT(*) FROM lista_leitura WHERE id_usuario=? AND status='lido'
                                AND strftime('%Y', data_leitura)=?""", (id_usuario, str(ano))).fetchone()[0]

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Cria e retorna um objeto MetaLeitura com os dados encontrados
        # e a quantidade de livros lidos no ano.
        return MetaLeitura(lidos=lidos, **dict(row))


# Classe responsável por realizar as operações de acesso ao banco de dados relacionadas às curiosidades.
class CuriosidadeDAO:

    # Método responsável por sortear uma curiosidade aleatória do banco de dados.
    def sortear(self, excluir=None):

        # Abre uma conexão com o banco de dados.
        conn = get_connection()

        # Verifica se foi informado o ID de uma curiosidade que não deve ser sorteada novamente.
        if excluir:

            # Busca uma curiosidade aleatória, excluindo aquela que possui o ID informado.
            row = conn.execute("SELECT * FROM curiosidades WHERE id_curiosidade != ? ORDER BY RANDOM() LIMIT 1",
                               (excluir,)).fetchone()

        # Caso nenhum ID tenha sido informado para exclusão.
        else:

            # Busca uma curiosidade aleatória entre todas as cadastradas no banco de dados.
            row = conn.execute("SELECT * FROM curiosidades ORDER BY RANDOM() LIMIT 1").fetchone()

        # Fecha a conexão com o banco de dados.
        conn.close()

        # Se uma curiosidade for encontrada, transforma os dados em um objeto Curiosidade.
        # Caso contrário, retorna None.
        return Curiosidade(**dict(row)) if row else None