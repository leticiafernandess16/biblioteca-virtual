-- Dados iniciais da Biblioteca Lírio (exemplos para demonstração escolar).
-- Execute DEPOIS do schema.sql. Contas: admin@biblioteca.com/admin123, leitor@biblioteca.com/leitor123,
-- ana@, bruno@ e carla@biblioteca.com/demo123 (senhas guardadas com hash).

-- ===== Gêneros, autores, livros e curiosidades =====
INSERT INTO generos (nome, descricao) VALUES
 ('Romance','Histórias de amor, laços e sentimentos'),
 ('Fantasia','Mundos mágicos e criaturas fantásticas'),
 ('Ficção científica','Ciência e tecnologia imaginadas'),
 ('Suspense','Tensão, segredos e reviravoltas'),
 ('Mistério','Enigmas e investigações'),
 ('Terror','Medo, sombras e o sobrenatural'),
 ('Aventura','Jornadas e descobertas'),
 ('Literatura clássica','Obras consagradas ao longo do tempo'),
 ('Drama','Conflitos humanos e emoções profundas'),
 ('Desenvolvimento pessoal','Hábitos, mentalidade e crescimento');

INSERT INTO autores (nome, nacionalidade, biografia) VALUES
 ('Machado de Assis','Brasileira','Um dos maiores escritores brasileiros e primeiro presidente da Academia Brasileira de Letras.'),
 ('Jane Austen','Britânica','Romancista inglesa conhecida pelas críticas sociais bem-humoradas.'),
 ('J. R. R. Tolkien','Britânica','Filólogo e autor de O Hobbit e O Senhor dos Anéis.'),
 ('Isaac Asimov','Russo-americana','Autor de ficção científica e divulgação científica.'),
 ('Agatha Christie','Britânica','Autora de romances policiais, criadora de Hercule Poirot.'),
 ('Clarice Lispector','Brasileira','Escritora de prosa introspectiva e inovadora.'),
 ('Júlio Verne','Francesa','Pioneiro da ficção científica de aventura.'),
 ('George Orwell','Britânica','Escritor e jornalista, autor de sátiras e distopias políticas.'),
 ('Bram Stoker','Irlandesa','Autor do clássico de terror Drácula.'),
 ('Mary Shelley','Britânica','Autora de Frankenstein.'),
 ('Stephen King','Americana','Um dos mais populares autores de terror e suspense.'),
 ('Arthur Conan Doyle','Britânica','Criador do detetive Sherlock Holmes.'),
 ('Dan Brown','Americana','Autor de thrillers de enigmas e símbolos.'),
 ('Paula Hawkins','Britânica','Autora de thrillers psicológicos.'),
 ('J. K. Rowling','Britânica','Autora da série Harry Potter.'),
 ('Antoine de Saint-Exupéry','Francesa','Escritor e aviador, autor de O Pequeno Príncipe.'),
 ('James Clear','Americana','Escritor sobre hábitos e melhoria contínua.'),
 ('Charles Duhigg','Americana','Jornalista e autor sobre ciência dos hábitos.'),
 ('Carol Dweck','Americana','Psicóloga conhecida pelos estudos sobre mentalidade.'),
 ('Suzanne Collins','Americana','Autora da trilogia Jogos Vorazes.'),
 ('John Green','Americana','Autor de romances para jovens leitores.'),
 ('Jorge Amado','Brasileira','Um dos escritores brasileiros mais lidos e traduzidos.'),
 ('Herman Melville','Americana','Autor de Moby Dick.');

