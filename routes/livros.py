# Importa os recursos necessários do Flask.
# Blueprint permite organizar as rotas da aplicação.
# request permite acessar os dados enviados pelo usuário.
# jsonify transforma os dados em respostas no formato JSON.
from flask import Blueprint, request, jsonify

# Importa as classes DAO responsáveis pelas operações
# relacionadas aos livros, autores e gêneros.
from dao.livro_dao import LivroDAO, AutorDAO, GeneroDAO

# Importa a classe AvaliacaoDAO, responsável por salvar
# e consultar as avaliações dos livros.
from dao.avaliacao_dao import AvaliacaoDAO

# Importa a classe EstatisticaDAO, responsável por buscar
# informações estatísticas do sistema.
from dao.estatistica_dao import EstatisticaDAO

# Importa a classe CuriosidadeDAO, responsável por buscar
# curiosidades cadastradas no sistema.
from dao.estante_dao import CuriosidadeDAO

# Importa as classes dos modelos.
# Livro representa os dados de um livro.
# Autor representa os dados de um autor.
# Genero representa os dados de um gênero literário.
# Avaliacao representa os dados de uma avaliação.
from models.livro import Livro
from models.autor import Autor
from models.genero import Genero
from models.avaliacao import Avaliacao

# Importa os decoradores responsáveis por controlar o acesso às rotas.
# admin_obrigatorio exige que o usuário seja administrador.
# login_obrigatorio exige que o usuário esteja logado.
from routes.auth import admin_obrigatorio, login_obrigatorio

# Importa session para acessar os dados do usuário conectado.
from flask import session


# Cria um Blueprint chamado "livros".
# Todas as rotas deste arquivo terão o prefixo "/api".
bp = Blueprint("livros", __name__, url_prefix="/api")

# Cria as instâncias das classes DAO.
# dao: realiza operações com livros.
# autor_dao: realiza operações com autores.
# genero_dao: realiza operações com gêneros.
# av_dao: realiza operações com avaliações.
dao, autor_dao, genero_dao, av_dao = LivroDAO(), AutorDAO(), GeneroDAO(), AvaliacaoDAO()

# Cria as instâncias responsáveis pelas estatísticas
# e pelas curiosidades do sistema.
est_dao, cur_dao = EstatisticaDAO(), CuriosidadeDAO()


# Cria uma função auxiliar para transformar os dados recebidos em JSON
# em um objeto da classe Livro.
# O parâmetro id_livro é opcional e pode ser utilizado
# quando o objetivo é editar um livro já cadastrado.
def _livro_do_json(d, id_livro=None):

    # Documentação da função:
    # valida os dados recebidos em JSON e retorna um objeto Livro
    # junto com uma possível mensagem de erro.

    # Obtém o título enviado pelo usuário.
    # str() transforma o valor em texto.
    # strip() remove espaços em branco do início e do final.
    titulo = str(d.get("titulo", "")).strip()

    # Verifica se o título está vazio.
    if not titulo:

        # Se não houver título, retorna None para o livro
        # e uma mensagem informando que o título é obrigatório.
        return None, "Informe o título."

    # Inicia um bloco try para tentar converter e obter
    # os dados numéricos necessários para cadastrar ou editar o livro.
    try:

        # Obtém a quantidade total de exemplares.
        # Se o usuário não informar esse campo, o valor padrão será 1.
        # int() transforma o valor em número inteiro.
        total = int(d.get("quantidade_total", 1))

        # Obtém o ano de publicação.
        # Se o valor não existir ou estiver vazio, utiliza None.
        # Caso contrário, transforma o ano em número inteiro.
        ano = int(d["ano_publicacao"]) if d.get("ano_publicacao") not in (None, "") else None

        # Obtém os IDs do autor e do gênero.
        # Ambos são convertidos para números inteiros.
        id_autor, id_genero = int(d["id_autor"]), int(d["id_genero"])

    # Captura erros que podem acontecer durante a conversão
    # ou quando alguma informação obrigatória estiver ausente.
    except (ValueError, KeyError, TypeError):

        # Retorna uma mensagem informando que algum dado
        # relacionado ao autor, gênero, ano ou quantidade está inválido.
        return None, "Dados inválidos (autor, gênero, ano ou quantidade)."

    # Verifica se a quantidade total de exemplares é negativa.
    if total < 0:

        # Se for negativa, retorna uma mensagem de erro.
        return None, "Quantidade inválida."

    # Cria um objeto da classe Livro com os dados recebidos.
    # Cada informação é enviada para seu respectivo atributo.
    return Livro(id_livro=id_livro, titulo=titulo, isbn=(d.get("isbn") or "").strip() or None,
                 ano_publicacao=ano, editora=d.get("editora", ""), quantidade_total=total,
                 capa_url=d.get("capa_url", ""), classificacao_indicativa=d.get("classificacao_indicativa", ""),
                 sinopse=d.get("sinopse", ""), id_autor=id_autor, id_genero=id_genero), None


