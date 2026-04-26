-- DML: Insercao, atualizacao e delecao

INSERT INTO planos (nome, preco, duracao_meses) VALUES
    ('Mensal',     99.90,  1),
    ('Trimestral', 249.90, 3),
    ('Anual',      799.90, 12)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO alunos (nome, email, telefone, plano) VALUES
    ('Joao Silva',  'joao@email.com',  '86999991111', 'Mensal'),
    ('Maria Souza', 'maria@email.com', '86999992222', 'Anual')
ON CONFLICT DO NOTHING;

UPDATE alunos
SET plano = 'Anual'
WHERE nome = 'Joao Silva';

DELETE FROM alunos WHERE email = 'maria@email.com';
