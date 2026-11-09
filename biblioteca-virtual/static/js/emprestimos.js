// ===== Empréstimos do usuário e área administrativa =====
async function pedirEmprestimo(idLivro) {
  try {
    const d = await api("/api/emprestimos/" + idLivro, "POST");
    toast(d.mensagem);
    fecharModal();
    atualizarTelasAbertas();
  } catch (e) { tratarErro(e); }
}

function atualizarTelasAbertas() {
  if (!document.getElementById("view-home").hidden) carregarHome().catch(tratarErro);
  if (!document.getElementById("view-catalogo").hidden) carregarCatalogo().catch(tratarErro);
  if (!document.getElementById("view-emprestimos").hidden) carregarMeusEmprestimos().catch(tratarErro);
  if (!document.getElementById("view-admin").hidden) carregarAdmin().catch(tratarErro);
}

const rotuloStatus = s => `<span class="badge ${s}">${s}</span>`;

async function carregarMeusEmprestimos() {
  const lista = await api("/api/emprestimos/meus");
  const conta = s => lista.filter(e => e.status === s).length;
  document.getElementById("resumo-emp").innerHTML = `
    <div class="stat"><b>${conta("ativo")}</b><span>em andamento</span></div>
    <div class="stat"><b>${conta("atrasado")}</b><span>atrasados</span></div>
    <div class="stat"><b>${conta("devolvido")}</b><span>devolvidos</span></div>`;
  document.getElementById("tab-meus").innerHTML = lista.map(e => `
    <tr><td><a href="#" onclick="event.preventDefault();abrirDetalhes(${e.id_livro})">${esc(e.titulo)}</a></td>
    <td>${e.data_emprestimo}</td><td>${e.data_prevista_devolucao}</td><td>${e.data_devolucao || "—"}</td>
    <td>${rotuloStatus(e.status)}</td>
    <td>${e.status !== "devolvido" ? `<button onclick="devolver(${e.id_emprestimo})">Devolver</button>` : ""}</td></tr>`
  ).join("") || `<tr><td colspan="6">Você ainda não fez nenhum empréstimo. 🌸</td></tr>`;
}

async function devolver(id) {
  try {
    const d = await api(`/api/emprestimos/${id}/devolver`, "POST");
    toast(d.mensagem);
    atualizarTelasAbertas();
  } catch (e) { tratarErro(e); }
}

// ---------- Administração ----------
function barras(el, itens) {
  const max = Math.max(1, ...itens.map(i => i.total));
  el.innerHTML = itens.map(i => `<div class="barra"><span>${esc(i.titulo)}</span>
    <div class="trilha"><div style="width:${i.total * 100 / max}%"></div></div><b>${i.total}</b></div>`).join("");
}

async function carregarAdmin() {
  const [painel, livros, todos, users, aut, gen] = await Promise.all([
    api("/api/admin/painel"), api("/api/livros"), api("/api/emprestimos"),
    api("/api/usuarios"), api("/api/autores"), api("/api/generos")]);
  autores = aut; generos = gen;

  document.getElementById("admin-stats").innerHTML = `
    <div class="stat"><b>${painel.livros}</b><span>livros cadastrados</span></div>
    <div class="stat"><b>${painel.usuarios}</b><span>usuários</span></div>
    <div class="stat"><b>${painel.emprestimos_ativos}</b><span>empréstimos ativos</span></div>
    <div class="stat"><b>${painel.emprestimos_atrasados}</b><span>atrasados</span></div>
    <div class="stat"><b>${painel.exemplares}</b><span>exemplares</span></div>
    <div class="stat"><b>${painel.avaliacoes}</b><span>avaliações</span></div>`;
  barras(document.getElementById("graf-livros"), painel.mais_emprestados);
  barras(document.getElementById("graf-generos"), painel.generos_populares);

  const sa = document.getElementById("liv-autor"), sg = document.getElementById("liv-genero");
  const va = sa.value, vg = sg.value;
  sa.innerHTML = autores.map(a => `<option value="${a.id_autor}">${esc(a.nome)}</option>`).join("");
  sg.innerHTML = generos.map(g => `<option value="${g.id_genero}">${esc(g.nome)}</option>`).join("");
  if (va) sa.value = va; if (vg) sg.value = vg;

  document.getElementById("admin-lista-livros").innerHTML = livros.map(l => `
    <tr><td>${esc(l.titulo)}</td><td>${esc(l.autor)}</td><td>${esc(l.genero)}</td>
    <td>${l.quantidade_disponivel}/${l.quantidade_total}</td>
    <td><button class="sec" onclick="editarLivro(${l.id_livro})">Editar</button>
    <button class="perigo" onclick="excluirLivro(${l.id_livro})">Excluir</button></td></tr>`).join("");

  document.getElementById("tab-todos").innerHTML = todos.map(e => `
    <tr><td>${esc(e.usuario)}</td><td>${esc(e.titulo)}</td><td>${e.data_emprestimo}</td>
    <td>${e.data_prevista_devolucao}</td><td>${rotuloStatus(e.status)}</td>
    <td>${e.status !== "devolvido" ? `<button onclick="devolver(${e.id_emprestimo})">Registrar devolução</button>` : ""}</td></tr>`).join("");

  document.getElementById("tab-usuarios").innerHTML = users.map(u => `
    <tr><td>${esc(u.nome)}</td><td>${esc(u.email)}</td><td>${u.tipo}</td><td>${u.data_cadastro}</td></tr>`).join("");
}

