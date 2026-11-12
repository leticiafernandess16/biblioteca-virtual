// ===== Página inicial, catálogo e detalhes =====

// Armazena a curiosidade literária que está sendo exibida no momento.
let curiosidadeAtual = null;

// Preenche o filtro de gêneros do catálogo com as opções disponíveis.
function preencherFiltroGeneros() {
  // Adiciona a opção para exibir livros de todos os gêneros e, em seguida, as opções recebidas do sistema.
  document.getElementById("filtro-genero").innerHTML = `<option value="">Todos os gêneros</option>` +
    generos.map(g => `<option value="${g.id_genero}">${esc(g.nome)}</option>`).join("");
  // O método map percorre os gêneros e cria uma opção para cada um.
}

// Cria uma lista horizontal de livros dentro do elemento HTML informado.
function trilho(id, livros) {
  // Verifica se existem livros para exibir.
  // Se houver, cria os cartões de cada livro; caso contrário, apresenta uma mensagem.
  document.getElementById(id).innerHTML = livros.length ? livros.map(cardLivro).join("") : "<p class='vazio'>Nada por aqui ainda.</p>";
}

// Função assíncrona responsável por carregar as informações da página inicial.
async function carregarHome() {
  // Busca na API os dados necessários para montar a página inicial.
  const h = await api("/api/home");

  // Atualiza a lista de gêneros e preenche o filtro do catálogo.
  generos = h.generos; preencherFiltroGeneros();

  // Exibe as estatísticas gerais da biblioteca.
  renderStats(document.getElementById("stats"), h.estatisticas);

  // Armazena as informações do livro selecionado como livro do dia.
  const d = h.livro_do_dia;

  // Exibe a capa, o título, o autor, o gênero e a avaliação do livro do dia.
  // Se não houver um livro disponível, deixa o espaço vazio.
  document.getElementById("livro-dia").innerHTML = d ? `${capaHTML(d)}
    <div><small>📅 Livro do dia</small><h3>${esc(d.titulo)}</h3>
    <p class="autor">${esc(d.autor)}</p><span class="tag">${esc(d.genero)}</span>
    <p><span class="nota">${notaTxt(d)}</span></p></div>` : "";

  // Define o clique no bloco do livro do dia para abrir seus detalhes.
  document.getElementById("livro-dia").onclick = d ? () => abrirDetalhes(d.id_livro) : null;

  // Cria botões para cada gênero, mostrando também a quantidade de livros disponíveis.
  // Ao clicar em uma categoria, o catálogo é aberto com aquele gênero selecionado.
  document.getElementById("categorias").innerHTML = h.generos.map(g =>
    `<button class="chip" onclick="irParaCatalogo('', ${g.id_genero})">${esc(g.nome)}<span>${g.total_livros}</span></button>`).join("");

  // Exibe os livros em destaque na página inicial.
  trilho("destaques", h.destaques);

  // Exibe os livros mais populares.
  trilho("populares", h.populares);

  // Exibe os lançamentos cadastrados na biblioteca.
  trilho("lancamentos", h.lancamentos);

  // Exibe uma curiosidade literária na página inicial.
  mostrarCuriosidade(h.curiosidade);

  // Obtém o bloco HTML destinado às recomendações personalizadas.
  const bloco = document.getElementById("bloco-recomendacoes");

  // Mostra o bloco de recomendações somente quando existe um usuário autenticado.
  bloco.hidden = !usuario;

  // Se houver um usuário conectado, busca e exibe os livros recomendados para ele.
  if (usuario) trilho("recomendacoes", await api("/api/recomendacoes"));
}

// Exibe uma curiosidade literária na página inicial.
function mostrarCuriosidade(c) {
  // Guarda a curiosidade atual para permitir que ela seja substituída posteriormente.
  curiosidadeAtual = c;

  // Monta o conteúdo da curiosidade com título, texto e botão para carregar outra.
  // Se não houver curiosidade, o espaço fica vazio.
  document.getElementById("curiosidade").innerHTML = c ? `
    <div><span class="selo">💡 Curiosidade literária</span><h3>${esc(c.titulo)}</h3><p>${esc(c.texto)}</p></div>
    <button class="rosa" onclick="outraCuriosidade()">Outra curiosidade</button>` : "";
}

