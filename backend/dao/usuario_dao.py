import sqlite3  # Importa o módulo sqlite3, utilizado para trabalhar com bancos de dados SQLite.
from database.conexao import get_connection  # Importa a função responsável por estabelecer a conexão com o banco de dados.
from models.usuario import Usuario  # Importa a classe Usuario, que representa os dados de um usuário.


class UsuarioDAO:  # Define a classe UsuarioDAO, responsável por realizar operações no banco de dados relacionadas aos usuários.

    @staticmethod  # Indica que o método pode ser utilizado sem precisar criar uma instância da classe.
    def _montar(row):  # Define um método responsável por transformar os dados retornados pelo banco em um objeto Usuario.
        return Usuario(**dict(row)) if row else None  # Converte a linha retornada em um dicionário e utiliza seus dados para criar um objeto Usuario. Se não houver resultado, retorna None.

    def inserir(self, usuario):  # Define o método responsável por cadastrar um novo usuário no banco de dados.
        conn = get_connection()  # Estabelece uma conexão com o banco de dados.
        try:  # Inicia um bloco de tratamento de possíveis erros durante a inserção.
            cur = conn.execute(  # Executa o comando SQL para inserir os dados do usuário na tabela usuarios.
                "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?,?,?,?)",  # Define os campos que receberão os dados e utiliza parâmetros para evitar a inserção direta de valores no SQL.
                (usuario.nome, usuario.email, usuario.senha_hash, usuario.tipo))  # Envia os valores correspondentes aos campos nome, email, senha_hash e tipo.
            conn.commit()  # Confirma e salva as alterações realizadas no banco de dados.
            return cur.lastrowid  # Retorna o ID do último registro inserido.
        except sqlite3.IntegrityError:  # Captura erros de integridade, como a tentativa de cadastrar um e-mail que já existe.
            return None  # Retorna None para indicar que a inserção não foi realizada devido ao e-mail já cadastrado.
        finally:  # Executa este bloco independentemente de ocorrer um erro ou não.
            conn.close()  # Fecha a conexão com o banco de dados para liberar os recursos utilizados.

    def buscar_por_email(self, email):  # Define o método responsável por localizar um usuário utilizando seu endereço de e-mail.
        conn = get_connection()  # Estabelece uma conexão com o banco de dados.
        row = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()  # Executa uma consulta SQL que busca o usuário pelo e-mail informado e retorna apenas o primeiro resultado encontrado.
        conn.close()  # Fecha a conexão com o banco de dados.
        return self._montar(row)  # Converte o resultado encontrado em um objeto Usuario ou retorna None caso nenhum usuário seja encontrado.

    def buscar_por_id(self, id_usuario):  # Define o método responsável por localizar um usuário pelo seu identificador.
        conn = get_connection()  # Estabelece uma conexão com o banco de dados.
        row = conn.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,)).fetchone()  # Executa uma consulta SQL para buscar o usuário que possui o ID informado e retorna o primeiro resultado.
        conn.close()  # Fecha a conexão com o banco de dados.
        return self._montar(row)  # Transforma o resultado em um objeto Usuario ou retorna None se não encontrar nenhum registro.

    def listar(self):  # Define o método responsável por consultar e listar todos os usuários cadastrados.
        conn = get_connection()  # Estabelece uma conexão com o banco de dados.
        rows = conn.execute("SELECT * FROM usuarios ORDER BY nome").fetchall()  # Executa uma consulta SQL que retorna todos os usuários, organizando os resultados em ordem alfabética pelo nome.
        conn.close()  # Fecha a conexão com o banco de dados.
        return [self._montar(r) for r in rows]  # Percorre todos os registros encontrados, transforma cada um em um objeto Usuario e retorna uma lista com os usuários.

    def atualizar(self, id_usuario, nome, senha_hash=None):  # Define o método responsável por atualizar o nome e, opcionalmente, a senha de um usuário identificado pelo seu ID.
        conn = get_connection()  # Estabelece uma conexão com o banco de dados.
        if senha_hash:  # Verifica se uma nova senha foi informada.
            conn.execute("UPDATE usuarios SET nome=?, senha_hash=? WHERE id_usuario=?", (nome, senha_hash, id_usuario))  # Executa um comando SQL que atualiza o nome e a senha do usuário correspondente ao ID informado.
        else:  # Executa este bloco caso nenhuma nova senha tenha sido informada.
            conn.execute("UPDATE usuarios SET nome=? WHERE id_usuario=?", (nome, id_usuario))  # Atualiza somente o nome do usuário, mantendo a senha atual.
        conn.commit()  # Confirma e salva as alterações realizadas no banco de dados.
        conn.close()  # Fecha a conexão com o banco de dados após finalizar a atualização.