# Define uma rota GET para listar os livros cadastrados.
# Endereço: /api/livros
@bp.get("/livros")
def listar():

    # Chama o método listar() do LivroDAO para buscar os livros.
    # Os parâmetros recebidos pela URL permitem filtrar e organizar
    # os resultados apresentados.
    livros = dao.listar(busca=request.args.get("busca", "").strip(),
                        id_genero=request.args.get("genero", type=int),
                        somente_disponiveis=request.args.get("disponiveis") == "1",
                        ordem=request.args.get("ordem", "titulo"),
                        nota_min=request.args.get("nota_min", type=float),
                        limite=request.args.get("limite", type=int))

    # Percorre a lista de livros encontrados.
    # to_dict() transforma cada objeto Livro em um dicionário.
    # jsonify retorna todos os livros em formato JSON.
    return jsonify([l.to_dict() for l in livros])


# Define uma rota GET para consultar os detalhes de um livro específico.
# O endereço recebe o ID do livro como número inteiro.
# Exemplo: /api/livros/5
@bp.get("/livros/<int:id_livro>")
def detalhe(id_livro):

    # Busca no banco de dados o livro que possui o ID informado.
    l = dao.buscar_por_id(id_livro)

    # Verifica se o livro foi encontrado.
    if not l:

        # Se não existir, retorna uma mensagem de erro
        # com o código 404 (recurso não encontrado).
        return jsonify(erro="Livro não encontrado."), 404

    # Retorna os detalhes do livro, suas avaliações
    # e a média das notas recebidas.
    # to_dict() transforma os dados do livro em dicionário.
    # listar_por_livro() busca as avaliações relacionadas ao livro.
    # media() calcula ou consulta a média das avaliações.
    return jsonify(livro=l.to_dict(), avaliacoes=av_dao.listar_por_livro(id_livro), nota=av_dao.media(id_livro))


# Define uma rota POST para cadastrar um novo livro.
# Endereço: /api/livros
@bp.post("/livros")

# Permite que somente administradores cadastrem livros.
@admin_obrigatorio
def cadastrar():

    # Recebe os dados enviados em JSON.
    # Se não houver conteúdo ou ele não puder ser interpretado,
    # utiliza um dicionário vazio.
    # A função auxiliar valida os dados e cria o objeto Livro.
    # O resultado contém o objeto Livro e uma possível mensagem de erro.
    livro, erro = _livro_do_json(request.get_json(silent=True) or {})

    # Verifica se ocorreu algum erro durante a validação.
    if erro:

        # Se houver erro, retorna a mensagem com o código 400,
        # indicando que os dados enviados são inválidos.
        return jsonify(erro=erro), 400

    # Chama o método inserir() para cadastrar o livro no banco de dados.
    # O método retorna o ID do novo livro quando o cadastro funciona.
    novo = dao.inserir(livro)

    # Verifica se o cadastro não foi realizado.
    if novo is None:

        # Retorna um erro com o código 409 (conflito).
        # Isso pode acontecer se o ISBN já estiver cadastrado
        # ou se o autor ou gênero informado não existir.
        return jsonify(erro="Não foi possível cadastrar (ISBN repetido ou autor/gênero inexistente)."), 409

    # Se o cadastro funcionar, retorna o ID do livro criado,
    # uma mensagem de sucesso e o código 201 (recurso criado).
    return jsonify(id_livro=novo, mensagem="Livro cadastrado."), 201


# Define uma rota PUT para editar os dados de um livro existente.
# O endereço recebe o ID do livro que será atualizado.
# Exemplo: /api/livros/5
@bp.put("/livros/<int:id_livro>")

# Exige que o usuário seja administrador.
@admin_obrigatorio
def editar(id_livro):

    # Recebe os dados enviados em JSON.
    # A função auxiliar valida as informações e cria um objeto Livro.
    # O ID recebido pela URL é enviado para identificar o livro editado.
    livro, erro = _livro_do_json(request.get_json(silent=True) or {}, id_livro)

    # Verifica se houve algum erro na validação dos dados.
    if erro:

        # Se houver erro, retorna a mensagem com o código 400.
        return jsonify(erro=erro), 400

    # Chama atualizar() para salvar as alterações no banco de dados.
    # Se a atualização não for realizada, o método retorna False.
    if not dao.atualizar(livro):

        # Retorna uma mensagem de erro com o código 409.
        return jsonify(erro="Não foi possível editar o livro."), 409

    # Se a atualização funcionar, retorna uma mensagem de sucesso.
    return jsonify(mensagem="Livro atualizado.")