INSERT INTO livros (titulo, ano_publicacao, editora, quantidade_total, quantidade_disponivel, classificacao_indicativa, sinopse, id_autor, id_genero) VALUES
 ('Dom Casmurro',1899,'Penguin-Companhia',3,3,'Livre','Bentinho narra a vida ao lado de Capitu e a dúvida que o consome sobre uma possível traição.',1,8),
 ('Memórias Póstumas de Brás Cubas',1881,'Penguin-Companhia',2,2,'Livre','Um defunto autor conta a própria vida com ironia e humor sombrio.',1,8),
 ('Orgulho e Preconceito',1813,'Martin Claret',3,3,'Livre','Elizabeth Bennet enfrenta convenções sociais e o orgulhoso Sr. Darcy.',2,1),
 ('Razão e Sensibilidade',1811,'Martin Claret',2,2,'Livre','As irmãs Dashwood buscam o amor entre a razão e a emoção.',2,1),
 ('O Hobbit',1937,'HarperCollins',4,4,'10 anos','Bilbo Bolseiro parte numa jornada inesperada com treze anões e um mago.',3,2),
 ('A Sociedade do Anel',1954,'Martins Fontes',3,3,'12 anos','Frodo recebe a missão de destruir o Um Anel e sair da Terra-média.',3,2),
 ('Eu, Robô',1950,'Aleph',2,2,'12 anos','Contos que exploram os dilemas das Três Leis da Robótica.',4,3),
 ('Fundação',1951,'Aleph',3,3,'12 anos','Um matemático tenta salvar o conhecimento durante a queda de um império galáctico.',4,3),
 ('Assassinato no Expresso do Oriente',1934,'HarperCollins',2,2,'14 anos','Hercule Poirot investiga um crime em um trem parado pela neve.',5,5),
 ('E Não Sobrou Nenhum',1939,'HarperCollins',2,2,'14 anos','Dez desconhecidos são convidados a uma ilha e passam a morrer um a um.',5,5),
 ('A Hora da Estrela',1977,'Rocco',2,2,'14 anos','A história de Macabéa, uma datilógrafa pobre e solitária no Rio de Janeiro.',6,9),
 ('Vinte Mil Léguas Submarinas',1870,'Zahar',2,2,'Livre','O capitão Nemo leva seus passageiros em uma viagem a bordo do Nautilus.',7,7),
 ('Viagem ao Centro da Terra',1864,'Zahar',2,2,'Livre','Um professor e seu sobrinho descem por um vulcão rumo ao interior do planeta.',7,7),
 ('1984',1949,'Companhia das Letras',3,3,'16 anos','Winston vive sob um Estado que vigia e controla cada pensamento.',8,3),
 ('A Revolução dos Bichos',1945,'Companhia das Letras',3,3,'12 anos','Os animais expulsam o fazendeiro, mas a nova ordem se corrompe.',8,8),
 ('Drácula',1897,'Penguin-Companhia',2,2,'14 anos','O conde Drácula viaja à Inglaterra e é perseguido por um grupo de aliados.',9,6),
 ('Frankenstein',1818,'Penguin-Companhia',2,2,'14 anos','Um cientista dá vida a uma criatura e enfrenta as consequências.',10,6),
 ('O Iluminado',1977,'Suma',2,2,'16 anos','Uma família passa o inverno em um hotel isolado e assombrado.',11,6),
 ('Um Estudo em Vermelho',1887,'Zahar',2,2,'12 anos','Sherlock Holmes e Watson se conhecem e resolvem um assassinato misterioso.',12,5),
 ('O Código Da Vinci',2003,'Arqueiro',3,3,'14 anos','Um simbologista segue pistas ligadas a segredos históricos e religiosos.',13,4),
 ('A Garota no Trem',2015,'Record',2,2,'16 anos','Rachel observa um casal da janela do trem e se envolve num desaparecimento.',14,4),
 ('Harry Potter e a Pedra Filosofal',1997,'Rocco',4,4,'10 anos','Harry descobre que é bruxo e entra na Escola de Magia de Hogwarts.',15,2),
 ('O Pequeno Príncipe',1943,'Agir',4,4,'Livre','Um piloto no deserto conhece um príncipe vindo de outro planeta.',16,2),
 ('Hábitos Atômicos',2018,'Alta Life',3,3,'Livre','Pequenas mudanças diárias que, somadas, geram grandes resultados.',17,10),
 ('O Poder do Hábito',2012,'Objetiva',2,2,'Livre','Como os hábitos funcionam e como é possível transformá-los.',18,10),
 ('Mindset',2006,'Objetiva',2,2,'Livre','A diferença entre mentalidade fixa e mentalidade de crescimento.',19,10),
 ('Jogos Vorazes',2008,'Rocco',3,3,'14 anos','Katniss participa de um jogo mortal transmitido para todo o país.',20,7),
 ('A Culpa é das Estrelas',2012,'Intrínseca',3,3,'14 anos','Hazel e Gus se conhecem em um grupo de apoio e vivem um amor intenso.',21,1),
 ('Capitães da Areia',1937,'Companhia das Letras',2,2,'14 anos','Meninos de rua de Salvador lutam para sobreviver juntos.',22,9),
 ('Moby Dick',1851,'Penguin-Companhia',2,2,'12 anos','O capitão Ahab persegue obsessivamente a baleia branca.',23,7);

