-- Biblioteca Virtual - esquema baseado no diagrama MER
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    senha_hash    TEXT NOT NULL,
    tipo          TEXT NOT NULL DEFAULT 'leitor' CHECK (tipo IN ('leitor','admin')),
    data_cadastro TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS autores (
    id_autor     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome         TEXT NOT NULL,
    nacionalidade TEXT,
    biografia    TEXT
);

CREATE TABLE IF NOT EXISTS generos (
    id_genero INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL UNIQUE,
    descricao TEXT
);

-- LIVRO: cada livro tem 1 autor (ESCREVE) e 1 gênero (CLASSIFICA)
CREATE TABLE IF NOT EXISTS livros (
    id_livro              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo                TEXT NOT NULL,
    isbn                  TEXT UNIQUE,
    ano_publicacao        INTEGER CHECK (ano_publicacao > 0),
    editora               TEXT,
    quantidade_total      INTEGER NOT NULL DEFAULT 1 CHECK (quantidade_total >= 0),
    quantidade_disponivel INTEGER NOT NULL DEFAULT 1 CHECK (quantidade_disponivel >= 0),
    capa_url              TEXT,
    classificacao_indicativa TEXT,
    sinopse               TEXT,
    data_cadastro         TEXT NOT NULL DEFAULT (date('now')),
    id_autor              INTEGER NOT NULL,
    id_genero             INTEGER NOT NULL,
    CHECK (quantidade_disponivel <= quantidade_total),
    FOREIGN KEY (id_autor)  REFERENCES autores(id_autor),
    FOREIGN KEY (id_genero) REFERENCES generos(id_genero)
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo           INTEGER PRIMARY KEY AUTOINCREMENT,
    data_emprestimo         TEXT NOT NULL DEFAULT (date('now')),
    data_prevista_devolucao TEXT NOT NULL,
    data_devolucao          TEXT,
    status                  TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo','devolvido','atrasado')),
    id_usuario              INTEGER NOT NULL,
    id_livro                INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_livro)   REFERENCES livros(id_livro)
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id_avaliacao   INTEGER PRIMARY KEY AUTOINCREMENT,
    nota           INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario     TEXT,
    data_avaliacao TEXT NOT NULL DEFAULT (date('now')),
    id_usuario     INTEGER NOT NULL,
    id_livro       INTEGER NOT NULL,
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_livro)   REFERENCES livros(id_livro) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favoritos (
    id_favorito INTEGER PRIMARY KEY AUTOINCREMENT,
    data_adicao TEXT NOT NULL DEFAULT (date('now')),
    id_usuario  INTEGER NOT NULL,
    id_livro    INTEGER NOT NULL,
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_livro)   REFERENCES livros(id_livro) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lista_leitura (
    id_lista    INTEGER PRIMARY KEY AUTOINCREMENT,
    data_adicao TEXT NOT NULL DEFAULT (date('now')),
    data_leitura TEXT,
    status      TEXT NOT NULL DEFAULT 'quero_ler' CHECK (status IN ('quero_ler','lido')),
    id_usuario  INTEGER NOT NULL,
    id_livro    INTEGER NOT NULL,
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_livro)   REFERENCES livros(id_livro) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metas_leitura (
    id_meta         INTEGER PRIMARY KEY AUTOINCREMENT,
    ano             INTEGER NOT NULL,
    quantidade_meta INTEGER NOT NULL CHECK (quantidade_meta > 0),
    id_usuario      INTEGER NOT NULL,
    UNIQUE (id_usuario, ano),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Curiosidades literárias exibidas na página inicial
CREATE TABLE IF NOT EXISTS curiosidades (
    id_curiosidade INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT NOT NULL,
    texto          TEXT NOT NULL
);
