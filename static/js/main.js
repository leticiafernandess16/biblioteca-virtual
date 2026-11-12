// ===== Estado global e utilidades =====

// Armazena os dados do usuário que está conectado ao sistema.
// Inicialmente, o valor é null, indicando que não há usuário autenticado.
let usuario = null;

// Armazena os gêneros literários cadastrados na biblioteca.
let generos = [];

// Armazena os autores cadastrados no sistema.
let autores = [];

// Armazena os IDs dos livros favoritados pelo usuário.
let idsFav = new Set();   // ids dos livros favoritados pelo usuário

// Armazena a situação de leitura de cada livro, identificando se o usuário quer ler ou já leu.
let listaMap = {};        // id_livro -> 'quero_ler' | 'lido'

// Define todas as telas disponíveis no sistema.
const VIEWS = ["home", "catalogo", "auth", "estante", "emprestimos", "perfil", "admin", "sobre"];

// Função responsável por escapar caracteres especiais de textos.
// Evita que caracteres sejam interpretados como código HTML.
function esc(t) {
  return String(t ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Função assíncrona responsável por realizar requisições à API do sistema.
async function api(url, metodo = "GET", corpo = null) {
  // Define o método HTTP e os cabeçalhos da requisição.
  const opcoes = { method: metodo, headers: {} };

  // Verifica se existe um corpo de dados para enviar.
  if (corpo) {
    // Informa que os dados enviados estão no formato JSON.
    opcoes.headers["Content-Type"] = "application/json";

    // Converte o objeto recebido para uma string JSON.
    opcoes.body = JSON.stringify(corpo);
  }

  // Realiza a requisição ao endereço informado.
  const resp = await fetch(url, opcoes);

  // Converte a resposta recebida para JSON.
  // Caso a conversão falhe, utiliza um objeto vazio.
  const dados = await resp.json().catch(() => ({}));

  // Verifica se a resposta não foi bem-sucedida e lança uma mensagem de erro.
  if (!resp.ok) throw new Error(dados.erro || "Erro inesperado.");

  // Retorna os dados recebidos da API.
  return dados;
}

// Exibe mensagens temporárias na interface do sistema.
function toast(texto, erro = false) {
  // Obtém o elemento HTML responsável por mostrar as notificações.
  const el = document.getElementById("toast");

  // Define o texto da mensagem.
  el.textContent = texto;

  // Aplica a classe visual correspondente a uma mensagem normal ou de erro.
  el.className = "toast" + (erro ? " erro" : "");

  // Torna a notificação visível.
  el.hidden = false;

  // Cancela o temporizador anterior, caso exista.
  clearTimeout(toast.t);

  // Define um temporizador para ocultar a mensagem após 3,5 segundos.
  toast.t = setTimeout(() => (el.hidden = true), 3500);
}

// Recebe um erro e exibe sua mensagem por meio da notificação visual.
function tratarErro(e) { toast(e.message || "Erro inesperado.", true); }

// ===== Navegação entre telas =====

// Monta os botões de navegação conforme o usuário e a tela selecionada.
function montarNav(ativa) {
  // Cria uma função auxiliar para gerar cada botão do menu.
  // Adiciona a classe "ativo" quando o botão corresponde à tela atual.
  const item = (v, rotulo, cls = "") =>
    `<button class="${cls} ${ativa === v ? "ativo" : ""}" onclick="mostrarView('${v}')">${rotulo}</button>`;

  // Adiciona os botões de início e catálogo ao menu.
  let html = item("home", "Início") + item("catalogo", "Catálogo");

  // Verifica se existe um usuário autenticado.
  if (usuario) {
    // Adiciona as opções de estante pessoal e empréstimos.
    html += item("estante", "Minha estante") + item("emprestimos", "Empréstimos");

    // Verifica se o usuário possui perfil administrativo.
    if (usuario.tipo === "admin") html += item("admin", "Administração");

    // Adiciona a opção de acesso ao perfil.
    html += item("perfil", "Perfil");
  }

  // Adiciona a opção de informações sobre o sistema.
  html += item("sobre", "Sobre");

  // Exibe o botão de sair quando existe um usuário conectado.
  // Caso contrário, exibe a opção de entrar ou cadastrar.
  html += usuario
    ? `<button class="destaque" onclick="sair()">Sair (${esc(usuario.nome.split(" ")[0])})</button>`
    : item("auth", "Entrar / Cadastrar", "destaque");

  // Insere os botões criados no elemento de navegação.
  document.getElementById("nav").innerHTML = html;
}

// Controla a troca entre as diferentes telas do sistema.
function mostrarView(nome) {
  // Verifica se o usuário tenta acessar uma área que exige autenticação.
  if (["estante", "emprestimos", "perfil"].includes(nome) && !usuario) {
    // Exibe um aviso solicitando que o usuário faça login.
    toast("Faça login para acessar esta área.", true);

    // Redireciona para a tela de autenticação.
    nome = "auth";
  }

  // Impede o acesso à administração por usuários que não possuem perfil administrativo.
  if (nome === "admin" && (!usuario || usuario.tipo !== "admin")) nome = usuario ? "home" : "auth";

  // Percorre todas as telas e deixa visível somente aquela selecionada.
  VIEWS.forEach(v => (document.getElementById("view-" + v).hidden = v !== nome));

  // Atualiza o endereço da página com o nome da tela atual.
  history.replaceState(null, "", "#" + nome);

  // Fecha o menu de navegação, caso esteja aberto.
  document.getElementById("nav").classList.remove("aberto");

  // Atualiza os botões do menu de acordo com a tela atual.
  montarNav(nome);

  // Faz a página voltar ao início da rolagem.
  window.scrollTo(0, 0);

  // Relaciona cada tela à função responsável por carregar seus dados.
  const carregar = { home: carregarHome, catalogo: carregarCatalogo, estante: carregarEstante,
    emprestimos: carregarMeusEmprestimos, perfil: preencherPerfil, admin: carregarAdmin }[nome];

  // Executa a função correspondente à tela selecionada, caso exista.
  // Também trata possíveis erros durante o carregamento.
  if (carregar) Promise.resolve(carregar()).catch(tratarErro);
}

// ===== Componentes visuais de livros =====

// Define combinações de cores utilizadas na criação das capas ilustrativas dos livros.
// Cada posição contém duas cores de fundo e uma cor para o texto.
const CAPAS = [
  ["#f9c6dc", "#d4b5f0", "#3b2a52"], ["#e6d5f7", "#b79ce0", "#3b2a52"], ["#fbd3e0", "#f29cc0", "#3b2a52"],
  ["#cdb7f0", "#7d5bb5", "#ffffff"], ["#fde2ea", "#e0b3da", "#3b2a52"], ["#bda6e8", "#f3b2d0", "#3b2a52"],
  ["#f4a9c6", "#9a74cf", "#ffffff"], ["#e9dcfa", "#f9d0e2", "#3b2a52"], ["#d9c3f3", "#c78ac0", "#3b2a52"],
  ["#f7cde0", "#a98ad8", "#3b2a52"],
];

// Define os ícones utilizados nas capas ilustrativas dos livros.
const ICONES = ["💌", "🐉", "🚀", "🕵️", "🔎", "🦇", "🧭", "🏛️", "🎭", "🌱"];

// Gera o código HTML de uma capa de livro.
function capaHTML(l, grande = false) {
  // Calcula o índice utilizado para escolher as cores e o ícone da capa.
  const i = (l.id_genero - 1) % CAPAS.length;

  // Obtém as duas cores de fundo e a cor do texto correspondentes.
  const [c1, c2, txt] = CAPAS[i];

  // Verifica se o livro possui uma imagem de capa cadastrada.
  // Se possuir, cria uma imagem com texto alternativo.
  // Caso ocorra um erro ao carregar a imagem, ela será removida.
  const img = l.capa_url ? `<img src="${esc(l.capa_url)}" alt="Capa de ${esc(l.titulo)}" onerror="this.remove()">` : "";

  // Retorna a estrutura HTML da capa com cores, ícone, título e autor.
  return `<div class="capa ${grande ? "grande" : ""}" style="background:linear-gradient(160deg,${c1},${c2});color:${txt}">
    <span class="c-ico">${ICONES[i]}</span>
    <span class="c-titulo">${esc(l.titulo)}</span>
    <span class="c-autor">${esc(l.autor)}</span>${img}</div>`;
}

// Formata a nota média do livro para exibição.
// Se não houver avaliações, apresenta a mensagem "Sem notas".
function notaTxt(l) {
  return l.nota_media ? `★ ${Number(l.nota_media).toFixed(1)}` : "Sem notas";
}

// Cria o cartão visual de um livro para exibição nas listas do sistema.
function cardLivro(l) {
  // Cria o botão de favorito somente quando existe um usuário autenticado.
  // A aparência do botão depende de o livro já estar favoritado.
  const coracao = usuario
    ? `<button class="coracao ${idsFav.has(l.id_livro) ? "on" : ""}" data-id="${l.id_livro}" title="Favoritar"
         onclick="event.stopPropagation();alternarFavorito(${l.id_livro})">♥</button>` : "";

  // Retorna a estrutura HTML do cartão com capa, título, autor, gênero, nota e disponibilidade.
  // Ao clicar no cartão, são abertos os detalhes do livro.
  return `<div class="card" onclick="abrirDetalhes(${l.id_livro})">
    ${coracao}${capaHTML(l)}
    <h3>${esc(l.titulo)}</h3>
    <div class="autor">${esc(l.autor)}</div>
    <span class="tag">${esc(l.genero)}</span>
    <div class="linha"><span class="nota">${notaTxt(l)}</span>
      <span class="${l.disponivel ? "ok" : "nao"}">${l.disponivel ? l.quantidade_disponivel + " disp." : "Indisponível"}</span></div>
  </div>`;
}

// Exibe as estatísticas gerais da biblioteca na página inicial.
function renderStats(el, s) {
  // Cria os indicadores de livros, usuários e empréstimos.
  // Os valores começam em zero e são armazenados no atributo data-n.
  el.innerHTML = `
    <div class="stat"><b data-n="${s.livros}">0</b><span>livros no acervo</span></div>
    <div class="stat"><b data-n="${s.usuarios}">0</b><span>leitores</span></div>
    <div class="stat"><b data-n="${s.emprestimos_total}">0</b><span>empréstimos realizados</span></div>
    <div class="stat"><b data-n="${s.emprestimos_ativos}">0</b><span>empréstimos ativos</span></div>`;

  // Seleciona todos os indicadores que possuem o atributo data-n.
  el.querySelectorAll("b[data-n]").forEach(b => {
    // Obtém o valor final que deverá ser apresentado no indicador.
    const alvo = +b.dataset.n;

    // Inicializa a contagem em zero.
    let n = 0;

    // Calcula o incremento utilizado na animação dos números.
    const passo = Math.max(1, Math.ceil(alvo / 25));

    // Atualiza o número gradualmente até alcançar o valor final.
    const t = setInterval(() => { n = Math.min(alvo, n + passo); b.textContent = n; if (n >= alvo) clearInterval(t); }, 25);
  });
}

// ===== Estado do usuário (favoritos e lista de leitura) =====

// Atualiza os dados de favoritos e da lista pessoal de leitura do usuário.
async function recarregarEstado() {
  // Se não houver usuário autenticado, limpa os dados pessoais armazenados.
  if (!usuario) { idsFav = new Set(); listaMap = {}; return; }

  // Busca na API os dados da estante pessoal do usuário.
  const d = await api("/api/estante");

  // Atualiza o conjunto de IDs dos livros favoritados.
  idsFav = new Set(d.ids_favoritos);

  // Atualiza o mapa com a situação de leitura dos livros.
  listaMap = d.lista;
}

// Adiciona ou remove um livro dos favoritos do usuário.
async function alternarFavorito(id) {
  try {
    // Envia uma requisição POST para alternar o estado de favorito do livro.
    const d = await api("/api/favoritos/" + id, "POST");

    // Atualiza o conjunto local conforme o resultado retornado pela API.
    // Adiciona o ID quando favoritado ou remove quando não estiver mais favoritado.
    d.favoritado ? idsFav.add(id) : idsFav.delete(id);

    // Exibe a mensagem de confirmação.
    toast(d.mensagem);

    // Atualiza a aparência dos botões de favorito que correspondem ao livro selecionado.
    document.querySelectorAll(`.coracao[data-id="${id}"]`).forEach(b => b.classList.toggle("on", d.favoritado));

    // Se a estante estiver aberta, atualiza seu conteúdo.
    if (!document.getElementById("view-estante").hidden) carregarEstante();

    // Se a janela de detalhes estiver aberta, atualiza suas informações.
    if (!document.getElementById("modal").hidden) abrirDetalhes(id);
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao alterar os favoritos.
}

// ===== Eventos =====

// Configura os eventos de interação dos elementos da página.
function ligarEventos() {
  // Cria uma função auxiliar para selecionar elementos HTML pelo ID.
  const $ = id => document.getElementById(id);

  // Variável utilizada para controlar o atraso da pesquisa no catálogo.
  let t;

  // Detecta alterações no campo de busca.
  // Aguarda 250 milissegundos após a digitação antes de atualizar o catálogo.
  $("busca").addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => carregarCatalogo().catch(tratarErro), 250); });

  // Detecta alterações nos filtros e atualiza o catálogo automaticamente.
  ["filtro-genero", "filtro-ordem", "filtro-disp", "filtro-nota"].forEach(id =>
    $(id).addEventListener("change", () => carregarCatalogo().catch(tratarErro)));

  // Associa o botão de login à função responsável pela autenticação.
  $("btn-login").addEventListener("click", entrar);

  // Associa o botão de cadastro à função responsável pelo registro de usuários.
  $("btn-cadastro").addEventListener("click", cadastrar);

  // Associa o botão de perfil à função que salva as alterações dos dados pessoais.
  $("btn-perfil").addEventListener("click", salvarPerfil);

  // Associa o botão de salvar livro à função de cadastro ou edição.
  $("btn-salvar-livro").addEventListener("click", salvarLivro);

  // Associa o botão de cancelar à função que limpa o formulário de livros.
  $("btn-cancelar").addEventListener("click", limparFormLivro);

  // Associa o botão de adicionar autor à função de cadastro de autores.
  $("btn-autor").addEventListener("click", novoAutor);

  // Associa o botão de adicionar gênero à função de cadastro de gêneros.
  $("btn-genero").addEventListener("click", novoGenero);

  // Controla a abertura e o fechamento do menu de navegação.
  $("menu-btn").addEventListener("click", () => $("nav").classList.toggle("aberto"));

  // Fecha a janela modal quando o usuário clica fora de seu conteúdo.
  $("modal").addEventListener("click", e => { if (e.target.id === "modal") fecharModal(); });

  // Fecha a janela modal quando a tecla Escape é pressionada.
  document.addEventListener("keydown", e => { if (e.key === "Escape") fecharModal(); });

  // Permite realizar o login ao pressionar Enter no campo de senha.
  $("login-senha").addEventListener("keydown", e => { if (e.key === "Enter") entrar(); });

  // Controla a troca entre as abas da estante pessoal.
  $("abas-estante").addEventListener("click", e => {
    // Verifica se o elemento clicado corresponde a uma aba.
    if (!e.target.dataset.aba) return;

    // Atualiza a variável que identifica a aba selecionada.
    abaEstante = e.target.dataset.aba;

    // Atualiza a aparência das abas, destacando somente a selecionada.
    document.querySelectorAll("#abas-estante .aba").forEach(b => b.classList.toggle("ativa", b === e.target));

    // Atualiza os livros exibidos conforme a aba selecionada.
    renderEstante();
  });

  // Controla a troca entre as abas da área administrativa.
  $("abas-admin").addEventListener("click", e => {
    // Verifica se o elemento clicado corresponde a uma aba.
    if (!e.target.dataset.aba) return;

    // Atualiza a aparência das abas administrativas.
    document.querySelectorAll("#abas-admin .aba").forEach(b => b.classList.toggle("ativa", b === e.target));

    // Exibe somente o conteúdo da aba administrativa selecionada.
    document.querySelectorAll(".admin-aba").forEach(d => (d.hidden = d.id !== "admin-" + e.target.dataset.aba));
  });
}