// Busca e exibe outra curiosidade literária.
async function outraCuriosidade() {
  try {
    // Consulta a API solicitando uma curiosidade diferente da que está sendo exibida.
    // O ID da curiosidade atual é enviado para evitar sua repetição.
    mostrarCuriosidade(await api("/api/curiosidade?excluir=" + (curiosidadeAtual?.id_curiosidade || "")));
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante a consulta.
}

// Prepara os filtros do catálogo e direciona o usuário para essa página.
function irParaCatalogo(busca = "", genero = "", ordem = "titulo") {
  // Preenche o campo de pesquisa com o texto recebido.
  document.getElementById("busca").value = busca;

  // Seleciona o gênero informado no filtro.
  document.getElementById("filtro-genero").value = genero;

  // Define a ordenação dos livros.
  document.getElementById("filtro-ordem").value = ordem;

  // Desmarca o filtro que exibe somente livros disponíveis.
  document.getElementById("filtro-disp").checked = false;

  // Desmarca o filtro de avaliação mínima.
  document.getElementById("filtro-nota").checked = false;

  // Abre a tela do catálogo.
  mostrarView("catalogo");
}

// Função assíncrona que carrega os livros de acordo com os filtros selecionados.
async function carregarCatalogo() {
  // Cria um objeto para organizar os parâmetros que serão enviados à API.
  const p = new URLSearchParams();

  // Cria uma função auxiliar para acessar elementos HTML pelo ID.
  const v = id => document.getElementById(id);

  // Adiciona o termo de pesquisa aos parâmetros, caso o campo não esteja vazio.
  if (v("busca").value.trim()) p.set("busca", v("busca").value.trim());

  // Adiciona o gênero selecionado aos parâmetros, caso exista um filtro escolhido.
  if (v("filtro-genero").value) p.set("genero", v("filtro-genero").value);

  // Define a ordem utilizada para organizar os livros.
  p.set("ordem", v("filtro-ordem").value);

  // Se o filtro estiver marcado, solicita somente livros disponíveis.
  if (v("filtro-disp").checked) p.set("disponiveis", "1");

  // Se o filtro estiver marcado, solicita livros com nota mínima 4.
  if (v("filtro-nota").checked) p.set("nota_min", "4");

  // Busca na API os livros que correspondem aos parâmetros selecionados.
  const livros = await api("/api/livros?" + p);

  // Atualiza o texto que informa a quantidade de livros encontrados.
  // Ajusta a palavra entre singular e plural conforme o resultado.
  v("contagem").textContent = livros.length + (livros.length === 1 ? " livro encontrado" : " livros encontrados");

  // Exibe os cartões dos livros encontrados.
  // Caso a pesquisa não retorne resultados, apresenta uma mensagem informativa.
  v("lista-livros").innerHTML = livros.length ? livros.map(cardLivro).join("")
    : "<p class='vazio'>Nenhum livro encontrado. Tente outros filtros. 🌸</p>";
}

// ===== Detalhes (modal) =====

// Fecha a janela modal que apresenta os detalhes de um livro.
function fecharModal() { document.getElementById("modal").hidden = true; }

// Função assíncrona que busca e exibe os detalhes de um livro selecionado.
async function abrirDetalhes(id) {
  try {
    // Consulta a API para obter as informações do livro pelo seu ID.
    const d = await api("/api/livros/" + id);

    // Armazena os dados principais do livro retornado.
    const l = d.livro;

    // Verifica se o livro está marcado como favorito pelo usuário.
    const fav = idsFav.has(id), status = listaMap[id];

    // Percorre as avaliações recebidas e monta o conteúdo de cada avaliação.
    // Exibe o nome do usuário, as estrelas, a data e o comentário.
    const avs = d.avaliacoes.map(a =>
      `<div class="aval"><b>${esc(a.usuario)}</b> · ${"★".repeat(a.nota)}${"☆".repeat(5 - a.nota)}
       <small>${a.data_avaliacao}</small><br>${esc(a.comentario)}</div>`).join("");

    // Define os botões e campos disponíveis conforme o usuário esteja autenticado ou não.
    const acoes = usuario ? `
      <div class="acoes">
        <button onclick="pedirEmprestimo(${id})" ${l.disponivel ? "" : "disabled"}>Solicitar empréstimo</button>
        <button class="${fav ? "rosa" : "sec"}" onclick="alternarFavorito(${id})">${fav ? "♥ Favoritado" : "♡ Favoritar"}</button>
        ${status === "lido"
          ? `<button class="sec" onclick="definirLista(${id}, 'quero_ler')">Lido (desfazer)</button>`
          : `<button class="sec" onclick="definirLista(${id}, 'quero_ler')" ${status ? "disabled" : ""}>${status ? "Na lista" : " Quero ler"}</button>
             <button class="sec" onclick="definirLista(${id}, 'lido')">✔ Marcar como lido</button>`}
        ${status ? `<button class="sec" onclick="tirarDaLista(${id})">Remover da lista</button>` : ""}
      </div>
      <h4>Sua avaliação</h4>
      <select id="av-nota" style="max-width:140px">${[5, 4, 3, 2, 1].map(n => `<option value="${n}">${"★".repeat(n)}</option>`).join("")}</select>
      <input id="av-coment" placeholder="Escreva um comentário (opcional)" maxlength="500">
      <button class="sec" style="margin-top:8px" onclick="enviarAvaliacao(${id})">Enviar avaliação</button>`
      : `<p class="dica">Entre na sua conta para pedir emprestado, favoritar e avaliar.</p>
         <button onclick="fecharModal();mostrarView('auth')">Entrar</button>`;

    // Monta o conteúdo completo da janela modal com as informações do livro e suas avaliações.
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

    // Torna a janela modal visível após preencher seu conteúdo.
    document.getElementById("modal").hidden = false;
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao buscar ou exibir os detalhes.
}

// Define ou atualiza a situação de leitura de um livro na estante do usuário.
async function definirLista(id, status) {
  try {
    // Envia o ID do livro e o status desejado para a API.
    const d = await api("/api/lista/" + id, "POST", { status });

    // Atualiza o status local, exibe a mensagem e recarrega os detalhes do livro.
    listaMap[id] = status; toast(d.mensagem); abrirDetalhes(id);

    // Se a estante estiver aberta, atualiza sua lista de livros.
    if (!document.getElementById("view-estante").hidden) carregarEstante();
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao atualizar a lista.
}

// Remove um livro da lista pessoal de leitura do usuário.
async function tirarDaLista(id) {
  try {
    // Envia uma requisição DELETE para remover o livro da lista.
    const d = await api("/api/lista/" + id, "DELETE");

    // Remove o status do livro do mapa local, exibe a mensagem e atualiza os detalhes.
    delete listaMap[id]; toast(d.mensagem); abrirDetalhes(id);

    // Se a estante estiver aberta, atualiza seu conteúdo.
    if (!document.getElementById("view-estante").hidden) carregarEstante();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante a remoção.
}

// Envia uma avaliação do usuário para um livro.
async function enviarAvaliacao(id) {
  try {
    // Envia a nota selecionada e o comentário preenchido para a API.
    const d = await api(`/api/livros/${id}/avaliacoes`, "POST", {
      nota: document.getElementById("av-nota").value,
      comentario: document.getElementById("av-coment").value });

    // Exibe a mensagem retornada após o envio da avaliação.
    toast(d.mensagem);

    // Atualiza a janela de detalhes para mostrar a avaliação registrada.
    abrirDetalhes(id);
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao enviar a avaliação.
}