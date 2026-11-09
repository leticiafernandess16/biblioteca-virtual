// ===== Login, cadastro, perfil e estante =====
let abaEstante = "favoritos";
let dadosEstante = null;

async function entrar() {
  try {
    const d = await api("/api/login", "POST", {
      email: document.getElementById("login-email").value,
      senha: document.getElementById("login-senha").value });
    usuario = d.usuario;
    await recarregarEstado();
    toast("Bem-vindo(a), " + usuario.nome + "! 🌸");
    mostrarView("home");
  } catch (e) { tratarErro(e); }
}

async function cadastrar() {
  try {
    const email = document.getElementById("cad-email").value;
    const senha = document.getElementById("cad-senha").value;
    const d = await api("/api/cadastro", "POST", {
      nome: document.getElementById("cad-nome").value, email, senha });
    toast(d.mensagem);
    document.getElementById("login-email").value = email;
    document.getElementById("login-senha").focus();
  } catch (e) { tratarErro(e); }
}

async function sair() {
  await api("/api/logout", "POST");
  usuario = null; await recarregarEstado();
  toast("Você saiu da conta.");
  mostrarView("home");
}

function preencherPerfil() {
  document.getElementById("perfil-nome").value = usuario.nome;
  document.getElementById("perfil-email").value = usuario.email;
  document.getElementById("perfil-senha").value = "";
  document.getElementById("perfil-info").textContent =
    `Conta ${usuario.tipo === "admin" ? "administrativa" : "de leitor"} · membro desde ${usuario.data_cadastro}`;
}

async function salvarPerfil() {
  try {
    const d = await api("/api/perfil", "PUT", {
      nome: document.getElementById("perfil-nome").value,
      senha: document.getElementById("perfil-senha").value });
    usuario = d.usuario; toast(d.mensagem); montarNav("perfil"); preencherPerfil();
  } catch (e) { tratarErro(e); }
}

// ===== Estante =====
async function carregarEstante() {
  dadosEstante = await api("/api/estante");
  idsFav = new Set(dadosEstante.ids_favoritos);
  listaMap = dadosEstante.lista;
  renderMeta();
  renderEstante();
}

function renderEstante() {
  const lista = dadosEstante[abaEstante] || [];
  const vazio = { favoritos: "Você ainda não favoritou nenhum livro. Toque no ♥ de um livro!",
    quero_ler: "Sua lista de leitura está vazia. Abra um livro e escolha “Quero ler”.",
    lidos: "Nenhum livro marcado como lido ainda." }[abaEstante];
  document.getElementById("estante-lista").innerHTML = lista.length ? lista.map(cardLivro).join("") : `<p class="vazio">${vazio} 🌸</p>`;
}

function renderMeta() {
  const m = dadosEstante.meta, ano = dadosEstante.ano;
  const form = `<div class="meta-form"><input id="meta-qtd" type="number" min="1" max="365" value="${m ? m.quantidade_meta : 12}">
    <button onclick="salvarMeta()">${m ? "Atualizar meta" : "Definir meta"}</button></div>`;
  document.getElementById("meta-card").innerHTML = m
    ? `<div style="flex:1;min-width:240px"><h3 style="margin:0">🎯 Desafio de leitura ${ano}</h3>
       <p style="margin:4px 0"><b>${m.lidos}</b> de <b>${m.quantidade_meta}</b> livros lidos (${m.percentual}%)</p>
       <div class="progresso"><div style="width:${m.percentual}%"></div></div>
       ${m.percentual >= 100 ? "<p>🎉 Meta alcançada! Parabéns!</p>" : ""}</div>${form}`
    : `<div><h3 style="margin:0">🎯 Desafio de leitura ${ano}</h3>
       <p style="margin:4px 0">Quantos livros você quer ler este ano?</p></div>${form}`;
}

async function salvarMeta() {
  try {
    const d = await api("/api/meta", "PUT", { quantidade_meta: document.getElementById("meta-qtd").value });
    toast(d.mensagem); carregarEstante();
  } catch (e) { tratarErro(e); }
}