INSERT INTO curiosidades (titulo, texto) VALUES
 ('A origem da palavra biblioteca','Biblioteca vem do grego: biblíon significa livro e théke significa depósito ou caixa.'),
 ('Machado de Assis e a Academia','Machado de Assis foi o primeiro presidente da Academia Brasileira de Letras, fundada em 1897.'),
 ('O significado das léguas','Nas Vinte Mil Léguas Submarinas, as léguas se referem à distância percorrida pelo Nautilus, e não à profundidade.'),
 ('As Três Leis da Robótica','Isaac Asimov formulou as Três Leis da Robótica, que influenciaram a ficção científica e debates reais sobre tecnologia.'),
 ('Uma autora muito jovem','Mary Shelley começou a escrever Frankenstein aos 18 anos.'),
 ('Línguas inventadas','Tolkien criou línguas como o quenya e o sindarin antes mesmo de concluir suas histórias da Terra-média.'),
 ('Um clássico traduzido no mundo todo','O Pequeno Príncipe está entre os livros mais traduzidos da história.'),
 ('Big Brother','A expressão Big Brother ganhou popularidade a partir do romance 1984, de George Orwell.'),
 ('A dúvida de Capitu','Há mais de cem anos leitores debatem se Capitu realmente traiu Bentinho em Dom Casmurro.'),
 ('Clarice nasceu na Ucrânia','Clarice Lispector nasceu na Ucrânia e chegou ao Brasil ainda bebê.');

-- ===== Usuários (1=admin, 2=leitor, 3=ana, 4=bruno, 5=carla) =====
INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES
 ('Administrador','admin@biblioteca.com','scrypt:32768:8:1$60m06tMD3xtLJzpB$d1b6fceb8db25795eae2753a5d878867dfa6414d0efdbb539418eb5927cf7f760e0b2ee6be994fcbaf2c2b0b111ccd99630d492554fce45b85b0965b3322fa30','admin'),
 ('Leitor Demo','leitor@biblioteca.com','scrypt:32768:8:1$uOeuipdqNofrILm4$02ce4a84ded41e49b59b962f81ff08bb884f3def8072719f7c6df8ccb4be1a841b11c589c5b09a1488e774632f85d8c36c2e4e8bce0ffd5ff06f216f04fd330b','leitor'),
 ('Ana Souza','ana@biblioteca.com','scrypt:32768:8:1$OYkq2IFwC6TfBDFV$b26f3574c326f5b707d0dc19442311fe177931c3e47c469fbcaa60e5015958b9c4c8e35967fe2a227aa593f64784cc841acd95c9a714b181f0cdcf63a3825586','leitor'),
 ('Bruno Lima','bruno@biblioteca.com','scrypt:32768:8:1$LUlLdsNvDW4P4X2o$0937529479ec4ec8e71d7d25d34a80e096ca7d02a0ff349c14a75ea152a173b923a4d89fe25a7e3228b9d5db9dc65c64cf3eb55732a617cf4d4882c5a90d4063','leitor'),
 ('Carla Dias','carla@biblioteca.com','scrypt:32768:8:1$18pSAYyB8RGmkcPF$38f5cc810ecdc4e02d910252752d9b837487fe0b69bf01ba34247c4a89c3cc5c1281c49039c96f39504529800331112eac27b862f299b11fa410d4c0fe0d2af2','leitor');

