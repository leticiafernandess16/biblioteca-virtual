// ===== Login, cadastro, perfil e estante =====

// Define a aba que será exibida inicialmente na estante do usuário.
let abaEstante = "favoritos";

// Armazena os dados carregados da estante pessoal.
let dadosEstante = null;

// Função assíncrona responsável por realizar o login do usuário.
async function entrar() {
  try {
    // Envia os dados de e-mail e senha para a API de autenticação.
    const d = await api("/api/login", "POST", {
      email: document.getElementById("login-email").value,
      senha: document.getElementById("login-senha").value });

    // Armazena os dados do usuário autenticado.
    usuario = d.usuario;

    // Atualiza os favoritos e a lista de leitura do usuário.
    await recarregarEstado();

    // Exibe uma mensagem de boas-vindas com o nome do usuário.
    toast("Bem-vindo(a), " + usuario.nome + "! 🌸");

    // Redireciona o usuário para a página inicial.
    mostrarView("home");
  } catch (e) { tratarErro(e); } // Exibe uma mensagem caso ocorra algum erro no login.
}

// Função assíncrona responsável por cadastrar um novo usuário.
async function cadastrar() {
  try {
    // Obtém o e-mail informado no formulário de cadastro.
    const email = document.getElementById("cad-email").value;

    // Obtém a senha informada pelo usuário.
    const senha = document.getElementById("cad-senha").value;

    // Envia os dados do novo usuário para a API de cadastro.
    const d = await api("/api/cadastro", "POST", {
      nome: document.getElementById("cad-nome").value, email, senha });

    // Exibe a mensagem retornada pela API após o cadastro.
    toast(d.mensagem);

    // Preenche o campo de e-mail do formulário de login com o e-mail cadastrado.
    document.getElementById("login-email").value = email;

    // Coloca o cursor no campo de senha para facilitar o acesso.
    document.getElementById("login-senha").focus();
  } catch (e) { tratarErro(e); } // Trata possíveis erros durante o cadastro.
}

// Função assíncrona responsável por encerrar a sessão do usuário.
async function sair() {
  // Envia uma requisição POST para a API realizar o logout.
  await api("/api/logout", "POST");

  // Limpa os dados do usuário conectado e atualiza o estado pessoal.
  usuario = null; await recarregarEstado();

  // Informa que o usuário saiu da conta.
  toast("Você saiu da conta.");

  // Retorna o usuário para a página inicial.
  mostrarView("home");
}

// Preenche os campos da tela de perfil com os dados do usuário autenticado.
function preencherPerfil() {
  // Exibe o nome cadastrado pelo usuário.
  document.getElementById("perfil-nome").value = usuario.nome;

  // Exibe o e-mail cadastrado na conta.
  document.getElementById("perfil-email").value = usuario.email;

  // Mantém o campo de senha vazio por segurança.
  document.getElementById("perfil-senha").value = "";

  // Exibe o tipo de conta e a data de cadastro do usuário.
  document.getElementById("perfil-info").textContent =
    `Conta ${usuario.tipo === "admin" ? "administrativa" : "de leitor"} · membro desde ${usuario.data_cadastro}`;
}

// Função assíncrona responsável por salvar as alterações do perfil.
async function salvarPerfil() {
  try {
    // Envia o novo nome e a senha informados para a API atualizar o perfil.
    const d = await api("/api/perfil", "PUT", {
      nome: document.getElementById("perfil-nome").value,
      senha: document.getElementById("perfil-senha").value });

    // Atualiza os dados locais do usuário com as informações retornadas pela API.
    usuario = d.usuario; toast(d.mensagem); montarNav("perfil"); preencherPerfil();

    // Exibe a mensagem de confirmação, atualiza o menu e recarrega os dados do perfil.
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao salvar as alterações.
}

// ===== Estante =====

// Função assíncrona responsável por carregar os dados da estante pessoal.
async function carregarEstante() {
  // Busca na API os livros, favoritos, listas e informações da estante.
  dadosEstante = await api("/api/estante");

  // Atualiza o conjunto de IDs dos livros favoritados.
  idsFav = new Set(dadosEstante.ids_favoritos);

  // Atualiza o mapa com a situação de leitura dos livros.
  listaMap = dadosEstante.lista;

  // Atualiza as informações da meta de leitura.
  renderMeta();

  // Exibe os livros correspondentes à aba selecionada.
  renderEstante();
}

// Organiza e exibe os livros da aba atual da estante.
function renderEstante() {
  // Obtém a lista de livros correspondente à aba selecionada.
  // Caso não exista uma lista para essa aba, utiliza um array vazio.
  const lista = dadosEstante[abaEstante] || [];

  // Define uma mensagem específica para cada aba quando não existem livros cadastrados.
  const vazio = { favoritos: "Você ainda não favoritou nenhum livro. Toque no ♥ de um livro!",
    quero_ler: "Sua lista de leitura está vazia. Abra um livro e escolha “Quero ler”.",
    lidos: "Nenhum livro marcado como lido ainda." }[abaEstante];

  // Exibe os cartões dos livros encontrados.
  // Se a lista estiver vazia, apresenta a mensagem correspondente à aba selecionada.
  document.getElementById("estante-lista").innerHTML = lista.length ? lista.map(cardLivro).join("") : `<p class="vazio">${vazio} 🌸</p>`;
}

// Exibe e atualiza as informações da meta anual de leitura do usuário.
function renderMeta() {
  // Obtém os dados da meta de leitura e o ano correspondente.
  const m = dadosEstante.meta, ano = dadosEstante.ano;

  // Cria o formulário para definir ou atualizar a quantidade de livros desejada.
  // Se já existir uma meta, utiliza sua quantidade atual como valor inicial.
  const form = `<div class="meta-form"><input id="meta-qtd" type="number" min="1" max="365" value="${m ? m.quantidade_meta : 12}">
    <button onclick="salvarMeta()">${m ? "Atualizar meta" : "Definir meta"}</button></div>`;

  // Verifica se o usuário já possui uma meta de leitura cadastrada.
  document.getElementById("meta-card").innerHTML = m
    // Se existir uma meta, exibe o progresso e a quantidade de livros lidos.
    ? `<div style="flex:1;min-width:240px"><h3 style="margin:0">🎯 Desafio de leitura ${ano}</h3>
       <p style="margin:4px 0"><b>${m.lidos}</b> de <b>${m.quantidade_meta}</b> livros lidos (${m.percentual}%)</p>
       <div class="progresso"><div style="width:${m.percentual}%"></div></div>
       ${m.percentual >= 100 ? "<p>🎉 Meta alcançada! Parabéns!</p>" : ""}</div>${form}`
    // Caso ainda não exista uma meta, apresenta o convite para definir uma quantidade de livros.
    : `<div><h3 style="margin:0">🎯 Desafio de leitura ${ano}</h3>
       <p style="margin:4px 0">Quantos livros você quer ler este ano?</p></div>${form}`;
}

// Função assíncrona responsável por salvar ou atualizar a meta anual de leitura.
async function salvarMeta() {
  try {
    // Envia a quantidade de livros definida pelo usuário para a API.
    const d = await api("/api/meta", "PUT", { quantidade_meta: document.getElementById("meta-qtd").value });

    // Exibe a mensagem retornada pela API e atualiza os dados da estante.
    toast(d.mensagem); carregarEstante();
  } catch (e) { tratarErro(e); } // Trata possíveis erros ao salvar a meta.
}