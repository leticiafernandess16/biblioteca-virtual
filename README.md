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
- `backend/app.py` — ponto de entrada da aplicação Flask
- `backend/config.py` — configurações e caminhos do projeto
- `backend/criar_banco.py` — script para criar ou recriar o banco
- `backend/exportar_demo.py` — exporta os dados do banco para o modo estático do GitHub Pages
- `backend/models/` — classes (Usuario, Livro, Autor, Genero, Emprestimo, Avaliacao, Favorito, ListaLeitura, MetaLeitura, Curiosidade)
- `backend/dao/` — acesso ao banco (um DAO por responsabilidade)
- `backend/routes/` — rotas Flask que respondem JSON
- `database/schema.sql` — 10 tabelas (as 9 do diagrama MER + `curiosidades`)
- `database/dados.sql` — gêneros, autores, 30 livros, curiosidades e dados de demonstração
- `database/conexao.py` — conexão Python ↔ SQLite e inicialização do banco
- `index.html`, `static/css/style.css`, `static/js/` — front-end
- `static/demo/` — dados exportados do banco para o modo demonstração do GitHub Pages

## Como executar (Windows + VS Code)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```
Abra http://127.0.0.1:5000. O banco `database/biblioteca.db` é criado e populado na primeira execução.

Também funciona executando de dentro da pasta `backend` (`cd backend` e depois `python app.py`) ou como módulo a partir da raiz (`python -m backend.app`).

Para recriar o banco do zero, rode `python backend/criar_banco.py --reset` (ou apague `database/biblioteca.db` e inicie o site novamente).

## Versão publicada (GitHub Pages)
O site também fica disponível em **https://leticiafernandess16.github.io/biblioteca-virtual/**.

O GitHub Pages serve apenas arquivos estáticos, sem Python/Flask/SQLite. Por isso, nos endereços `*.github.io`, ao abrir o `index.html` via `file://` ou com `?demo=1` na URL, o front-end entra em **modo demonstração**:

- `static/js/demo.js` responde às mesmas rotas `/api/...` usadas pelo front-end, simulando as regras do Flask (login, empréstimos, devoluções, favoritos, lista de leitura, metas, avaliações, painel e CRUD administrativo).
- Os dados iniciais vêm de `static/demo/dados.js`, exportados do banco SQLite por `backend/exportar_demo.py` (com 30 livros, 5 usuários, 10 empréstimos e 18 avaliações).
- As alterações feitas no site publicado (cadastros, empréstimos, favoritos etc.) ficam salvas no `localStorage` do navegador, nas chaves `biblioteca-lirio-dados-v1` e `biblioteca-lirio-sessao-v1`. Cada visitante trabalha com a própria cópia dos dados, e limpar os dados do site restaura o estado inicial.
- O Flask continua sendo a versão completa: em `http://127.0.0.1:5000` o modo demonstração não é ativado.

Se o banco for alterado, regenere os dados publicados e envie as alterações:

```
python backend/exportar_demo.py
git add static/demo
git commit -m "Atualiza dados do modo demonstração"
git push
```

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
- Os livros são dados de exemplo. As capas ficam em `static/img/<id>.<ext>` e são servidas pela rota `/capa/<id>`; se não houver imagem, a capa é gerada em CSS.
- Diagnóstico da reorganização para `backend/`: veja `docs/DIAGNOSTICO.md`.
- Repositório: adicionar o professor como colaborador (leonardo.stephan@eaportal.org).
