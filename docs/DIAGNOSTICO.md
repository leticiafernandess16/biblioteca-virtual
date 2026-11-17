# Diagnóstico — Biblioteca Virtual Lírio

**Data:** 17/11/2026  
**Repositório:** `C:\Users\nogueira_leticia\Documents\GitHub\biblioteca-virtual`  
**Branch:** `main` — HEAD `4f2c7a3` ("ajustes 2")  
**Ambiente:** Windows, Python 3.14.3, Flask 3.1.3 (testado em venv temporário fora do projeto)

> Este documento registra o diagnóstico feito **antes de qualquer alteração no código**. As correções recomendadas na seção 8 foram aplicadas em seguida e estão resumidas na seção 11.

---

## 1. Resumo executivo

Existem **dois problemas independentes**:

1. **Fatal no front-end:** a função `iniciar()` foi apagada de `static/js/main.js` no commit `e913b97` (13/11), mas `index.html` continua chamando `iniciar();` na linha 235. O navegador lança `ReferenceError: iniciar is not defined` e **nada é carregado** (menu, livros, estatísticas, botões, eventos).
2. **Estrutural (mudança para `backend/`):** o comando documentado `python app.py` não existe mais na raiz, e o modo `python -m backend.app` falha com `ModuleNotFoundError: No module named 'config'`. Só funciona `python backend/app.py` (ou `cd backend` + `python app.py`).

O **back-end está saudável**: banco, rotas e APIs responderam corretamente nos testes. A mudança de pastas **não foi a causa do site vazio** — essa regressão veio do commit `e913b97`, anterior à reorganização. As duas coisas se somaram e deram a impressão de que "tudo quebrou junto".

---

## 2. Como o diagnóstico foi feito

- Leitura da estrutura e dos imports de todos os módulos.
- Comparação com o histórico do Git (`git log`, `git show`, `git diff`).
- Execução real do servidor com Flask instalado em um venv temporário **fora do projeto**.
- Teste de todas as rotas com `Invoke-WebRequest`.
- Abertura do site no navegador integrado e leitura do console JavaScript.
- Teste da função ausente injetada em memória (sem alterar arquivos) para provar a causa.

O `database/biblioteca.db` foi apenas aberto pelos testes e depois restaurado com `git restore`; a árvore de trabalho ficou limpa.

---

## 3. Estrutura atual

```
biblioteca-virtual/
├── backend/
│   ├── app.py              <- ponto de entrada do Flask
│   ├── config.py
│   ├── criar_banco.py
│   ├── dao/                (6 DAOs + __init__.py)
│   ├── models/             (10 modelos + __init__.py)
│   └── routes/             (6 rotas + __init__.py)
├── database/
│   ├── biblioteca.db
│   ├── conexao.py
│   ├── dados.sql
│   └── schema.sql
├── static/
│   ├── css/style.css
│   ├── img/*.jpg|*.webp
│   └── js/main.js, livros.js, emprestimos.js, usuarios.js
├── docs/
├── index.html              <- página servida pela rota "/"
├── templates               <- ARQUIVO VAZIO (0 bytes), não é pasta
├── README.md
└── requirements.txt
```

O commit `58af933` ("backend") foi **apenas um rename** (`git show --stat` mostra 0 inserções e 0 remoções). Os ajustes de caminho vieram depois, em `ba0d541` e `4f2c7a3`.

---

## 4. Causa raiz nº 1 (fatal) — `iniciar is not defined`

### 4.1 Evidências

**`index.html`, linha 235:**
```html
<script>iniciar();</script>
```

**`static/js/main.js`:** tem 248 linhas, termina na função `ligarEventos()` e **não define `iniciar` em nenhum lugar**. Uma busca em todos os JS confirma:
```
grep "iniciar" static/js/*.js  -> nenhum resultado
```

**Console do navegador ao abrir `http://127.0.0.1:5000/`:**
```
ReferenceError: iniciar is not defined
    at http://127.0.0.1:5000/:235:9
```

### 4.2 Quando a função foi apagada

O commit **`e913b97` — "Capas dos livros por id" (13/11/2026)** alterou `capaHTML` e, no mesmo commit, **removeu o final do `main.js`**, incluindo:

```js
async function iniciar() {
  try {
    usuario = (await api("/api/me")).usuario;
    await recarregarEstado();
    generos = await api("/api/generos");
    preencherFiltroGeneros();
    ligarEventos();
    const alvo = location.hash.replace("#", "");
    mostrarView(VIEWS.includes(alvo) ? alvo : "home");
  } catch (e) { tratarErro(e); }
}

// ===== Capa do livro (imagem com emoji de reserva) =====
function escaparHtml(texto) { ... }

function htmlCapa(livro, classe = "") { ... }
```