# Define uma rota DELETE para excluir um livro.
# O endereço recebe o ID do livro que será excluído.
# Exemplo: /api/livros/5
@bp.delete("/livros/<int:id_livro>")

# Somente administradores podem excluir livros.
@admin_obrigatorio
def excluir(id_livro):

    # Chama o método excluir() do LivroDAO.
    # Envia o ID do livro que deverá ser removido do banco de dados.
    if not dao.excluir(id_livro):

        # Se a exclusão não for possível, retorna um erro com código 409.
        # Isso pode acontecer quando o livro não existe
        # ou possui empréstimos relacionados.
        return jsonify(erro="Não foi possível excluir (livro inexistente ou com empréstimos)."), 409

    # Se a exclusão funcionar, retorna uma mensagem de confirmação.
    return jsonify(mensagem="Livro excluído.")


# Define uma rota GET para consultar os gêneros literários.
# Endereço: /api/generos
@bp.get("/generos")
def generos():

    # Chama listar_com_contagem() para buscar os gêneros cadastrados
    # e a quantidade de livros relacionada a cada um.
    # Retorna os resultados em formato JSON.
    return jsonify(genero_dao.listar_com_contagem())


# Define uma rota POST para cadastrar um novo gênero literário.
# Endereço: /api/generos
@bp.post("/generos")

# Exige que o usuário seja administrador.
@admin_obrigatorio
def novo_genero():

    # Obtém os dados enviados pelo usuário em formato JSON.
    # Se não houver dados válidos, utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Obtém o nome do gênero e remove espaços em branco
    # do início e do final do texto.
    nome = d.get("nome", "").strip()

    # Verifica se o nome do gênero foi informado.
    if not nome:

        # Se estiver vazio, retorna uma mensagem de erro com código 400.
        return jsonify(erro="Informe o nome do gênero."), 400

    # Cria um objeto Genero com o nome e a descrição recebidos.
    # Em seguida, chama inserir() para cadastrar o gênero no banco.
    # O método retorna o ID do novo gênero quando o cadastro funciona.
    novo = genero_dao.inserir(Genero(nome=nome, descricao=d.get("descricao", "")))

    # Verifica se o gênero não foi cadastrado.
    if novo is None:

        # Retorna um erro com código 409,
        # indicando que o gênero já existe.
        return jsonify(erro="Gênero já existe."), 409

    # Retorna o ID do gênero cadastrado e o código 201.
    return jsonify(id_genero=novo), 201


# Define uma rota GET para consultar os autores cadastrados.
# Endereço: /api/autores
@bp.get("/autores")
def autores():

    # Busca todos os autores por meio do método listar().
    # to_dict() transforma cada objeto Autor em um dicionário.
    # jsonify retorna a lista de autores em formato JSON.
    return jsonify([a.to_dict() for a in autor_dao.listar()])


# Define uma rota POST para cadastrar um novo autor.
# Endereço: /api/autores
@bp.post("/autores")

# Exige que o usuário seja administrador.
@admin_obrigatorio
def novo_autor():

    # Obtém os dados enviados pelo usuário em formato JSON.
    # Se não houver dados válidos, utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Obtém o nome do autor e remove os espaços em branco
    # do início e do final do texto.
    nome = d.get("nome", "").strip()

    # Verifica se o nome foi informado.
    if not nome:

        # Se estiver vazio, retorna uma mensagem de erro com código 400.
        return jsonify(erro="Informe o nome do autor."), 400

    # Cria um objeto Autor com os dados recebidos.
    # Se a nacionalidade ou a biografia não forem informadas,
    # utiliza textos vazios como valores padrão.
    # Depois, chama inserir() para cadastrar o autor.
    novo = autor_dao.inserir(Autor(nome=nome, nacionalidade=d.get("nacionalidade", ""), biografia=d.get("biografia", "")))

    # Retorna o ID do autor cadastrado e o código 201 (criado).
    return jsonify(id_autor=novo), 201


# Define uma rota POST para registrar uma avaliação de um livro.
# O endereço recebe o ID do livro que será avaliado.
# Exemplo: /api/livros/5/avaliacoes
@bp.post("/livros/<int:id_livro>/avaliacoes")

