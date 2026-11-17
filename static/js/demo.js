// ===== Modo demonstração estático =====
//
// O GitHub Pages não executa Python/Flask. Quando o site é aberto em
// github.io, via file:// ou com ?demo=1, este arquivo assume o lugar da API:
// as mesmas rotas usadas pelo front-end são respondidas no navegador com os
// dados exportados do banco (static/demo/dados.js) e persistidas no
// localStorage. O Flask continua funcionando normalmente em outros endereços.

// Detecta automaticamente o ambiente estático.
var MODO_ESTATICO =
  location.protocol === "file:" ||
  location.hostname.endsWith("github.io") ||
  new URLSearchParams(location.search).has("demo");

// Chaves usadas para guardar os dados e a sessão no navegador.
var CHAVE_DADOS = "biblioteca-lirio-dados-v1";
var CHAVE_SESSAO = "biblioteca-lirio-sessao-v1";

// Guarda os dados em memória depois do primeiro carregamento.
var estadoDemo = null;

// Guarda o ID do usuário conectado (a sessão do Flask é substituída por ele).
var idSessao = lerJSON(CHAVE_SESSAO, null);


// ===== Persistência local =====

function armazenamentoLocal() {
  // Alguns navegadores bloqueiam o localStorage em arquivos abertos via
  // file://. Nesse caso, o modo demo continua funcionando apenas em memória.
  try { return window.localStorage; } catch { return null; }
}

function lerJSON(chave, padrao) {
  // Lê e interpreta um valor salvo. Se algo falhar, devolve o padrão.
  try {
    const texto = armazenamentoLocal()?.getItem(chave);
    return texto ? JSON.parse(texto) : padrao;
  } catch { return padrao; }
}

function gravarJSON(chave, valor) {
  // Salva um valor sem interromper a aplicação se o navegador bloquear.
  try { armazenamentoLocal()?.setItem(chave, JSON.stringify(valor)); } catch { /* sem persistência */ }
}

function salvarEstado() {
  // Salva todas as alterações feitas no modo demo.
  gravarJSON(CHAVE_DADOS, estadoDemo);
}

function carregarEstadoDemo() {
  // Na primeira chamada, usa os dados exportados do banco. Depois disso,
  // reaproveita o estado em memória para manter as alterações do visitante.
  if (estadoDemo) return estadoDemo;

  const base = window.DADOS_DEMO;
  if (!base) throw new Error("Dados de demonstração não encontrados. Rode backend/exportar_demo.py.");

  const salvo = lerJSON(CHAVE_DADOS, null);

  // Se o formato dos dados mudou, descarta o estado antigo do navegador.
  estadoDemo = salvo && salvo.versao === base.versao
    ? salvo
    : JSON.parse(JSON.stringify(base));

  if (!salvo || salvo.versao !== base.versao) salvarEstado();
  return estadoDemo;
}


// ===== Utilidades de data e de dados =====