// Função assíncrona responsável por iniciar o funcionamento do sistema.
async function iniciar() {
  try {
    // Consulta a API para verificar se existe um usuário autenticado.
    usuario = (await api("/api/me")).usuario;

    // Carrega os favoritos e a lista pessoal de leitura do usuário.
    await recarregarEstado();

    // Busca os gêneros cadastrados no banco de dados.
    generos = await api("/api/generos");

    // Preenche o filtro de gêneros com os dados recebidos.
    preencherFiltroGeneros();

    // Configura os eventos de interação dos elementos da página.
    ligarEventos();

    // Obtém o nome da tela indicado na URL.
    const alvo = location.hash.replace("#", "");

    // Verifica se a tela indicada existe.
    // Caso exista, abre essa tela; caso contrário, abre a página inicial.
    mostrarView(VIEWS.includes(alvo) ? alvo : "home");
<<<<<<< HEAD
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante a inicialização.
=======
  } catch (e) { tratarErro(e); }
}

// ===== Capa do livro (imagem com emoji de reserva) =====
function escaparHtml(texto) {
  return String(texto ?? "").replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function htmlCapa(livro, classe = "") {
  const url = livro && livro.capa_url ? escaparHtml(livro.capa_url) : "";
  const titulo = escaparHtml(livro && livro.titulo ? livro.titulo : "Livro");
  const img = url
    ? `<img class="capa-img" src="${url}" alt="Capa de ${titulo}" loading="lazy"
            onerror="this.remove()">`
    : "";
  return `<div class="capa-box ${classe}">${img}<span class="capa-emoji">📖</span></div>`;
>>>>>>> 1048b47c7f9eda725e67b1526e07987250b44414
}