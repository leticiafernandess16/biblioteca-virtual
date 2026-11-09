// ===== Estado global e utilidades =====
let usuario = null;
let generos = [];
let autores = [];
let idsFav = new Set();   // ids dos livros favoritados pelo usuário
let listaMap = {};        // id_livro -> 'quero_ler' | 'lido'

const VIEWS = ["home", "catalogo", "auth", "estante", "emprestimos", "perfil", "admin", "sobre"];

function esc(t) {
  return String(t ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

async function api(url, metodo = "GET", corpo = null) {
  const opcoes = { method: metodo, headers: {} };
  if (corpo) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }
  const resp = await fetch(url, opcoes);
  const dados = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(dados.erro || "Erro inesperado.");
  return dados;
}

function toast(texto, erro = false) {
  const el = document.getElementById("toast");
  el.textContent = texto;
  el.className = "toast" + (erro ? " erro" : "");
  el.hidden = false;
  clearTimeout(toast.t);
  toast.t = setTimeout(() => (el.hidden = true), 3500);
}
function tratarErro(e) { toast(e.message || "Erro inesperado.", true); }

// ===== Navegação entre telas =====
function montarNav(ativa) {
  const item = (v, rotulo, cls = "") =>
    `<button class="${cls} ${ativa === v ? "ativo" : ""}" onclick="mostrarView('${v}')">${rotulo}</button>`;
  let html = item("home", "Início") + item("catalogo", "Catálogo");
  if (usuario) {
    html += item("estante", "Minha estante") + item("emprestimos", "Empréstimos");
    if (usuario.tipo === "admin") html += item("admin", "Administração");
    html += item("perfil", "Perfil");
  }
  html += item("sobre", "Sobre");
  html += usuario
    ? `<button class="destaque" onclick="sair()">Sair (${esc(usuario.nome.split(" ")[0])})</button>`
    : item("auth", "Entrar / Cadastrar", "destaque");
  document.getElementById("nav").innerHTML = html;
}

function mostrarView(nome) {
  if (["estante", "emprestimos", "perfil"].includes(nome) && !usuario) {
    toast("Faça login para acessar esta área.", true);
    nome = "auth";
  }
  if (nome === "admin" && (!usuario || usuario.tipo !== "admin")) nome = usuario ? "home" : "auth";
  VIEWS.forEach(v => (document.getElementById("view-" + v).hidden = v !== nome));
  history.replaceState(null, "", "#" + nome);
  document.getElementById("nav").classList.remove("aberto");
  montarNav(nome);
  window.scrollTo(0, 0);
  const carregar = { home: carregarHome, catalogo: carregarCatalogo, estante: carregarEstante,
    emprestimos: carregarMeusEmprestimos, perfil: preencherPerfil, admin: carregarAdmin }[nome];
  if (carregar) Promise.resolve(carregar()).catch(tratarErro);
}

// ===== Componentes visuais de livros =====
const CAPAS = [
  ["#f9c6dc", "#d4b5f0", "#3b2a52"], ["#e6d5f7", "#b79ce0", "#3b2a52"], ["#fbd3e0", "#f29cc0", "#3b2a52"],
  ["#cdb7f0", "#7d5bb5", "#ffffff"], ["#fde2ea", "#e0b3da", "#3b2a52"], ["#bda6e8", "#f3b2d0", "#3b2a52"],
  ["#f4a9c6", "#9a74cf", "#ffffff"], ["#e9dcfa", "#f9d0e2", "#3b2a52"], ["#d9c3f3", "#c78ac0", "#3b2a52"],
  ["#f7cde0", "#a98ad8", "#3b2a52"],
];
const ICONES = ["💌", "🐉", "🚀", "🕵️", "🔎", "🦇", "🧭", "🏛️", "🎭", "🌱"];

function capaHTML(l, grande = false) {
  const i = (l.id_genero - 1) % CAPAS.length;
  const [c1, c2, txt] = CAPAS[i];
  const img = l.capa_url ? `<img src="${esc(l.capa_url)}" alt="Capa de ${esc(l.titulo)}" onerror="this.remove()">` : "";
  return `<div class="capa ${grande ? "grande" : ""}" style="background:linear-gradient(160deg,${c1},${c2});color:${txt}">
    <span class="c-ico">${ICONES[i]}</span>
    <span class="c-titulo">${esc(l.titulo)}</span>
    <span class="c-autor">${esc(l.autor)}</span>${img}</div>`;
}

function notaTxt(l) {
  return l.nota_media ? `★ ${Number(l.nota_media).toFixed(1)}` : "Sem notas";
}

function cardLivro(l) {
  const coracao = usuario
    ? `<button class="coracao ${idsFav.has(l.id_livro) ? "on" : ""}" data-id="${l.id_livro}" title="Favoritar"
         onclick="event.stopPropagation();alternarFavorito(${l.id_livro})">♥</button>` : "";
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
  el.innerHTML = `
    <div class="stat"><b data-n="${s.livros}">0</b><span>livros no acervo</span></div>
    <div class="stat"><b data-n="${s.usuarios}">0</b><span>leitores</span></div>
    <div class="stat"><b data-n="${s.emprestimos_total}">0</b><span>empréstimos realizados</span></div>
    <div class="stat"><b data-n="${s.emprestimos_ativos}">0</b><span>empréstimos ativos</span></div>`;
  el.querySelectorAll("b[data-n]").forEach(b => {
    const alvo = +b.dataset.n; let n = 0;
    const passo = Math.max(1, Math.ceil(alvo / 25));
    const t = setInterval(() => { n = Math.min(alvo, n + passo); b.textContent = n; if (n >= alvo) clearInterval(t); }, 25);
  });
}

// ===== Estado do usuário (favoritos e lista de leitura) =====
async function recarregarEstado() {
  if (!usuario) { idsFav = new Set(); listaMap = {}; return; }
  const d = await api("/api/estante");
  idsFav = new Set(d.ids_favoritos);
  listaMap = d.lista;
}

async function alternarFavorito(id) {
  try {
    const d = await api("/api/favoritos/" + id, "POST");
    d.favoritado ? idsFav.add(id) : idsFav.delete(id);
    toast(d.mensagem);
    document.querySelectorAll(`.coracao[data-id="${id}"]`).forEach(b => b.classList.toggle("on", d.favoritado));
    if (!document.getElementById("view-estante").hidden) carregarEstante();
    if (!document.getElementById("modal").hidden) abrirDetalhes(id);
  } catch (e) { tratarErro(e); }
}

// ===== Eventos =====
function ligarEventos() {
  const $ = id => document.getElementById(id);
  let t;
  $("busca").addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => carregarCatalogo().catch(tratarErro), 250); });
  ["filtro-genero", "filtro-ordem", "filtro-disp", "filtro-nota"].forEach(id =>
    $(id).addEventListener("change", () => carregarCatalogo().catch(tratarErro)));
  $("btn-login").addEventListener("click", entrar);
  $("btn-cadastro").addEventListener("click", cadastrar);
  $("btn-perfil").addEventListener("click", salvarPerfil);
  $("btn-salvar-livro").addEventListener("click", salvarLivro);
  $("btn-cancelar").addEventListener("click", limparFormLivro);
  $("btn-autor").addEventListener("click", novoAutor);
  $("btn-genero").addEventListener("click", novoGenero);
  $("menu-btn").addEventListener("click", () => $("nav").classList.toggle("aberto"));
  $("modal").addEventListener("click", e => { if (e.target.id === "modal") fecharModal(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") fecharModal(); });
  $("login-senha").addEventListener("keydown", e => { if (e.key === "Enter") entrar(); });
  $("abas-estante").addEventListener("click", e => {
    if (!e.target.dataset.aba) return;
    abaEstante = e.target.dataset.aba;
    document.querySelectorAll("#abas-estante .aba").forEach(b => b.classList.toggle("ativa", b === e.target));
    renderEstante();
  });
  $("abas-admin").addEventListener("click", e => {
    if (!e.target.dataset.aba) return;
    document.querySelectorAll("#abas-admin .aba").forEach(b => b.classList.toggle("ativa", b === e.target));
    document.querySelectorAll(".admin-aba").forEach(d => (d.hidden = d.id !== "admin-" + e.target.dataset.aba));
  });
}

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