-- ===== Empréstimos, avaliações, favoritos, lista de leitura e metas =====
INSERT INTO emprestimos (data_emprestimo, data_prevista_devolucao, data_devolucao, status, id_usuario, id_livro) VALUES
 (date('now','-40 days'), date('now','-26 days'), date('now','-28 days'), 'devolvido', 2, 5),
 (date('now','-30 days'), date('now','-16 days'), date('now','-18 days'), 'devolvido', 3, 22),
 (date('now','-25 days'), date('now','-11 days'), date('now','-12 days'), 'devolvido', 4, 14),
 (date('now','-20 days'), date('now','-6 days'),  date('now','-8 days'),  'devolvido', 5, 3),
 (date('now','-18 days'), date('now','-4 days'),  date('now','-6 days'),  'devolvido', 3, 24),
 (date('now','-16 days'), date('now','-2 days'),  NULL, 'ativo', 4, 22),
 (date('now','-10 days'), date('now','+4 days'),  NULL, 'ativo', 2, 14),
 (date('now','-6 days'),  date('now','+8 days'),  NULL, 'ativo', 5, 1),
 (date('now','-3 days'),  date('now','+11 days'), NULL, 'ativo', 3, 9),
 (date('now','-2 days'),  date('now','+12 days'), NULL, 'ativo', 2, 24);

INSERT INTO avaliacoes (nota, comentario, id_usuario, id_livro) VALUES
 (5,'Uma aventura inesquecível, li em poucos dias.',2,5),
 (5,'Mágico do começo ao fim.',3,22),
 (4,'Assustadoramente atual.',4,14),
 (5,'Elizabeth é uma personagem incrível.',5,3),
 (4,'Mudou minha rotina de estudos.',3,24),
 (5,'Clássico absoluto!',2,1),
 (4,'Final surpreendente.',4,10),
 (3,'Bom, mas esperava mais.',5,20),
 (5,'Leitura emocionante.',3,28),
 (4,'Muito bem escrito.',2,15),
 (5,'Não consegui parar de ler.',4,27),
 (4,'Poético e profundo.',5,23),
 (5,'Mistério perfeito.',3,9),
 (4,'Boa história de terror.',2,16),
 (3,'Interessante, porém lento.',4,30),
 (5,'Ótimo para iniciantes em fantasia.',5,5),
 (4,'Conceitos práticos e simples.',2,24),
 (5,'Ficção científica inteligente.',3,8);

INSERT INTO favoritos (id_usuario, id_livro) VALUES (2,5),(2,14),(2,22),(3,3),(3,9),(3,28),(4,27),(4,16),(5,1),(5,23);

INSERT INTO lista_leitura (status, data_leitura, id_usuario, id_livro) VALUES
 ('lido', date('now','-8 days'), 2, 5),
 ('lido', date('now','-30 days'), 2, 1),
 ('quero_ler', NULL, 2, 6),
 ('quero_ler', NULL, 2, 8),
 ('lido', date('now','-6 days'), 3, 24),
 ('quero_ler', NULL, 3, 10),
 ('quero_ler', NULL, 4, 18);

INSERT INTO metas_leitura (ano, quantidade_meta, id_usuario) VALUES
 (CAST(strftime('%Y','now') AS INTEGER), 12, 2),
 (CAST(strftime('%Y','now') AS INTEGER), 6, 3);

-- Ajusta a disponibilidade conforme os empréstimos em aberto
UPDATE livros SET quantidade_disponivel = quantidade_total -
  (SELECT COUNT(*) FROM emprestimos e WHERE e.id_livro = livros.id_livro AND e.status IN ('ativo','atrasado'));