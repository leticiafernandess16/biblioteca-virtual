
-- BIBLIOTECA VIRTUAL - schema.sql (SQLite)
-- Apenas a estrutura das tabelas (sem dados iniciais)
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS metas_leitura;
DROP TABLE IF EXISTS lista_leitura;
DROP TABLE IF EXISTS avaliacoes;
DROP TABLE IF EXISTS favoritos;
DROP TABLE IF EXISTS emprestimos;
DROP TABLE IF EXISTS livros;
DROP TABLE IF EXISTS generos;
DROP TABLE IF EXISTS autores;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id_usuario     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL CHECK (length(trim(nome)) >= 2),
    email          TEXT NOT NULL UNIQUE,
    senha_hash     TEXT NOT NULL,
    tipo           TEXT NOT NULL DEFAULT 'leitor'
                   CHECK (tipo IN ('leitor', 'admin')),
    data_cadastro  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE autores (
    id_autor       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL,
    nacionalidade  TEXT,
    biografia      TEXT
);

CREATE TABLE generos (
    id_genero      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL UNIQUE,
    descricao      TEXT
);

CREATE TABLE livros (
    id_livro                  INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo                    TEXT NOT NULL,
    isbn                      TEXT UNIQUE,
    ano_publicacao            INTEGER CHECK (ano_publicacao BETWEEN 1000 AND 2100),
    editora                   TEXT,
    sinopse                   TEXT,
    capa_url                  TEXT,
    classificacao_indicativa  TEXT NOT NULL DEFAULT 'Livre'
                              CHECK (classificacao_indicativa IN ('Livre','10','12','14','16','18')),
    quantidade_total          INTEGER NOT NULL DEFAULT 1 CHECK (quantidade_total >= 0),
    quantidade_disponivel     INTEGER NOT NULL DEFAULT 1 CHECK (quantidade_disponivel >= 0),
    id_autor                  INTEGER NOT NULL,
    id_genero                 INTEGER NOT NULL,
    data_cadastro             TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (quantidade_disponivel <= quantidade_total),
    FOREIGN KEY (id_autor)  REFERENCES autores (id_autor)  ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_genero) REFERENCES generos (id_genero) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_livros_titulo ON livros (titulo);
CREATE INDEX idx_livros_autor  ON livros (id_autor);
CREATE INDEX idx_livros_genero ON livros (id_genero);

CREATE TABLE emprestimos (
    id_emprestimo            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario               INTEGER NOT NULL,
    id_livro                 INTEGER NOT NULL,
    data_emprestimo          TEXT NOT NULL DEFAULT (date('now')),
    data_prevista_devolucao  TEXT NOT NULL,
    data_devolucao           TEXT,
    status                   TEXT NOT NULL DEFAULT 'ativo'
                             CHECK (status IN ('ativo', 'devolvido', 'atrasado')),
    CHECK (data_prevista_devolucao >= data_emprestimo),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro)   REFERENCES livros   (id_livro)   ON DELETE RESTRICT
);

-- impede o mesmo usuário de ter 2 empréstimos em aberto do mesmo livro
CREATE UNIQUE INDEX ux_emprestimo_em_aberto
    ON emprestimos (id_usuario, id_livro)
    WHERE status IN ('ativo', 'atrasado');

CREATE INDEX idx_emprestimos_usuario ON emprestimos (id_usuario);

CREATE TABLE favoritos (
    id_favorito  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario   INTEGER NOT NULL,
    id_livro     INTEGER NOT NULL,
    data_adicao  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro)   REFERENCES livros   (id_livro)   ON DELETE CASCADE
);

CREATE TABLE avaliacoes (
    id_avaliacao    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario      INTEGER NOT NULL,
    id_livro        INTEGER NOT NULL,
    nota            INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario      TEXT,
    data_avaliacao  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro)   REFERENCES livros   (id_livro)   ON DELETE CASCADE
);

CREATE TABLE lista_leitura (
    id_lista      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario    INTEGER NOT NULL,
    id_livro      INTEGER NOT NULL,
    status        TEXT NOT NULL DEFAULT 'quero_ler'
                  CHECK (status IN ('quero_ler', 'lido')),
    data_adicao   TEXT NOT NULL DEFAULT (datetime('now')),
    data_leitura  TEXT,
    UNIQUE (id_usuario, id_livro),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_livro)   REFERENCES livros   (id_livro)   ON DELETE CASCADE
);

CREATE TABLE metas_leitura (
    id_meta          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario       INTEGER NOT NULL,
    ano              INTEGER NOT NULL CHECK (ano BETWEEN 2000 AND 2100),
    quantidade_meta  INTEGER NOT NULL CHECK (quantidade_meta > 0),
    UNIQUE (id_usuario, ano),
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);