# Exige que o usuário esteja logado para avaliar um livro.
@login_obrigatorio
def avaliar(id_livro):

    # Obtém os dados da avaliação enviados em JSON.
    # Se não houver dados válidos, utiliza um dicionário vazio.
    d = request.get_json(silent=True) or {}

    # Inicia um bloco try para tentar converter a nota em número inteiro.
    try:

        # Obtém o valor do campo "nota" e transforma em inteiro.
        nota = int(d.get("nota"))

    # Captura erros caso a nota não seja informada
    # ou não possa ser convertida para número inteiro.
    except (TypeError, ValueError):

        # Retorna uma mensagem de erro com código 400.
        return jsonify(erro="Nota inválida."), 400

    # Verifica se a nota está dentro do intervalo permitido:
    # no mínimo 1 e no máximo 5.
    if not 1 <= nota <= 5:

        # Se estiver fora do intervalo, retorna um erro com código 400.
        return jsonify(erro="A nota deve ser de 1 a 5."), 400

    # Verifica se o livro informado realmente existe no banco de dados.
    if not dao.buscar_por_id(id_livro):

        # Se o livro não for encontrado, retorna o código 404.
        return jsonify(erro="Livro não encontrado."), 404

    # Cria um objeto Avaliacao com os dados recebidos.
    # nota: nota atribuída ao livro.
    # comentario: texto escrito pelo usuário, limitado a 500 caracteres.
    # id_usuario: ID do usuário que está conectado.
    # id_livro: ID do livro que está sendo avaliado.
    # Em seguida, chama salvar() para registrar a avaliação.
    av_dao.salvar(Avaliacao(nota=nota, comentario=d.get("comentario", "")[:500],
                            id_usuario=session["id_usuario"], id_livro=id_livro))

    # Retorna uma mensagem confirmando que a avaliação foi registrada.
    return jsonify(mensagem="Avaliação registrada.")


# Define uma rota GET para consultar as estatísticas gerais do sistema.
# Endereço: /api/estatisticas
@bp.get("/estatisticas")
def estatisticas():

    # Chama o método resumo() do EstatisticaDAO.
    # Ele retorna um conjunto de informações estatísticas do sistema.
    # jsonify transforma essas informações em uma resposta JSON.
    return jsonify(est_dao.resumo())


# Define uma rota GET para buscar todas as informações necessárias
# para carregar a página inicial do site.
# Endereço: /api/home
@bp.get("/home")
def home():

    # Documentação da função:
    # reúne em uma única requisição os dados utilizados pela página inicial.

    # Busca o livro do dia.
    dia = dao.livro_do_dia()

    # Sorteia uma curiosidade cadastrada no sistema.
    cur = cur_dao.sortear()

    # Retorna todos os dados da página inicial em formato JSON.
    return jsonify(

        # Retorna os dados do livro do dia.
        # Se nenhum livro for encontrado, retorna None.
        livro_do_dia=dia.to_dict() if dia else None,

        # Retorna até 8 livros em destaque, organizados pela avaliação.
        destaques=[l.to_dict() for l in dao.listar(ordem="avaliacao", limite=8)],

        # Retorna até 8 livros populares.
        populares=[l.to_dict() for l in dao.listar(ordem="popular", limite=8)],

        # Retorna até 8 lançamentos, organizados pelos mais recentes.
        lancamentos=[l.to_dict() for l in dao.listar(ordem="recentes", limite=8)],

        # Retorna os gêneros literários cadastrados
        # junto com a contagem de livros de cada gênero.
        generos=genero_dao.listar_com_contagem(),

        # Retorna a curiosidade sorteada.
        # Se nenhuma curiosidade for encontrada, retorna None.
        curiosidade=cur.to_dict() if cur else None,

        # Retorna o resumo das estatísticas gerais do sistema.
        estatisticas=est_dao.resumo()
    )


# Define uma rota GET para consultar uma curiosidade aleatória.
# Endereço: /api/curiosidade
@bp.get("/curiosidade")
def curiosidade():

    # Sorteia uma curiosidade.
    # O parâmetro "excluir" é opcional e recebe um número inteiro.
    # Ele permite informar um ID que deve ser excluído do sorteio.
    cur = cur_dao.sortear(request.args.get("excluir", type=int))

    # Se uma curiosidade for encontrada, transforma seus dados em dicionário.
    # Caso contrário, retorna None.
    # jsonify envia o resultado em formato JSON.
    return jsonify(cur.to_dict() if cur else None)


# Define uma rota GET para buscar recomendações de livros.
# Endereço: /api/recomendacoes
@bp.get("/recomendacoes")

# Exige que o usuário esteja logado para acessar suas recomendações.
@login_obrigatorio
def recomendacoes():

    # Chama o método recomendar() do LivroDAO.
    # Envia o ID do usuário conectado para buscar recomendações relacionadas a ele.
    # to_dict() transforma cada livro recomendado em um dicionário.
    # jsonify retorna a lista de recomendações em formato JSON.
    return jsonify([l.to_dict() for l in dao.recomendar(session["id_usuario"])])