Confirmações:
- `git show e913b97^:static/js/main.js` → **tinha** `async function iniciar()`.
- `git show e913b97:static/js/main.js` → **não tem mais**.
- Todos os commits posteriores (`899a7da`, `ff736ec`, `4789a05`, `93c33ab`, `58af933`, `4f2c7a3`) **nunca recolocaram** a função.
- `git show e913b97^:index.html` já chamava `iniciar();` — ou seja, a chamada ficou órfã.

> Observação: os commits `899a7da` ("Resolve conflito no main.js") e `ff736ec` ("restaura app/CSS") tentaram recuperar partes do arquivo, mas não restauraram `iniciar()`.

### 4.3 O que deixou de acontecer

Sem `iniciar()`:

- nenhuma chamada a `/api/me` (usuário logado não é restaurado);
- nenhuma chamada a `/api/generos` (filtro de gêneros vazio);
- `ligarEventos()` nunca roda (nenhum botão funciona: login, cadastro, busca, filtros, menu, modal, abas);
- `mostrarView("home")` nunca roda (a home não carrega `/api/home`);
- conseqüência: **nenhum livro, estatística, categoria ou curiosidade aparece**, e o site parece "morto", mesmo com HTML e CSS carregando.

### 4.4 Prova de que é só isso

Com a página aberta, injetei a função `iniciar()` original **em memória** (sem editar arquivos) e executei. Resultado imediato:

```
destaqueCards: 8
popularCards: 8
stats: "30 | livros no acervo | 5 | leitores | 10 | empréstimos realizados | 5 | empréstimos ativos"
nav: "Início | Catálogo | Sobre | Entrar / Cadastrar"
livroDia: "O Iluminado — Stephen King"
viewHome: true
```

Ou seja: **restaurar a função resolve o site vazio**.

### 4.5 Correção necessária

Recolocar em `static/js/main.js` (no final, ou antes de `ligarEventos`) exatamente:

```js
async function iniciar() {
  try {
    usuario = (await api("/api/me")).usuario;
    await recarregarEstado();
    generos = await api("/api/generos");
    preencherFiltroGeneros();
    ligarEventos();
    const alvo = location.hash.replace("#", "");
    mostrarView(VIEWS.includes(alvo) ? alvo : "home");
  } catch (e) { tratarErro(e); }
}
```

Todas as funções chamadas por ela (`api`, `recarregarEstado`, `preencherFiltroGeneros`, `ligarEventos`, `mostrarView`, `tratarErro`) existem no código atual.

---

## 5. Causa raiz nº 2 — a mudança para `backend/` quebrou a execução

### 5.1 `python app.py` na raiz não funciona mais

O `README.md` ainda instrui (linhas 31 e 33):
```
python app.py
```

Resultado real:
```
python.exe: can't open file '...\biblioteca-virtual\app.py': [Errno 2] No such file or directory
```

O arquivo agora está em `backend/app.py`. O comando correto é:
```
python backend/app.py
```
ou
```
cd backend
python app.py
```

### 5.2 `python -m backend.app` também falha

Resultado real:
```
File "...\backend\app.py", line 13, in <module>
    import config
ModuleNotFoundError: No module named 'config'
```

**Por quê:** os imports são de pacotes "de topo" (`import config`, `from dao...`, `from models...`, `from routes...`). Eles só são encontrados quando a pasta `backend/` está no `sys.path`.

- `python backend/app.py` → o Python coloca automaticamente a pasta do script (`backend/`) no início do `sys.path`. Funciona.
- `python -m backend.app` → o `sys.path[0]` é a raiz do projeto, não `backend/`. `config`, `dao`, `models` e `routes` não são encontrados. Falha.

O mesmo acontece com `python -m backend.criar_banco`:
```
ModuleNotFoundError: No module named 'config'
```
Já `python backend/criar_banco.py` funciona:
```
Banco pronto em: ...\database\biblioteca.db
```

### 5.3 Por que `python backend/app.py` funciona

O próprio `backend/app.py` faz:
```python
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(RAIZ)
```
Isso coloca a raiz no path (para achar `database/`), e a pasta do script já está no path (para achar `config`, `dao`, `models`, `routes`). Por isso o servidor sobe e as APIs respondem.

### 5.4 Efeito no VS Code / Pylance

Se o VS Code abre a pasta raiz, o analisador Python não sabe que `backend/` é a raiz dos imports. É comum aparecerem avisos do tipo:

```
Import "config" could not be resolved
Import "dao.livro_dao" could not be resolved
```

Isso **não impede o `python backend/app.py` de rodar**, mas confunde e faz parecer que "nada está linkando". Opções:
- adicionar `.vscode/settings.json` com `"python.analysis.extraPaths": ["./backend"]`; ou
- converter o projeto em pacote de verdade (ver 5.5).

