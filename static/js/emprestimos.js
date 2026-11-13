// ===== Empréstimos do usuário e área administrativa =====

// Função assíncrona que solicita um empréstimo de livro pelo seu ID.
async function pedirEmprestimo(idLivro) {
  try {
    // Envia uma requisição POST para registrar o empréstimo do livro.
    const d = await api("/api/emprestimos/" + idLivro, "POST");

    // Exibe uma mensagem de confirmação retornada pela API.
    toast(d.mensagem);

    // Fecha a janela modal aberta na tela.
    fecharModal();

    // Atualiza as telas que estiverem abertas para mostrar os dados recentes.
    atualizarTelasAbertas();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante a solicitação.
}

// Verifica quais telas estão abertas e atualiza seus conteúdos.
function atualizarTelasAbertas() {
  // Se a página inicial estiver visível, atualiza suas informações.
  if (!document.getElementById("view-home").hidden) carregarHome().catch(tratarErro);

  // Se o catálogo estiver visível, atualiza a lista de livros.
  if (!document.getElementById("view-catalogo").hidden) carregarCatalogo().catch(tratarErro);

  // Se a tela de empréstimos estiver visível, atualiza os empréstimos do usuário.
  if (!document.getElementById("view-emprestimos").hidden) carregarMeusEmprestimos().catch(tratarErro);

  // Se a área administrativa estiver visível, atualiza seus dados.
  if (!document.getElementById("view-admin").hidden) carregarAdmin().catch(tratarErro);
}

// Cria uma função que gera um elemento HTML para exibir o status de um empréstimo.
// A classe CSS recebe o status e o texto exibido corresponde ao próprio status.
const rotuloStatus = s => `<span class="badge ${s}">${s}</span>`;

// Função assíncrona que busca e exibe os empréstimos realizados pelo usuário.
async function carregarMeusEmprestimos() {
  // Busca na API a lista de empréstimos do usuário autenticado.
  const lista = await api("/api/emprestimos/meus");

  // Conta quantos empréstimos existem para cada status informado.
  const conta = s => lista.filter(e => e.status === s).length;

  // Exibe um resumo com a quantidade de empréstimos por situação.
  document.getElementById("resumo-emp").innerHTML = `
    <div class="stat"><b>${conta("ativo")}</b><span>em andamento</span></div>
    <div class="stat"><b>${conta("atrasado")}</b><span>atrasados</span></div>
    <div class="stat"><b>${conta("devolvido")}</b><span>devolvidos</span></div>`;

  // Percorre a lista de empréstimos e cria uma linha da tabela para cada registro.
  document.getElementById("tab-meus").innerHTML = lista.map(e => `
    <tr><td><a href="#" onclick="event.preventDefault();abrirDetalhes(${e.id_livro})">${esc(e.titulo)}</a></td>
    <td>${e.data_emprestimo}</td><td>${e.data_prevista_devolucao}</td><td>${e.data_devolucao || "—"}</td>
    <td>${rotuloStatus(e.status)}</td>
    <td>${e.status !== "devolvido" ? `<button onclick="devolver(${e.id_emprestimo})">Devolver</button>` : ""}</td></tr>`
  ).join("") || `<tr><td colspan="6">Você ainda não fez nenhum empréstimo. 🌸</td></tr>`;
  // Se não houver empréstimos, exibe uma mensagem informando que a lista está vazia.
}

// Função assíncrona responsável por registrar a devolução de um empréstimo.
async function devolver(id) {
  try {
    // Envia uma requisição POST para registrar a devolução do empréstimo informado.
    const d = await api(`/api/emprestimos/${id}/devolver`, "POST");

    // Exibe a mensagem retornada pela API.
    toast(d.mensagem);

    // Atualiza as telas abertas para refletir a devolução.
    atualizarTelasAbertas();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante a devolução.
}

// ---------- Administração ----------

// Função que cria barras visuais para representar os dados recebidos.
function barras(el, itens) {
  // Identifica o maior valor da lista para calcular proporcionalmente o tamanho das barras.
  // Math.max utiliza 1 como valor mínimo para evitar divisão por zero.
  const max = Math.max(1, ...itens.map(i => i.total));

  // Percorre os itens e monta uma barra proporcional ao total de cada um.
  el.innerHTML = itens.map(i => `<div class="barra"><span>${esc(i.titulo)}</span>
    <div class="trilha"><div style="width:${i.total * 100 / max}%"></div></div><b>${i.total}</b></div>`).join("");
}

// Função assíncrona que carrega os dados necessários para a área administrativa.
async function carregarAdmin() {
  // Realiza várias requisições simultaneamente para obter os dados do painel.
  const [painel, livros, todos, users, aut, gen] = await Promise.all([
    api("/api/admin/painel"), api("/api/livros"), api("/api/emprestimos"),
    api("/api/usuarios"), api("/api/autores"), api("/api/generos")]);

  // Armazena os autores e gêneros recebidos para utilização nos formulários.
  autores = aut; generos = gen;

  // Exibe os indicadores gerais do sistema no painel administrativo.
  document.getElementById("admin-stats").innerHTML = `
    <div class="stat"><b>${painel.livros}</b><span>livros cadastrados</span></div>
    <div class="stat"><b>${painel.usuarios}</b><span>usuários</span></div>
    <div class="stat"><b>${painel.emprestimos_ativos}</b><span>empréstimos ativos</span></div>
    <div class="stat"><b>${painel.emprestimos_atrasados}</b><span>atrasados</span></div>
    <div class="stat"><b>${painel.exemplares}</b><span>exemplares</span></div>
    <div class="stat"><b>${painel.avaliacoes}</b><span>avaliações</span></div>`;

  // Gera o gráfico dos livros mais emprestados.
  barras(document.getElementById("graf-livros"), painel.mais_emprestados);

  // Gera o gráfico dos gêneros mais populares.
  barras(document.getElementById("graf-generos"), painel.generos_populares);

  // Obtém os campos de seleção de autores e gêneros do formulário de livros.
  const sa = document.getElementById("liv-autor"), sg = document.getElementById("liv-genero");

  // Guarda temporariamente os valores selecionados antes de atualizar as opções.
  const va = sa.value, vg = sg.value;

  // Preenche o campo de seleção com os autores disponíveis.
  sa.innerHTML = autores.map(a => `<option value="${a.id_autor}">${esc(a.nome)}</option>`).join("");

  // Preenche o campo de seleção com os gêneros disponíveis.
  sg.innerHTML = generos.map(g => `<option value="${g.id_genero}">${esc(g.nome)}</option>`).join("");

  // Restaura os valores que estavam selecionados, caso ainda existam.
  if (va) sa.value = va; if (vg) sg.value = vg;

  // Monta a tabela administrativa com os livros cadastrados.
  document.getElementById("admin-lista-livros").innerHTML = livros.map(l => `
    <tr><td>${esc(l.titulo)}</td><td>${esc(l.autor)}</td><td>${esc(l.genero)}</td>
    <td>${l.quantidade_disponivel}/${l.quantidade_total}</td>
    <td><button class="sec" onclick="editarLivro(${l.id_livro})">Editar</button>
    <button class="perigo" onclick="excluirLivro(${l.id_livro})">Excluir</button></td></tr>`).join("");

  // Monta a tabela com todos os empréstimos registrados no sistema.
  document.getElementById("tab-todos").innerHTML = todos.map(e => `
    <tr><td>${esc(e.usuario)}</td><td>${esc(e.titulo)}</td><td>${e.data_emprestimo}</td>
    <td>${e.data_prevista_devolucao}</td><td>${rotuloStatus(e.status)}</td>
    <td>${e.status !== "devolvido" ? `<button onclick="devolver(${e.id_emprestimo})">Registrar devolução</button>` : ""}</td></tr>`).join("");

  // Monta a tabela com os usuários cadastrados, exibindo nome, e-mail, tipo e data de cadastro.
  document.getElementById("tab-usuarios").innerHTML = users.map(u => `
    <tr><td>${esc(u.nome)}</td><td>${esc(u.email)}</td><td>${u.tipo}</td><td>${u.data_cadastro}</td></tr>`).join("");
}

// Reúne os valores preenchidos no formulário de cadastro ou edição de livros.
function dadosFormLivro() {
  // Cria uma função auxiliar para obter o valor de um campo pelo seu ID.
  const v = id => document.getElementById(id).value;

  // Retorna um objeto com os dados do livro preenchidos no formulário.
  return { titulo: v("liv-titulo"), id_autor: v("liv-autor"), id_genero: v("liv-genero"), ano_publicacao: v("liv-ano"),
    editora: v("liv-editora"), isbn: v("liv-isbn"), quantidade_total: v("liv-qtd"),
    classificacao_indicativa: v("liv-class"), capa_url: v("liv-capa"), sinopse: v("liv-sinopse") };
}

// Limpa os campos do formulário de cadastro e edição de livros.
function limparFormLivro() {
  // Percorre os IDs dos campos que devem ser esvaziados.
  for (const id of ["liv-id", "liv-titulo", "liv-ano", "liv-editora", "liv-isbn", "liv-class", "liv-capa", "liv-sinopse"])
    document.getElementById(id).value = "";

  // Define a quantidade inicial de exemplares como 1.
  document.getElementById("liv-qtd").value = 1;

  // Restaura o título do formulário para o modo de cadastro.
  document.getElementById("titulo-form").textContent = "Cadastrar livro";

  // Oculta o botão utilizado para cancelar uma edição.
  document.getElementById("btn-cancelar").hidden = true;
}

// Função assíncrona que salva um novo livro ou atualiza um livro existente.
async function salvarLivro() {
  try {
    // Obtém o ID do livro. Se estiver vazio, trata-se de um novo cadastro.
    const id = document.getElementById("liv-id").value;

    // Envia os dados para a API.
    // Utiliza PUT quando existe um ID e POST quando se trata de um novo livro.
    const d = await api(id ? "/api/livros/" + id : "/api/livros", id ? "PUT" : "POST", dadosFormLivro());

    // Exibe a mensagem retornada, limpa o formulário e atualiza a área administrativa.
    toast(d.mensagem); limparFormLivro(); carregarAdmin();
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao salvar o livro.
}

// Função assíncrona que carrega os dados de um livro para preencher o formulário de edição.
async function editarLivro(id) {
  try {
    // Busca os dados do livro pelo seu ID.
    const l = (await api("/api/livros/" + id)).livro;

    // Cria uma função auxiliar para preencher um campo com determinado valor.
    // Se o valor for nulo ou indefinido, utiliza uma string vazia.
    const set = (k, v) => (document.getElementById(k).value = v ?? "");

    // Preenche os campos do formulário com os dados do livro selecionado.
    set("liv-id", l.id_livro); set("liv-titulo", l.titulo); set("liv-autor", l.id_autor); set("liv-genero", l.id_genero);
    set("liv-ano", l.ano_publicacao); set("liv-editora", l.editora); set("liv-isbn", l.isbn);
    set("liv-qtd", l.quantidade_total); set("liv-class", l.classificacao_indicativa);
    set("liv-capa", l.capa_url); set("liv-sinopse", l.sinopse);

    // Altera o título do formulário para indicar que o usuário está editando um livro.
    document.getElementById("titulo-form").textContent = "Editar livro";

    // Exibe o botão que permite cancelar a edição.
    document.getElementById("btn-cancelar").hidden = false;

    // Rola a página suavemente até o início para facilitar o acesso ao formulário.
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao buscar os dados do livro.
}

// Função assíncrona responsável por excluir um livro do sistema.
async function excluirLivro(id) {
  // Solicita confirmação antes de realizar a exclusão.
  if (!confirm("Excluir este livro?")) return;

  try {
    // Envia uma requisição DELETE para excluir o livro e exibe a mensagem retornada.
    toast((await api("/api/livros/" + id, "DELETE")).mensagem);

    // Atualiza os dados exibidos na área administrativa.
    carregarAdmin();
  }
  catch (e) { tratarErro(e); } // Trata possíveis erros durante a exclusão.
}

// Função assíncrona que cadastra um novo autor no sistema.
async function novoAutor() {
  try {
    // Envia os dados do autor para a API por meio de uma requisição POST.
    await api("/api/autores", "POST", { nome: document.getElementById("novo-autor-nome").value,
      nacionalidade: document.getElementById("novo-autor-nac").value });

    // Limpa os campos do formulário após o cadastro.
    document.getElementById("novo-autor-nome").value = ""; document.getElementById("novo-autor-nac").value = "";

    // Exibe uma mensagem de confirmação e atualiza os dados administrativos.
    toast("Autor adicionado."); carregarAdmin();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante o cadastro do autor.
}

// Função assíncrona que cadastra um novo gênero literário no sistema.
async function novoGenero() {
  try {
    // Envia o nome e a descrição do gênero para a API.
    await api("/api/generos", "POST", { nome: document.getElementById("novo-genero-nome").value,
      descricao: document.getElementById("novo-genero-desc").value });

    // Limpa os campos do formulário após o cadastro.
    document.getElementById("novo-genero-nome").value = ""; document.getElementById("novo-genero-desc").value = "";

    // Exibe uma mensagem de confirmação e atualiza a área administrativa.
    toast("Gênero adicionado."); carregarAdmin();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante o cadastro do gênero.
}