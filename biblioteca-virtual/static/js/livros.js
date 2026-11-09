// ===== Página inicial, catálogo e detalhes =====
let curiosidadeAtual = null;

function preencherFiltroGeneros() {
  document.getElementById("filtro-genero").innerHTML = `<option value="">Todos os gêneros</option>` +
    generos.map(g => `<option value="${g.id_genero}">${esc(g.nome)}</option>`).join("");
}

function trilho(id, livros) {
  document.getElementById(id).innerHTML = livros.length ? livros.map(cardLivro).join("") : "<p class='vazio'>Nada por aqui ainda.</p>";
}

async function carregarHome() {
  const h = await api("/api/home");
  generos = h.generos; preencherFiltroGeneros();
  renderStats(document.getElementById("stats"), h.estatisticas);

  const d = h.livro_do_dia;
  document.getElementById("livro-dia").innerHTML = d ? `${capaHTML(d)}
    <div><small>📅 Livro do dia</small><h3>${esc(d.titulo)}</h3>
    <p class="autor">${esc(d.autor)}</p><span class="tag">${esc(d.genero)}</span>
    <p><span class="nota">${notaTxt(d)}</span></p></div>` : "";
  document.getElementById("livro-dia").onclick = d ? () => abrirDetalhes(d.id_livro) : null;

  document.getElementById("categorias").innerHTML = h.generos.map(g =>
    `<button class="chip" onclick="irParaCatalogo('', ${g.id_genero})">${esc(g.nome)}<span>${g.total_livros}</span></button>`).join("");
  trilho("destaques", h.destaques);
  trilho("populares", h.populares);
  trilho("lancamentos", h.lancamentos);
  mostrarCuriosidade(h.curiosidade);

  const bloco = document.getElementById("bloco-recomendacoes");
  bloco.hidden = !usuario;
  if (usuario) trilho("recomendacoes", await api("/api/recomendacoes"));
}

function mostrarCuriosidade(c) {
  curiosidadeAtual = c;
  document.getElementById("curiosidade").innerHTML = c ? `
    <div><span class="selo">💡 Curiosidade literária</span><h3>${esc(c.titulo)}</h3><p>${esc(c.texto)}</p></div>
    <button class="rosa" onclick="outraCuriosidade()">Outra curiosidade</button>` : "";
}

async function outraCuriosidade() {
  try { mostrarCuriosidade(await api("/api/curiosidade?excluir=" + (curiosidadeAtual?.id_curiosidade || ""))); }
  catch (e) { tratarErro(e); }
}

function irParaCatalogo(busca = "", genero = "", ordem = "titulo") {
  document.getElementById("busca").value = busca;
  document.getElementById("filtro-genero").value = genero;
  document.getElementById("filtro-ordem").value = ordem;
  document.getElementById("filtro-disp").checked = false;
  document.getElementById("filtro-nota").checked = false;
  mostrarView("catalogo");
}

async function carregarCatalogo() {
  const p = new URLSearchParams();
  const v = id => document.getElementById(id);
  if (v("busca").value.trim()) p.set("busca", v("busca").value.trim());
  if (v("filtro-genero").value) p.set("genero", v("filtro-genero").value);
  p.set("ordem", v("filtro-ordem").value);
  if (v("filtro-disp").checked) p.set("disponiveis", "1");
  if (v("filtro-nota").checked) p.set("nota_min", "4");
  const livros = await api("/api/livros?" + p);
  v("contagem").textContent = livros.length + (livros.length === 1 ? " livro encontrado" : " livros encontrados");
  v("lista-livros").innerHTML = livros.length ? livros.map(cardLivro).join("")
    : "<p class='vazio'>Nenhum livro encontrado. Tente outros filtros. 🌸</p>";
}

// ===== Detalhes (modal) =====
function fecharModal() { document.getElementById("modal").hidden = true; }