### 5.5 Correções recomendadas para a estrutura

**Opção A — mínima e segura (recomendada para agora):**

No topo de `backend/app.py` e `backend/criar_banco.py`, garantir explicitamente as duas pastas no path:

```python
import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))   # .../backend
RAIZ = os.path.dirname(BASE)                        # .../biblioteca-virtual
for p in (BASE, RAIZ):
    if p not in sys.path:
        sys.path.insert(0, p)
```

Assim `python backend/app.py`, `cd backend && python app.py` e `python -m backend.app` passam a funcionar. Depois, atualizar o README.

**Opção B — pacote "correto" (mais invasiva):**

- criar `backend/__init__.py`;
- trocar `import config` por `from backend import config`;
- trocar `from dao...` por `from backend.dao...`, e assim por diante;
- ajustar `database/conexao.py` e `backend/dao/emprestimo_dao.py`, que também fazem `import config`;
- executar com `python -m backend.app`.

A Opção A resolve o problema com menos risco e sem renomear imports.

---

## 6. Problemas secundários encontrados

| # | Arquivo | Evidência | Impacto | Correção sugerida |
|---|---|---|---|---|
| 1 | `templates` (raiz) | É um **arquivo de 0 bytes**, não uma pasta (`Test-Path -PathType Container` = `False`) | Hoje não quebra porque nenhuma rota usa `render_template`. Mas o README diz `templates/index.html`, que não existe. Se alguém usar templates, o Flask falha | Apagar o arquivo `templates` ou transformá-lo em pasta com o HTML, se for adotar `render_template` |
| 2 | `backend/config.py` linhas 14 e 17 | `SEED_PATH` e `DEMO_PATH` apontam para `database/seed.sql` e `database/demo.sql`, que **não existem** (só existe `dados.sql`) | Código morto/enganoso; qualquer uso futuro gera `FileNotFoundError` | Remover as constantes ou criar os arquivos |
| 3 | `.gitignore` linha 14 | `database/biblioteca.dbdatabase/*.bak` (falta quebra de linha; virou um padrão único) | `database/biblioteca.db` **não é ignorado** e está versionado (`git ls-files` confirma); qualquer empréstimo/login suja o Git com binário | Corrigir para `database/biblioteca.db` em linha própria; remover duplicatas de `*.bak` |
| 4 | `README.md` linhas 21-24 e 31-33 | Diz que `models/`, `dao/`, `routes/` ficam na raiz e que o HTML está em `templates/index.html`; manda rodar `python app.py` | Instruções não funcionam | Atualizar estrutura e comandos |
| 5 | `index.html` linha 7 e 231-234 | Usa caminhos relativos (`static/css/...`, `static/js/...`) | Funciona em `/`, mas quebra se a página for servida em subpasta | Usar `/static/...` (absoluto) |
| 6 | Rotas | `/api/admin/estatisticas` retorna 404 | Não é bug do front (o JS usa `/api/admin/painel`, que existe) | Nenhuma; apenas documentar que o endpoint correto é `/api/admin/painel` |
| 7 | Ambiente | Flask **não está instalado** no Python global e **não existe venv** no projeto | `python backend/app.py` falha com `ModuleNotFoundError: No module named 'flask'` em uma instalação limpa | Criar venv e instalar `requirements.txt` |

---

## 7. O que está funcionando (testes reais)

Servidor iniciado com `python backend/app.py` (Flask 3.1.3, Python 3.14.3):

| Rota | Resultado |
|---|---|
| `/` | 200 — 11.309 bytes |
| `/static/css/style.css` | 200 — 12.408 bytes |
| `/static/js/main.js` | 200 — 13.335 bytes |
| `/static/js/livros.js` | 200 — 12.526 bytes |
| `/static/js/usuarios.js` | 200 — 7.285 bytes |
| `/static/js/emprestimos.js` | 200 — 13.136 bytes |
| `/capa/1` | 200 — 368.124 bytes |
| `/api/home` | 200 — 19.446 bytes |
| `/api/livros` | 200 — 19.643 bytes |
| `/api/estatisticas` | 200 |
| `/api/autores` | 200 |
| `/api/generos` | 200 |
| `/api/curiosidade` | 200 |
| `/api/login` (admin) | 200 — sessão criada |
| `/api/me` | 200 |
| `/api/estante` | 200 |
| `/api/admin/painel` | 200 |
| `/api/emprestimos/meus` | 200 |

Também foi validado que **todas as URLs chamadas pelo JavaScript existem** no `url_map` do Flask (login, cadastro, logout, perfil, home, livros, autores, gêneros, favoritos, lista, meta, estante, empréstimos, admin, recomendações, curiosidade, capa).