function hojeISO() {
  // Data local no formato AAAA-MM-DD, igual ao date('now') do SQLite.
  const d = new Date();
  const pad = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function dataMaisDias(dias) {
  // Soma dias à data atual e devolve no formato AAAA-MM-DD.
  const d = new Date();
  d.setDate(d.getDate() + Number(dias || 0));
  const pad = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function anoAtual() {
  return new Date().getFullYear();
}

function proximoId(lista, campo) {
  // Gera o próximo ID de uma coleção, imitando o AUTOINCREMENT do SQLite.
  return lista.reduce((maior, item) => Math.max(maior, Number(item[campo]) || 0), 0) + 1;
}

function normalizar(texto) {
  // Deixa a busca sem diferença entre maiúsculas, minúsculas e acentos.
  return String(texto ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function compararTitulos(a, b) {
  return String(a.titulo).localeCompare(String(b.titulo), "pt-BR", { sensitivity: "base" });
}

function usuarioSemSenha(u) {
  // Nunca devolve a senha para o restante da aplicação.
  return {
    id_usuario: u.id_usuario,
    nome: u.nome,
    email: u.email,
    tipo: u.tipo,
    data_cadastro: u.data_cadastro
  };
}

function usuarioAtual() {
  // Localiza o usuário da sessão atual no estado do modo demo.
  const estado = carregarEstadoDemo();
  return estado.usuarios.find(u => u.id_usuario === idSessao) || null;
}

function exigirLogin() {
  // Reproduz o erro 401 das rotas protegidas do Flask.
  const u = usuarioAtual();
  if (!u) throw new Error("Faça login para continuar.");
  return u;
}

function exigirAdmin() {
  // Reproduz o erro 403 das rotas administrativas do Flask.
  const u = exigirLogin();
  if (u.tipo !== "admin") throw new Error("Acesso restrito ao administrador.");
  return u;
}

function atualizarAtrasados(estado) {
  // Marca como atrasados os empréstimos ativos cuja devolução já venceu.
  const hoje = hojeISO();
  let alterou = false;

  estado.emprestimos.forEach(e => {
    if (e.status === "ativo" && e.data_prevista_devolucao < hoje) {
      e.status = "atrasado";
      alterou = true;
    }
  });

  if (alterou) salvarEstado();
}


// ===== Montagem das respostas =====

function livroDTO(livro, estado) {
  // Junta ao livro os mesmos campos calculados pela consulta SELECT_LIVRO.
  const autor = estado.autores.find(a => a.id_autor === livro.id_autor);
  const genero = estado.generos.find(g => g.id_genero === livro.id_genero);
  const avaliacoes = estado.avaliacoes.filter(a => a.id_livro === livro.id_livro);

  const media = avaliacoes.length
    ? Math.round(avaliacoes.reduce((soma, a) => soma + a.nota, 0) * 10 / avaliacoes.length) / 10
    : null;

  return {
    ...livro,
    autor: autor ? autor.nome : "",
    genero: genero ? genero.nome : "",
    nota_media: media,
    total_avaliacoes: avaliacoes.length,
    total_emprestimos: estado.emprestimos.filter(e => e.id_livro === livro.id_livro).length,
    disponivel: livro.quantidade_disponivel > 0
  };
}

function listarLivros(estado, opcoes = {}) {
  // Reproduz os filtros e a ordenação do LivroDAO.listar().
  const busca = normalizar(opcoes.busca || "");
  const idGenero = Number(opcoes.genero) || null;
  const ordem = opcoes.ordem || "titulo";
  const notaMin = Number(opcoes.notaMin) || 0;
  const limite = Number(opcoes.limite) || 0;

  let livros = estado.livros.map(l => livroDTO(l, estado));

  if (busca) {
    livros = livros.filter(l =>
      normalizar(l.titulo).includes(busca) ||
      normalizar(l.autor).includes(busca) ||
      normalizar(l.genero).includes(busca)
    );
  }

  if (idGenero) livros = livros.filter(l => l.id_genero === idGenero);
  if (opcoes.disponiveis) livros = livros.filter(l => l.quantidade_disponivel > 0);
  if (notaMin) livros = livros.filter(l => (l.nota_media || 0) >= notaMin);

  const ordens = {
    titulo: compararTitulos,
    popular: (a, b) => (b.total_emprestimos - a.total_emprestimos) || compararTitulos(a, b),
    avaliacao: (a, b) => ((b.nota_media || 0) - (a.nota_media || 0)) ||
      (b.total_avaliacoes - a.total_avaliacoes) || compararTitulos(a, b),
    recentes: (a, b) => ((b.ano_publicacao || 0) - (a.ano_publicacao || 0)) || compararTitulos(a, b)
  };

  livros.sort(ordens[ordem] || ordens.titulo);
  if (limite) livros = livros.slice(0, limite);
  return livros;
}

function generosComContagem(estado) {
  // Reproduz o LEFT JOIN que conta os livros de cada gênero.
  return estado.generos
    .map(g => ({
      ...g,
      total_livros: estado.livros.filter(l => l.id_genero === g.id_genero).length
    }))
    .sort((a, b) => String(a.nome).localeCompare(String(b.nome), "pt-BR", { sensitivity: "base" }));
}

function estatisticas(estado) {
  // Reproduz o resumo do EstatisticaDAO.
  atualizarAtrasados(estado);

  return {
    livros: estado.livros.length,
    exemplares: estado.livros.reduce((soma, l) => soma + (l.quantidade_total || 0), 0),
    usuarios: estado.usuarios.length,
    emprestimos_total: estado.emprestimos.length,
    emprestimos_ativos: estado.emprestimos.filter(e => e.status === "ativo" || e.status === "atrasado").length,
    emprestimos_atrasados: estado.emprestimos.filter(e => e.status === "atrasado").length,
    avaliacoes: estado.avaliacoes.length,
    generos: estado.generos.length
  };
}

function livroDoDia(estado) {
  // Reproduz o sorteio diário do LivroDAO.livro_do_dia().
  const ids = estado.livros.map(l => l.id_livro).sort((a, b) => a - b);
  if (!ids.length) return null;

  // date.toordinal() do Python equivale a estes dias desde 0001-01-01.
  const ordinal = Math.floor(Date.now() / 86400000) + 719163;
  const livro = estado.livros.find(l => l.id_livro === ids[ordinal % ids.length]);
  return livro ? livroDTO(livro, estado) : null;
}

function curiosidadeAleatoria(estado, excluir = null) {
  // Reproduz o ORDER BY RANDOM() LIMIT 1 do CuriosidadeDAO.
  let itens = estado.curiosidades;
  if (excluir) itens = itens.filter(c => c.id_curiosidade !== excluir);
  if (!itens.length) return null;
  return itens[Math.floor(Math.random() * itens.length)];
}

function emprestimoDTO(emprestimo, estado) {
  // Junta ao empréstimo o título do livro e o nome do leitor.
  const livro = estado.livros.find(l => l.id_livro === emprestimo.id_livro);
  const usuario = estado.usuarios.find(u => u.id_usuario === emprestimo.id_usuario);

  return {
    ...emprestimo,
    titulo: livro ? livro.titulo : "",
    usuario: usuario ? usuario.nome : ""
  };
}

function recomendacoes(estado, idUsuario) {
  // Reproduz o LivroDAO.recomendar() usando favoritos, empréstimos e lista.
  const frequencia = new Map();
  const contar = idLivro => {
    const livro = estado.livros.find(l => l.id_livro === idLivro);
    if (!livro) return;
    frequencia.set(livro.id_genero, (frequencia.get(livro.id_genero) || 0) + 1);
  };

  estado.favoritos.filter(f => f.id_usuario === idUsuario).forEach(f => contar(f.id_livro));
  estado.emprestimos.filter(e => e.id_usuario === idUsuario).forEach(e => contar(e.id_livro));
  estado.lista_leitura.filter(l => l.id_usuario === idUsuario).forEach(l => contar(l.id_livro));

  const generos = [...frequencia.entries()]
    .sort((a, b) => (b[1] - a[1]) || (a[0] - b[0]))
    .slice(0, 3)
    .map(entrada => entrada[0]);

  if (!generos.length) return listarLivros(estado, { ordem: "avaliacao", limite: 6 });

  const vistos = new Set([
    ...estado.favoritos.filter(f => f.id_usuario === idUsuario).map(f => f.id_livro),
    ...estado.emprestimos.filter(e => e.id_usuario === idUsuario).map(e => e.id_livro),
    ...estado.lista_leitura.filter(l => l.id_usuario === idUsuario).map(l => l.id_livro)
  ]);

  const candidatos = [];
  generos.forEach(genero => {
    candidatos.push(...listarLivros(estado, { genero, ordem: "avaliacao" }));
  });

  return candidatos.filter(l => !vistos.has(l.id_livro)).slice(0, 6);
}

function estanteDTO(estado, idUsuario) {
  // Reproduz a montagem da rota GET /api/estante.
  const mapa = {};
  estado.lista_leitura
    .filter(l => l.id_usuario === idUsuario)
    .forEach(l => { mapa[l.id_livro] = l.status; });

  const favoritos = estado.favoritos
    .filter(f => f.id_usuario === idUsuario)
    .map(f => f.id_livro)
    .sort((a, b) => a - b);

  const comStatus = ids => ids
    .map(id => estado.livros.find(l => l.id_livro === id))
    .filter(Boolean)
    .map(livro => livroDTO(livro, estado));

  const ano = anoAtual();
  const meta = estado.metas_leitura.find(m => m.id_usuario === idUsuario && m.ano === ano);
  const lidos = estado.lista_leitura.filter(
    l => l.id_usuario === idUsuario && l.status === "lido" && String(l.data_leitura || "").startsWith(String(ano))
  ).length;

  return {
    favoritos: comStatus(favoritos),
    quero_ler: comStatus(Object.keys(mapa).filter(id => mapa[id] === "quero_ler").map(Number)),
    lidos: comStatus(Object.keys(mapa).filter(id => mapa[id] === "lido").map(Number)),
    ids_favoritos: favoritos,
    lista: mapa,
    meta: meta ? {
      ...meta,
      lidos,
      percentual: meta.quantidade_meta ? Math.min(100, Math.round(lidos * 100 / meta.quantidade_meta)) : 0
    } : null,
    ano
  };
}

function painelAdministrativo(estado) {
  // Reproduz o painel do EstatisticaDAO com os gráficos do front-end.
  const dados = estatisticas(estado);

  dados.mais_emprestados = estado.livros
    .map(l => ({
      titulo: l.titulo,
      total: estado.emprestimos.filter(e => e.id_livro === l.id_livro).length
    }))
    .sort((a, b) => (b.total - a.total) || compararTitulos(a, b))
    .slice(0, 5);

  dados.generos_populares = estado.generos
    .map(g => ({
      titulo: g.nome,
      total: estado.emprestimos.filter(e => {
        const livro = estado.livros.find(l => l.id_livro === e.id_livro);
        return livro && livro.id_genero === g.id_genero;
      }).length
    }))
    .sort((a, b) => (b.total - a.total) ||
      String(a.titulo).localeCompare(String(b.titulo), "pt-BR", { sensitivity: "base" }))
    .slice(0, 5);

  return dados;
}


// ===== Operações administrativas e do leitor =====

function dadosDoLivro(estado, corpo) {
  // Valida os campos do formulário de livro, como _livro_do_json() no Flask.
  const titulo = String(corpo.titulo ?? "").trim();
  if (!titulo) throw new Error("Informe o título.");

  const total = corpo.quantidade_total === undefined || corpo.quantidade_total === "" ||
    corpo.quantidade_total === null ? 1 : parseInt(corpo.quantidade_total, 10);

  const ano = corpo.ano_publicacao === undefined || corpo.ano_publicacao === "" ||
    corpo.ano_publicacao === null ? null : parseInt(corpo.ano_publicacao, 10);

  const idAutor = parseInt(corpo.id_autor, 10);
  const idGenero = parseInt(corpo.id_genero, 10);

  if (!Number.isFinite(total) || !Number.isFinite(idAutor) || !Number.isFinite(idGenero) ||
    (ano !== null && !Number.isFinite(ano))) {
    throw new Error("Dados inválidos (autor, gênero, ano ou quantidade).");
  }

  if (total < 0) throw new Error("Quantidade inválida.");

  const autor = estado.autores.find(a => a.id_autor === idAutor);
  const genero = estado.generos.find(g => g.id_genero === idGenero);
  if (!autor || !genero) throw new Error("Não foi possível cadastrar (ISBN repetido ou autor/gênero inexistente).");

  return {
    titulo,
    isbn: String(corpo.isbn ?? "").trim() || null,
    ano_publicacao: ano,
    editora: corpo.editora ?? "",
    quantidade_total: total,
    capa_url: corpo.capa_url ?? "",
    classificacao_indicativa: corpo.classificacao_indicativa ?? "",
    sinopse: corpo.sinopse ?? "",
    id_autor: idAutor,
    id_genero: idGenero
  };
}


// ===== Roteador que imita as rotas Flask =====

async function apiEstatica(url, metodo = "GET", corpo = null) {
  // Converte a URL em caminho + parâmetros. A base fictícia evita que o
  // subdiretório do GitHub Pages (/biblioteca-virtual/) interfira na rota.
  const estado = carregarEstadoDemo();
  const endereco = new URL(url, "http://biblioteca.local");
  const caminho = endereco.pathname.replace(/\/+$/, "") || "/";
  const q = endereco.searchParams;
  const m = String(metodo || "GET").toUpperCase();
  const d = corpo || {};

  // ----- Usuários e sessão -----

  if (caminho === "/api/me" && m === "GET") {
    return { usuario: usuarioAtual() ? usuarioSemSenha(usuarioAtual()) : null };
  }

  if (caminho === "/api/login" && m === "POST") {
    const email = String(d.email ?? "").trim().toLowerCase();
    const u = estado.usuarios.find(x => String(x.email).toLowerCase() === email);

    if (!u || !u.senha || u.senha !== String(d.senha ?? "")) {
      throw new Error("E-mail ou senha incorretos.");
    }

    idSessao = u.id_usuario;
    gravarJSON(CHAVE_SESSAO, idSessao);
    return { usuario: usuarioSemSenha(u) };
  }

  if (caminho === "/api/cadastro" && m === "POST") {
    const nome = String(d.nome ?? "").trim();
    const email = String(d.email ?? "").trim().toLowerCase();
    const senha = String(d.senha ?? "");

    if (nome.length < 2) throw new Error("Informe o nome.");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new Error("E-mail inválido.");
    if (senha.length < 6) throw new Error("A senha deve ter ao menos 6 caracteres.");
    if (estado.usuarios.some(u => String(u.email).toLowerCase() === email)) throw new Error("E-mail já cadastrado.");

    estado.usuarios.push({
      id_usuario: proximoId(estado.usuarios, "id_usuario"),
      nome,
      email,
      senha,
      tipo: "leitor",
      data_cadastro: hojeISO()
    });

    salvarEstado();
    return { mensagem: "Conta criada! Faça login." };
  }

  if (caminho === "/api/logout" && m === "POST") {
    idSessao = null;
    gravarJSON(CHAVE_SESSAO, null);
    return { mensagem: "Sessão encerrada." };
  }

  if (caminho === "/api/perfil" && m === "PUT") {
    const u = exigirLogin();
    const nome = String(d.nome ?? "").trim();
    const senha = String(d.senha ?? "");

    if (nome.length < 2) throw new Error("Informe o nome.");
    if (senha && senha.length < 6) throw new Error("A nova senha deve ter ao menos 6 caracteres.");

    u.nome = nome;
    if (senha) u.senha = senha;
    salvarEstado();

    return { mensagem: "Perfil atualizado.", usuario: usuarioSemSenha(u) };
  }

  if (caminho === "/api/usuarios" && m === "GET") {
    exigirAdmin();
    return [...estado.usuarios]
      .sort((a, b) => String(a.nome).localeCompare(String(b.nome), "pt-BR", { sensitivity: "base" }))
      .map(usuarioSemSenha);
  }

  // ----- Livros, gêneros e autores -----

  if (caminho === "/api/livros" && m === "GET") {
    return listarLivros(estado, {
      busca: q.get("busca") || "",
      genero: q.get("genero"),
      disponiveis: q.get("disponiveis") === "1",
      ordem: q.get("ordem") || "titulo",
      notaMin: q.get("nota_min"),
      limite: q.get("limite")
    });
  }

  if (caminho === "/api/livros" && m === "POST") {
    exigirAdmin();
    const dados = dadosDoLivro(estado, d);

    if (dados.isbn && estado.livros.some(l => l.isbn === dados.isbn)) {
      throw new Error("Não foi possível cadastrar (ISBN repetido ou autor/gênero inexistente).");
    }

    const livro = {
      id_livro: proximoId(estado.livros, "id_livro"),
      ...dados,
      quantidade_disponivel: dados.quantidade_total,
      data_cadastro: hojeISO(),
      capa_demo: ""
    };

    estado.livros.push(livro);
    salvarEstado();
    return { id_livro: livro.id_livro, mensagem: "Livro cadastrado." };
  }

  let achado = caminho.match(/^\/api\/livros\/(\d+)$/);

  if (achado && m === "GET") {
    const livro = estado.livros.find(l => l.id_livro === Number(achado[1]));
    if (!livro) throw new Error("Livro não encontrado.");

    const avaliacoes = estado.avaliacoes
      .filter(a => a.id_livro === livro.id_livro)
      .sort((a, b) => b.id_avaliacao - a.id_avaliacao)
      .map(a => ({
        ...a,
        usuario: (estado.usuarios.find(u => u.id_usuario === a.id_usuario) || {}).nome || ""
      }));

    const dto = livroDTO(livro, estado);
    return {
      livro: dto,
      avaliacoes,
      nota: { media: dto.nota_media, total: dto.total_avaliacoes }
    };
  }

  if (achado && m === "PUT") {
    exigirAdmin();
    const livro = estado.livros.find(l => l.id_livro === Number(achado[1]));
    if (!livro) throw new Error("Não foi possível editar o livro.");

    const dados = dadosDoLivro(estado, d);

    if (dados.isbn && estado.livros.some(l => l.id_livro !== livro.id_livro && l.isbn === dados.isbn)) {
      throw new Error("Não foi possível editar o livro.");
    }

    const emprestados = livro.quantidade_total - livro.quantidade_disponivel;
    const novaDisponivel = dados.quantidade_total - emprestados;
    if (novaDisponivel < 0) throw new Error("Não foi possível editar o livro.");

    Object.assign(livro, dados, { quantidade_disponivel: novaDisponivel });
    salvarEstado();
    return { mensagem: "Livro atualizado." };
  }

  if (achado && m === "DELETE") {
    exigirAdmin();
    const id = Number(achado[1]);
    const existe = estado.livros.some(l => l.id_livro === id);
    const temEmprestimo = estado.emprestimos.some(e => e.id_livro === id);

    if (!existe || temEmprestimo) {
      throw new Error("Não foi possível excluir (livro inexistente ou com empréstimos).");
    }

    estado.livros = estado.livros.filter(l => l.id_livro !== id);
    estado.avaliacoes = estado.avaliacoes.filter(a => a.id_livro !== id);
    estado.favoritos = estado.favoritos.filter(f => f.id_livro !== id);
    estado.lista_leitura = estado.lista_leitura.filter(l => l.id_livro !== id);
    salvarEstado();
    return { mensagem: "Livro excluído." };
  }

  achado = caminho.match(/^\/api\/livros\/(\d+)\/avaliacoes$/);

  if (achado && m === "POST") {
    const u = exigirLogin();
    const idLivro = Number(achado[1]);

    if (!estado.livros.some(l => l.id_livro === idLivro)) throw new Error("Livro não encontrado.");

    const nota = parseInt(d.nota, 10);
    if (!Number.isFinite(nota)) throw new Error("Nota inválida.");
    if (nota < 1 || nota > 5) throw new Error("A nota deve ser de 1 a 5.");

    const existente = estado.avaliacoes.find(
      a => a.id_usuario === u.id_usuario && a.id_livro === idLivro
    );

    if (existente) {
      existente.nota = nota;
      existente.comentario = String(d.comentario ?? "").slice(0, 500);
      existente.data_avaliacao = hojeISO();
    } else {
      estado.avaliacoes.push({
        id_avaliacao: proximoId(estado.avaliacoes, "id_avaliacao"),
        nota,
        comentario: String(d.comentario ?? "").slice(0, 500),
        data_avaliacao: hojeISO(),
        id_usuario: u.id_usuario,
        id_livro: idLivro
      });
    }

    salvarEstado();
    return { mensagem: "Avaliação registrada." };
  }

  if (caminho === "/api/generos" && m === "GET") {
    return generosComContagem(estado);
  }

  if (caminho === "/api/generos" && m === "POST") {
    exigirAdmin();
    const nome = String(d.nome ?? "").trim();
    if (!nome) throw new Error("Informe o nome do gênero.");
    if (estado.generos.some(g => g.nome === nome)) throw new Error("Gênero já existe.");

    const genero = {
      id_genero: proximoId(estado.generos, "id_genero"),
      nome,
      descricao: d.descricao ?? ""
    };

    estado.generos.push(genero);
    salvarEstado();
    return { id_genero: genero.id_genero };
  }

  if (caminho === "/api/autores" && m === "GET") {
    return [...estado.autores].sort(
      (a, b) => String(a.nome).localeCompare(String(b.nome), "pt-BR", { sensitivity: "base" })
    );
  }

  if (caminho === "/api/autores" && m === "POST") {
    exigirAdmin();
    const nome = String(d.nome ?? "").trim();
    if (!nome) throw new Error("Informe o nome do autor.");

    const autor = {
      id_autor: proximoId(estado.autores, "id_autor"),
      nome,
      nacionalidade: d.nacionalidade ?? "",
      biografia: d.biografia ?? ""
    };

    estado.autores.push(autor);
    salvarEstado();
    return { id_autor: autor.id_autor };
  }

  // ----- Página inicial, estatísticas e curiosidades -----

  if (caminho === "/api/home" && m === "GET") {
    return {
      livro_do_dia: livroDoDia(estado),
      destaques: listarLivros(estado, { ordem: "avaliacao", limite: 8 }),
      populares: listarLivros(estado, { ordem: "popular", limite: 8 }),
      lancamentos: listarLivros(estado, { ordem: "recentes", limite: 8 }),
      generos: generosComContagem(estado),
      curiosidade: curiosidadeAleatoria(estado),
      estatisticas: estatisticas(estado)
    };
  }

  if (caminho === "/api/estatisticas" && m === "GET") {
    return estatisticas(estado);
  }

  if (caminho === "/api/curiosidade" && m === "GET") {
    const excluir = parseInt(q.get("excluir"), 10);
    return curiosidadeAleatoria(estado, Number.isFinite(excluir) ? excluir : null);
  }

  if (caminho === "/api/recomendacoes" && m === "GET") {
    const u = exigirLogin();
    return recomendacoes(estado, u.id_usuario);
  }

  // ----- Estante, favoritos, lista e meta -----

  if (caminho === "/api/estante" && m === "GET") {
    const u = exigirLogin();
    return estanteDTO(estado, u.id_usuario);
  }

  achado = caminho.match(/^\/api\/favoritos\/(\d+)$/);

  if (achado && m === "POST") {
    const u = exigirLogin();
    const idLivro = Number(achado[1]);

    if (!estado.livros.some(l => l.id_livro === idLivro)) throw new Error("Livro não encontrado.");

    const indice = estado.favoritos.findIndex(
      f => f.id_usuario === u.id_usuario && f.id_livro === idLivro
    );

    let favoritado;
    if (indice >= 0) {
      estado.favoritos.splice(indice, 1);
      favoritado = false;
    } else {
      estado.favoritos.push({
        id_favorito: proximoId(estado.favoritos, "id_favorito"),
        data_adicao: hojeISO(),
        id_usuario: u.id_usuario,
        id_livro: idLivro
      });
      favoritado = true;
    }

    salvarEstado();
    return {
      favoritado,
      mensagem: favoritado ? "Adicionado aos favoritos." : "Removido dos favoritos."
    };
  }

  achado = caminho.match(/^\/api\/lista\/(\d+)$/);

  if (achado && m === "POST") {
    const u = exigirLogin();
    const idLivro = Number(achado[1]);
    const status = d.status || "quero_ler";

    if (status !== "quero_ler" && status !== "lido") {
      throw new Error("Não foi possível atualizar a lista.");
    }

    if (!estado.livros.some(l => l.id_livro === idLivro)) {
      throw new Error("Não foi possível atualizar a lista.");
    }

    const existente = estado.lista_leitura.find(
      l => l.id_usuario === u.id_usuario && l.id_livro === idLivro
    );

    if (existente) {
      existente.status = status;
      existente.data_leitura = status === "lido" ? hojeISO() : null;
    } else {
      estado.lista_leitura.push({
        id_lista: proximoId(estado.lista_leitura, "id_lista"),
        data_adicao: hojeISO(),
        data_leitura: status === "lido" ? hojeISO() : null,
        status,
        id_usuario: u.id_usuario,
        id_livro: idLivro
      });
    }

    salvarEstado();
    return { mensagem: status === "lido" ? "Marcado como lido!" : "Adicionado à lista de leitura." };
  }

  if (achado && m === "DELETE") {
    const u = exigirLogin();
    const idLivro = Number(achado[1]);

    estado.lista_leitura = estado.lista_leitura.filter(
      l => !(l.id_usuario === u.id_usuario && l.id_livro === idLivro)
    );

    salvarEstado();
    return { mensagem: "Removido da lista." };
  }

  if (caminho === "/api/meta" && m === "PUT") {
    const u = exigirLogin();
    const qtd = parseInt(d.quantidade_meta, 10);

    if (!Number.isFinite(qtd)) throw new Error("Informe um número.");
    if (qtd < 1 || qtd > 365) throw new Error("A meta deve ficar entre 1 e 365 livros.");

    const ano = anoAtual();
    const existente = estado.metas_leitura.find(m => m.id_usuario === u.id_usuario && m.ano === ano);

    if (existente) {
      existente.quantidade_meta = qtd;
    } else {
      estado.metas_leitura.push({
        id_meta: proximoId(estado.metas_leitura, "id_meta"),
        ano,
        quantidade_meta: qtd,
        id_usuario: u.id_usuario
      });
    }

    salvarEstado();
    return { mensagem: "Meta de leitura salva!" };
  }

  // ----- Empréstimos -----

  if (caminho === "/api/emprestimos/meus" && m === "GET") {
    const u = exigirLogin();
    atualizarAtrasados(estado);

    return estado.emprestimos
      .filter(e => e.id_usuario === u.id_usuario)
      .sort((a, b) => b.id_emprestimo - a.id_emprestimo)
      .map(e => emprestimoDTO(e, estado));
  }

  if (caminho === "/api/emprestimos" && m === "GET") {
    exigirAdmin();
    atualizarAtrasados(estado);

    return [...estado.emprestimos]
      .sort((a, b) => b.id_emprestimo - a.id_emprestimo)
      .map(e => emprestimoDTO(e, estado));
  }

  achado = caminho.match(/^\/api\/emprestimos\/(\d+)\/devolver$/);

  if (achado && m === "POST") {
    const u = exigirLogin();
    const emprestimo = estado.emprestimos.find(e => e.id_emprestimo === Number(achado[1]));

    if (!emprestimo) throw new Error("Empréstimo não encontrado.");
    if (u.tipo !== "admin" && emprestimo.id_usuario !== u.id_usuario) {
      throw new Error("Este empréstimo não é seu.");
    }
    if (emprestimo.status === "devolvido") throw new Error("Livro já devolvido.");

    emprestimo.status = "devolvido";
    emprestimo.data_devolucao = hojeISO();

    const livro = estado.livros.find(l => l.id_livro === emprestimo.id_livro);
    if (livro) livro.quantidade_disponivel += 1;

    salvarEstado();
    return { mensagem: "Devolução registrada." };
  }

  achado = caminho.match(/^\/api\/emprestimos\/(\d+)$/);

  if (achado && m === "POST") {
    const u = exigirLogin();
    const livro = estado.livros.find(l => l.id_livro === Number(achado[1]));

    if (!livro) throw new Error("Livro não encontrado.");
    if (livro.quantidade_disponivel <= 0) throw new Error("Não há exemplares disponíveis.");

    const duplicado = estado.emprestimos.some(
      e => e.id_usuario === u.id_usuario && e.id_livro === livro.id_livro &&
        (e.status === "ativo" || e.status === "atrasado")
    );

    if (duplicado) throw new Error("Você já possui este livro emprestado.");

    const prevista = dataMaisDias(estado.dias_emprestimo || 14);

    estado.emprestimos.push({
      id_emprestimo: proximoId(estado.emprestimos, "id_emprestimo"),
      data_emprestimo: hojeISO(),
      data_prevista_devolucao: prevista,
      data_devolucao: null,
      status: "ativo",
      id_usuario: u.id_usuario,
      id_livro: livro.id_livro
    });

    livro.quantidade_disponivel -= 1;
    salvarEstado();

    return { mensagem: `Empréstimo realizado! Devolução até ${prevista}.` };
  }

  // ----- Administração -----

  if (caminho === "/api/admin/painel" && m === "GET") {
    exigirAdmin();
    return painelAdministrativo(estado);
  }

  // Se alguma rota nova for criada no Flask e não for implementada aqui,
  // o erro abaixo deixa claro que falta atualizar o modo demonstração.
  throw new Error("Recurso não disponível no modo demonstração.");
}

// Aviso útil no console para identificar quando o site está em modo demo.
console.info("Biblioteca Lírio: modo demonstração estático ativo.");