function dadosFormLivro() {
  const v = id => document.getElementById(id).value;
  return { titulo: v("liv-titulo"), id_autor: v("liv-autor"), id_genero: v("liv-genero"), ano_publicacao: v("liv-ano"),
    editora: v("liv-editora"), isbn: v("liv-isbn"), quantidade_total: v("liv-qtd"),
    classificacao_indicativa: v("liv-class"), capa_url: v("liv-capa"), sinopse: v("liv-sinopse") };
}

function limparFormLivro() {
  for (const id of ["liv-id", "liv-titulo", "liv-ano", "liv-editora", "liv-isbn", "liv-class", "liv-capa", "liv-sinopse"])
    document.getElementById(id).value = "";
  document.getElementById("liv-qtd").value = 1;
  document.getElementById("titulo-form").textContent = "Cadastrar livro";
  document.getElementById("btn-cancelar").hidden = true;
}

async function salvarLivro() {
  try {
    const id = document.getElementById("liv-id").value;
    const d = await api(id ? "/api/livros/" + id : "/api/livros", id ? "PUT" : "POST", dadosFormLivro());
    toast(d.mensagem); limparFormLivro(); carregarAdmin();
  } catch (e) { tratarErro(e); }
}

async function editarLivro(id) {
  try {
    const l = (await api("/api/livros/" + id)).livro;
    const set = (k, v) => (document.getElementById(k).value = v ?? "");
    set("liv-id", l.id_livro); set("liv-titulo", l.titulo); set("liv-autor", l.id_autor); set("liv-genero", l.id_genero);
    set("liv-ano", l.ano_publicacao); set("liv-editora", l.editora); set("liv-isbn", l.isbn);
    set("liv-qtd", l.quantidade_total); set("liv-class", l.classificacao_indicativa);
    set("liv-capa", l.capa_url); set("liv-sinopse", l.sinopse);
    document.getElementById("titulo-form").textContent = "Editar livro";
    document.getElementById("btn-cancelar").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (e) { tratarErro(e); }
}

async function excluirLivro(id) {
  if (!confirm("Excluir este livro?")) return;
  try { toast((await api("/api/livros/" + id, "DELETE")).mensagem); carregarAdmin(); }
  catch (e) { tratarErro(e); }
}

async function novoAutor() {
  try {
    await api("/api/autores", "POST", { nome: document.getElementById("novo-autor-nome").value,
      nacionalidade: document.getElementById("novo-autor-nac").value });
    document.getElementById("novo-autor-nome").value = ""; document.getElementById("novo-autor-nac").value = "";
    toast("Autor adicionado."); carregarAdmin();
  } catch (e) { tratarErro(e); }
}

async function novoGenero() {
  try {
    await api("/api/generos", "POST", { nome: document.getElementById("novo-genero-nome").value,
      descricao: document.getElementById("novo-genero-desc").value });
    document.getElementById("novo-genero-nome").value = ""; document.getElementById("novo-genero-desc").value = "";
    toast("Gênero adicionado."); carregarAdmin();
  } catch (e) { tratarErro(e); }
}
