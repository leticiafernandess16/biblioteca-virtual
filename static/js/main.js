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

  } catch (e) {
    tratarErro(e);
  }
}

// ===== Capa do livro: static/IMG/<id_livro>.png (emoji se a imagem não existir) =====
function htmlCapa(livro, classe = "") {
  const id = livro && livro.id_livro ? livro.id_livro : "";
  const titulo = String(livro && livro.titulo ? livro.titulo : "Livro")
    .replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const img = id
    ? `<img class="capa-img" src="/static/IMG/${id}.png" alt="Capa de ${titulo}" loading="lazy" onerror="this.remove()">`
    : "";
  return `<div class="capa-box ${classe}">${img}<span class="capa-emoji">📖</span></div>`;
}