O `401` em `/api/estante` e `/api/recomendacoes` sem sessão é o comportamento esperado.

---

## 8. Plano de correção aplicado

1. ✅ **Crítico:** restaurada `iniciar()` no fim de `static/js/main.js`.
2. ✅ **Estrutural:** `BASE` e `RAIZ` inseridos explicitamente no `sys.path` em `backend/app.py` e `backend/criar_banco.py` (Opção A).
3. ✅ **Limpeza:** removido o arquivo vazio `templates`; removidos `SEED_PATH`/`DEMO_PATH` de `config.py`; corrigido o `.gitignore` e removido `database/biblioteca.db` do versionamento (o arquivo local foi preservado).
4. ✅ **Documentação:** `README.md` atualizado com a nova estrutura e os comandos corretos.
5. ✅ **Ambiente:** criado `venv` no projeto e instalado `requirements.txt` (Flask 3.1.3).
6. ✅ **Validação final:** site aberto no navegador, console sem erros, home com 8 destaques, login admin, catálogo com 30 livros, painel admin e estante testados.

---

## 9. Comandos para reproduzir os erros

```powershell
# Erro 1: função ausente (abrir o site e olhar o console do navegador)
python backend/app.py
# ReferenceError: iniciar is not defined (index.html:235)

# Erro 2: comando antigo do README
python app.py
# can't open file '...\app.py'

# Erro 3: modo módulo
python -m backend.app
# ModuleNotFoundError: No module named 'config'

# O que funciona hoje:
python backend/app.py
# ou
cd backend
python app.py
```

---

## 10. Conclusão

- O back-end e o banco estão íntegros.
- O site "não linka nada" porque **`iniciar()` foi removido do `main.js`** e a chamada ficou no HTML. Essa é a correção que devolve a vida ao front-end.
- A mudança para `backend/` quebrou o **comando de execução** e os imports em modo módulo; isso foi alinhado no código e no README.
- O arquivo vazio `templates`, as constantes inexistentes em `config.py`, o `.gitignore` malformado e o README desatualizado eram pendências secundárias e também foram corrigidos.

---

## 11. Correções aplicadas e validação final

### Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `static/js/main.js` | Restaurada a função `iniciar()`, que inicializa usuário, estante, gêneros, eventos e a tela inicial |
| `backend/app.py` | `BASE` e `RAIZ` inseridos no `sys.path`; funciona com `python backend/app.py` e `python -m backend.app` |
| `backend/criar_banco.py` | Mesmo ajuste de path; funciona como script e como módulo |
| `backend/config.py` | Removidos `SEED_PATH` e `DEMO_PATH` (arquivos inexistentes) |
| `index.html` | Caminhos de CSS/JS alterados para absolutos (`/static/...`) |
| `.gitignore` | Corrigida a linha do banco e duplicatas; `database/biblioteca.db` agora é ignorado |
| `README.md` | Estrutura e comandos de execução atualizados |
| `templates` | Arquivo vazio removido (não era usado) |
| `database/biblioteca.db` | Removido do versionamento com `git rm --cached`; o arquivo local foi preservado |
| `.vscode/settings.json` | Adicionado `python.analysis.extraPaths` para o Pylance achar `backend/` |
| `docs/DIAGNOSTICO.md` | Este diagnóstico |

### Validação executada

- `python backend/app.py` → `/` HTTP 200 e `/api/home` HTTP 200.
- `python -m backend.app` → `/` HTTP 200 e `/api/home` HTTP 200.
- Navegador: **zero erros no console**.
- Home: 30 livros, 5 leitores, 10 empréstimos realizados, 5 ativos; 8 destaques, 8 populares e 8 lançamentos.
- Catálogo: 30 livros encontrados.
- Login `admin@biblioteca.com` / `admin123`: menu com Administração, Perfil e Sair; painel admin carregado.
- Minha estante: desafio de leitura, favoritos, quero ler e já li carregados.
- `python -m compileall backend database`: compilação Python OK.
- `venv` criado no projeto com Flask 3.1.3.

### Como rodar agora

```powershell
cd C:\Users\nogueira_leticia\Documents\GitHub\biblioteca-virtual
venv\Scripts\activate
python backend/app.py
```

Ou, a partir da raiz com o venv ativo:

```powershell
python -m backend.app
```

Abra `http://127.0.0.1:5000`.

### Situação do Git

Nada foi commitado. As alterações estão na working tree; a remoção de `database/biblioteca.db` e do arquivo `templates` do versionamento está **staged** (`git status` mostra `D`). O banco local continua em `database/biblioteca.db` e será recriado automaticamente em um clone novo na primeira execução.
