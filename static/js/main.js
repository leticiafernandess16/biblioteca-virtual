// ===== Estado global e utilidades =====

// Guarda os dados do usuário que está conectado
let usuario = null;

// Armazena os gêneros e autores dos livros
let generos = [];
let autores = [];

// Armazena os IDs dos livros favoritados pelo usuário
let idsFav = new Set();

// Guarda os livros da lista de leitura e sua situação:
// 'quero_ler' para livros que deseja ler e 'lido' para livros já lidos
let listaMap = {};

// Lista de todas as telas disponíveis no sistema
const VIEWS = ["home", "catalogo", "auth", "estante", "emprestimos", "perfil", "admin", "sobre"];

// ===== Função para proteger textos =====

function esc(t) {
  // Transforma o valor em texto e substitui caracteres especiais por códigos HTML
  // Isso evita que textos sejam interpretados como códigos HTML
  return String(t ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// ===== Comunicação com a API =====

async function api(url, metodo = "GET", corpo = null) {
  // Define o método da requisição e os cabeçalhos
  const opcoes = { method: metodo, headers: {} };

  // Se existir um corpo de dados, prepara o envio em formato JSON
  if (corpo) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }

  // Envia a requisição para a API
  const resp = await fetch(url, opcoes);

  // Converte a resposta para JSON
  // Se não conseguir converter, utiliza um objeto vazio
  const dados = await resp.json().catch(() => ({}));

  // Verifica se a requisição apresentou algum erro
  if (!resp.ok) throw new Error(dados.erro || "Erro inesperado.");

  // Retorna os dados recebidos
  return dados;
}

// ===== Mensagens de aviso =====

function toast(texto, erro = false) {
  // Busca o elemento responsável por mostrar as mensagens
  const el = document.getElementById("toast");

  // Define o texto da mensagem
  el.textContent = texto;

  // Adiciona a classe de erro quando necessário
  el.className = "toast" + (erro ? " erro" : "");

  // Torna a mensagem visível
  el.hidden = false;

  // Cancela o temporizador anterior, caso exista
  clearTimeout(toast.t);

  // Esconde a mensagem automaticamente após 3,5 segundos
  toast.t = setTimeout(() => (el.hidden = true), 3500);
}

// Exibe uma mensagem de erro utilizando a função toast
function tratarErro(e) { toast(e.message || "Erro inesperado.", true); }


// ===== Navegação entre telas =====

function montarNav(ativa) {
  // Cria o HTML de um botão da navegação
  // Destaca o botão correspondente à tela que está aberta
  const item = (v, rotulo, cls = "") =>
    `<button class="${cls} ${ativa === v ? "ativo" : ""}" onclick="mostrarView('${v}')">${rotulo}</button>`;

  // Adiciona os botões Início e Catálogo
  let html = item("home", "Início") + item("catalogo", "Catálogo");

  // Verifica se existe um usuário conectado
  if (usuario) {
    // Adiciona as opções disponíveis para usuários conectados
    html += item("estante", "Minha estante") + item("emprestimos", "Empréstimos");

    // Verifica se o usuário possui permissão de administrador
    if (usuario.tipo === "admin") html += item("admin", "Administração");

    // Adiciona a opção de perfil
    html += item("perfil", "Perfil");
  }

  // Adiciona a opção Sobre
  html += item("sobre", "Sobre");

  // Se existir um usuário conectado, mostra o botão Sair
  // Caso contrário, mostra Entrar / Cadastrar
  html += usuario
    ? `<button class="destaque" onclick="sair()">Sair (${esc(usuario.nome.split(" ")[0])})</button>`
    : item("auth", "Entrar / Cadastrar", "destaque");

  // Insere os botões criados na área de navegação
  document.getElementById("nav").innerHTML = html;
}

function mostrarView(nome) {
  // Verifica se o usuário está tentando acessar uma tela que exige login
  if (["estante", "emprestimos", "perfil"].includes(nome) && !usuario) {
    toast("Faça login para acessar esta área.", true);
    nome = "auth";
  }

  // Impede que usuários comuns acessem a área administrativa
  if (nome === "admin" && (!usuario || usuario.tipo !== "admin")) nome = usuario ? "home" : "auth";

  // Mostra somente a tela selecionada e esconde as demais
  VIEWS.forEach(v => (document.getElementById("view-" + v).hidden = v !== nome));

  // Atualiza o endereço da página com o nome da tela
  history.replaceState(null, "", "#" + nome);

  // Fecha o menu de navegação, caso esteja aberto
  document.getElementById("nav").classList.remove("aberto");

  // Atualiza os botões da navegação
  montarNav(nome);

  // Volta a página para o início
  window.scrollTo(0, 0);

  // Relaciona cada tela com sua função responsável por carregar os dados
  const carregar = { home: carregarHome, catalogo: carregarCatalogo, estante: carregarEstante,
    emprestimos: carregarMeusEmprestimos, perfil: preencherPerfil, admin: carregarAdmin }[nome];

  // Se a tela possuir uma função de carregamento, executa essa função
  if (carregar) Promise.resolve(carregar()).catch(tratarErro);
}


// ===== Componentes visuais de livros =====

// Define as cores utilizadas nas capas dos livros
const CAPAS = [
  ["#f9c6dc", "#d4b5f0", "#3b2a52"], ["#e6d5f7", "#b79ce0", "#3b2a52"], ["#fbd3e0", "#f29cc0", "#3b2a52"],
  ["#cdb7f0", "#7d5bb5", "#ffffff"], ["#fde2ea", "#e0b3da", "#3b2a52"], ["#bda6e8", "#f3b2d0", "#3b2a52"],
  ["#f4a9c6", "#9a74cf", "#ffffff"], ["#e9dcfa", "#f9d0e2", "#3b2a52"], ["#d9c3f3", "#c78ac0", "#3b2a52"],
  ["#f7cde0", "#a98ad8", "#3b2a52"],
];

// Define os ícones que aparecem nas capas dos livros
const ICONES = ["💌", "🐉", "🚀", "🕵️", "🔎", "🦇", "🧭", "🏛️", "🎭", "🌱"];

function capaHTML(l, grande = false) {
  // Escolhe as cores e o ícone da capa com base no gênero do livro
  const i = (l.id_genero - 1) % CAPAS.length;
  const [c1, c2, txt] = CAPAS[i];

  // Verifica se o livro possui uma capa cadastrada
  // Se possuir, cria uma imagem; caso contrário, não adiciona imagem
  const img = l.id_livro ? `<img src="/capa/${l.id_livro}" alt="Capa de ${esc(l.titulo)}" onerror="this.remove()">` : "";

  // Retorna o HTML da capa com suas cores, ícone, título e autor
  return `<div class="capa ${grande ? "grande" : ""}" style="background:linear-gradient(160deg,${c1},${c2});color:${txt}">
    <span class="c-ico">${ICONES[i]}</span>
    <span class="c-titulo">${esc(l.titulo)}</span>
    <span class="c-autor">${esc(l.autor)}</span>${img}</div>`;
}

function notaTxt(l) {
  // Mostra a nota média do livro com uma casa decimal
  // Se não houver avaliação, mostra "Sem notas"
  return l.nota_media ? `★ ${Number(l.nota_media).toFixed(1)}` : "Sem notas";
}

function cardLivro(l) {
  // Se existir um usuário conectado, cria o botão de favoritar
  // Também verifica se o livro já está nos favoritos
  const coracao = usuario
    ? `<button class="coracao ${idsFav.has(l.id_livro) ? "on" : ""}" data-id="${l.id_livro}" title="Favoritar"
         onclick="event.stopPropagation();alternarFavorito(${l.id_livro})">♥</button>` : "";

  // Cria o cartão do livro com capa, título, autor, gênero, nota e disponibilidade
  return `<div class="card" onclick="abrirDetalhes(${l.id_livro})">
    ${coracao}${capaHTML(l)}
    <h3>${esc(l.titulo)}</h3>
    <div class="autor">${esc(l.autor)}</div>
    <span class="tag">${esc(l.genero)}</span>
    <div class="linha"><span class="nota">${notaTxt(l)}</span>
      <span class="${l.disponivel ? "ok" : "nao"}">${l.disponivel ? l.quantidade_disponivel + " disp." : "Indisponível"}</span></div>
  </div>`;
}

function renderStats(el, s) {
  // Insere na página os indicadores gerais da biblioteca
  el.innerHTML = `
    <div class="stat"><b data-n="${s.livros}">0</b><span>livros no acervo</span></div>
    <div class="stat"><b data-n="${s.usuarios}">0</b><span>leitores</span></div>
    <div class="stat"><b data-n="${s.emprestimos_total}">0</b><span>empréstimos realizados</span></div>
    <div class="stat"><b data-n="${s.emprestimos_ativos}">0</b><span>empréstimos ativos</span></div>`;

  // Seleciona os números que serão animados
  el.querySelectorAll("b[data-n]").forEach(b => {
    // Define o valor final e inicia a contagem em zero
    const alvo = +b.dataset.n; let n = 0;

    // Calcula de quanto em quanto o número vai aumentar
    const passo = Math.max(1, Math.ceil(alvo / 25));

    // Atualiza o número a cada 25 milissegundos até atingir o valor final
    const t = setInterval(() => { n = Math.min(alvo, n + passo); b.textContent = n; if (n >= alvo) clearInterval(t); }, 25);
  });
}


// ===== Estado do usuário (favoritos e lista de leitura) =====

async function recarregarEstado() {
  // Se não houver usuário conectado, limpa os favoritos e a lista de leitura
  if (!usuario) { idsFav = new Set(); listaMap = {}; return; }

  // Busca na API os dados da estante do usuário
  const d = await api("/api/estante");

  // Atualiza os IDs dos livros favoritados
  idsFav = new Set(d.ids_favoritos);

  // Atualiza a situação dos livros na lista de leitura
  listaMap = d.lista;
}

async function alternarFavorito(id) {
  try {
    // Envia uma requisição para adicionar ou remover o livro dos favoritos
    const d = await api("/api/favoritos/" + id, "POST");

    // Atualiza a lista de favoritos de acordo com a resposta da API
    d.favoritado ? idsFav.add(id) : idsFav.delete(id);

    // Mostra uma mensagem informando o resultado da ação
    toast(d.mensagem);

    // Atualiza a aparência dos botões de favorito na página
    document.querySelectorAll(`.coracao[data-id="${id}"]`).forEach(b => b.classList.toggle("on", d.favoritado));

    // Se a tela da estante estiver aberta, atualiza seu conteúdo
    if (!document.getElementById("view-estante").hidden) carregarEstante();

    // Se o modal estiver aberto, atualiza os detalhes do livro
    if (!document.getElementById("modal").hidden) abrirDetalhes(id);

  } catch (e) {
    // Exibe uma mensagem caso aconteça algum erro
    tratarErro(e);
  }
}


// ===== Eventos =====

function ligarEventos() {
  // Atalho para encontrar elementos HTML pelo ID
  const $ = id => document.getElementById(id);

  // Variável usada para controlar o tempo da busca
  let t;

  // Executa a busca no catálogo enquanto o usuário digita
  // Aguarda 250 milissegundos após a última tecla antes de carregar os resultados
  $("busca").addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => carregarCatalogo().catch(tratarErro), 250); });

  // Atualiza o catálogo quando algum filtro é alterado
  ["filtro-genero", "filtro-ordem", "filtro-disp", "filtro-nota"].forEach(id =>
    $(id).addEventListener("change", () => carregarCatalogo().catch(tratarErro)));

  // Liga os botões às funções de login, cadastro e edição de perfil
  $("btn-login").addEventListener("click", entrar);
  $("btn-cadastro").addEventListener("click", cadastrar);
  $("btn-perfil").addEventListener("click", salvarPerfil);

  // Liga os botões às funções de gerenciamento de livros
  $("btn-salvar-livro").addEventListener("click", salvarLivro);
  $("btn-cancelar").addEventListener("click", limparFormLivro);
  $("btn-autor").addEventListener("click", novoAutor);
  $("btn-genero").addEventListener("click", novoGenero);

  // Abre ou fecha o menu de navegação em telas menores
  $("menu-btn").addEventListener("click", () => $("nav").classList.toggle("aberto"));

  // Fecha o modal quando o usuário clica fora do conteúdo
  $("modal").addEventListener("click", e => { if (e.target.id === "modal") fecharModal(); });

  // Fecha o modal quando a tecla ESC é pressionada
  document.addEventListener("keydown", e => { if (e.key === "Escape") fecharModal(); });

  // Permite fazer login pressionando Enter no campo de senha
  $("login-senha").addEventListener("keydown", e => { if (e.key === "Enter") entrar(); });

  // Controla a troca das abas da estante
  $("abas-estante").addEventListener("click", e => {
    // Verifica se o elemento clicado possui uma aba identificada
    if (!e.target.dataset.aba) return;

    // Atualiza a aba selecionada
    abaEstante = e.target.dataset.aba;

    // Atualiza visualmente qual aba está ativa
    document.querySelectorAll("#abas-estante .aba").forEach(b => b.classList.toggle("ativa", b === e.target));

    // Atualiza os livros exibidos na estante
    renderEstante();
  });

  // Controla a troca das abas da administração
  $("abas-admin").addEventListener("click", e => {
    // Verifica se o elemento clicado possui uma aba identificada
    if (!e.target.dataset.aba) return;

    // Atualiza visualmente a aba selecionada
    document.querySelectorAll("#abas-admin .aba").forEach(b => b.classList.toggle("ativa", b === e.target));

    // Mostra somente o conteúdo da aba administrativa selecionada
    document.querySelectorAll(".admin-aba").forEach(d => (d.hidden = d.id !== "admin-" + e.target.dataset.aba));
  });
}