async function abrirDetalhes(id) {
  try {
    const d = await api("/api/livros/" + id);
    const l = d.livro;
    const fav = idsFav.has(id), status = listaMap[id];
    const avs = d.avaliacoes.map(a =>
      `<div class="aval"><b>${esc(a.usuario)}</b> · ${"★".repeat(a.nota)}${"☆".repeat(5 - a.nota)}
       <small>${a.data_avaliacao}</small><br>${esc(a.comentario)}</div>`).join("");
    const acoes = usuario ? `
      <div class="acoes">
        <button onclick="pedirEmprestimo(${id})" ${l.disponivel ? "" : "disabled"}>📖 Solicitar empréstimo</button>
        <button class="${fav ? "rosa" : "sec"}" onclick="alternarFavorito(${id})">${fav ? "♥ Favoritado" : "♡ Favoritar"}</button>
        ${status === "lido"
          ? `<button class="sec" onclick="definirLista(${id}, 'quero_ler')">✅ Lido (desfazer)</button>`
          : `<button class="sec" onclick="definirLista(${id}, 'quero_ler')" ${status ? "disabled" : ""}>${status ? "📌 Na lista" : "📌 Quero ler"}</button>
             <button class="sec" onclick="definirLista(${id}, 'lido')">✔ Marcar como lido</button>`}
        ${status ? `<button class="sec" onclick="tirarDaLista(${id})">Remover da lista</button>` : ""}
      </div>
      <h4>Sua avaliação</h4>
      <select id="av-nota" style="max-width:140px">${[5, 4, 3, 2, 1].map(n => `<option value="${n}">${"★".repeat(n)}</option>`).join("")}</select>
      <input id="av-coment" placeholder="Escreva um comentário (opcional)" maxlength="500">
      <button class="sec" style="margin-top:8px" onclick="enviarAvaliacao(${id})">Enviar avaliação</button>`
      : `<p class="dica">Entre na sua conta para pedir emprestado, favoritar e avaliar.</p>
         <button onclick="fecharModal();mostrarView('auth')">Entrar</button>`;
    document.getElementById("modal-corpo").innerHTML = `
      <button class="fechar" onclick="fecharModal()" aria-label="Fechar">✕</button>
      <div class="det"><div>${capaHTML(l, true)}</div><div>
        <h2>${esc(l.titulo)}</h2>
        <p>por <b>${esc(l.autor)}</b> · <span class="tag">${esc(l.genero)}</span></p>
        <p><span class="nota">${notaTxt(l)}</span> <small>(${l.total_avaliacoes} avaliações)</small></p>
        <p>${esc(l.sinopse) || "Sem sinopse."}</p>
        <div class="meta-info">
          <div><small>Editora</small>${esc(l.editora) || "—"}</div>
          <div><small>Ano</small>${l.ano_publicacao ?? "—"}</div>
          <div><small>Classificação</small>${esc(l.classificacao_indicativa) || "—"}</div>
          <div><small>Disponibilidade</small><span class="${l.disponivel ? "ok" : "nao"}">${l.quantidade_disponivel} de ${l.quantidade_total}</span></div>
        </div>${acoes}</div></div>
      <h4 style="margin-top:18px">Avaliações dos leitores</h4>${avs || "<p class='dica'>Ainda não há avaliações.</p>"}`;
    document.getElementById("modal").hidden = false;
  } catch (e) { tratarErro(e); }
}

async function definirLista(id, status) {
  try {
    const d = await api("/api/lista/" + id, "POST", { status });
    listaMap[id] = status; toast(d.mensagem); abrirDetalhes(id);
    if (!document.getElementById("view-estante").hidden) carregarEstante();
  } catch (e) { tratarErro(e); }
}

async function tirarDaLista(id) {
  try {
    const d = await api("/api/lista/" + id, "DELETE");
    delete listaMap[id]; toast(d.mensagem); abrirDetalhes(id);
    if (!document.getElementById("view-estante").hidden) carregarEstante();
  } catch (e) { tratarErro(e); }
}

async function enviarAvaliacao(id) {
  try {
    const d = await api(`/api/livros/${id}/avaliacoes`, "POST", {
      nota: document.getElementById("av-nota").value,
      comentario: document.getElementById("av-coment").value });
    toast(d.mensagem);
    abrirDetalhes(id);
  } catch (e) { tratarErro(e); }
}
