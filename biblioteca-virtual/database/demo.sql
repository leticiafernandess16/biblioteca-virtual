-- Dados de demonstração (usuários 1=admin, 2=leitor, 3=ana, 4=bruno, 5=carla)
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
