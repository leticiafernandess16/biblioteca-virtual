# 🌸 Biblioteca Lírio — Biblioteca Virtual

Projeto integrado DWS + POO + BD: Python/Flask, SQLite, HTML, CSS e JavaScript (Fetch API).

## Funcionalidades
- **Início:** banner com busca, livro do dia, estatísticas, categorias, destaques, populares, lançamentos, recomendações (logado) e curiosidades literárias
- **Catálogo:** 30 livros do banco; busca por título/autor/gênero em tempo real; filtros de disponibilidade e nota 4+; ordenação A–Z, popularidade, avaliação e recentes
- **Detalhes do livro:** capa, sinopse, editora, ano, classificação, disponibilidade, avaliações, favoritar, lista de leitura e empréstimo
- **Usuários:** cadastro, login (senha com hash), edição de perfil
- **Empréstimos:** prazo de 14 dias, controle automático de exemplares, bloqueio de duplicidade, status (ativo/atrasado/devolvido), devolução e histórico
- **Minha estante:** favoritos, quero ler, já li e desafio anual de leitura com barra de progresso
- **Avaliações:** nota de 1 a 5 e comentário
- **Administração:** painel com estatísticas e gráficos, CRUD de livros, empréstimos e devoluções, usuários, novos autores e gêneros
- **Sobre:** informações da biblioteca (história, horários, regras, contato)

## Estrutura
- `database/schema.sql` — 10 tabelas (as 9 do diagrama MER + `curiosidades`)
- `database/seed.sql` — gêneros, autores, 30 livros e curiosidades
- `database/demo.sql` — empréstimos, avaliações, favoritos, listas e metas de demonstração
- `database/conexao.py` — conexão Python ↔ SQLite e inicialização do banco
- `models/` — classes (Usuario, Livro, Autor, Genero, Emprestimo, Avaliacao, Favorito, ListaLeitura, MetaLeitura, Curiosidade)
- `dao/` — acesso ao banco (um DAO por responsabilidade)
- `routes/` — rotas Flask que respondem JSON
- `templates/index.html`, `static/css/style.css`, `static/js/` — front-end

## Como executar (Windows + VS Code)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Abra http://127.0.0.1:5000. O banco `database/biblioteca.db` é criado e populado na primeira execução.
Para recriar do zero, apague `database/biblioteca.db` e rode `python app.py` novamente.

## Contas de demonstração
| Perfil | E-mail | Senha |
|---|---|---|
| Admin | admin@biblioteca.com | admin123 |
| Leitor | leitor@biblioteca.com | leitor123 |
| Leitores | ana@, bruno@, carla@biblioteca.com | demo123 |

## Roteiro de testes
1. Início: veja o livro do dia, clique numa categoria e em "Outra curiosidade".
2. Catálogo: busque "terror", ordene por popularidade, marque "Só disponíveis".
3. Entre como `leitor@biblioteca.com`: favorite livros (♥), marque "Quero ler" e "Marcar como lido" e veja a Minha estante e o desafio de leitura.
4. Abra um livro e solicite empréstimo; confira a quantidade e a tela Empréstimos; devolva.
5. Avalie um livro e veja a nota média no card.
6. Entre como admin: veja o painel, cadastre/edite/exclua um livro, registre devolução, adicione gênero.

## Observações
- Os livros são dados de exemplo; capas são geradas em CSS (ou use a URL da capa ao cadastrar).
- Repositório: adicionar o professor como colaborador (leonardo.stephan@eaportal.org).
