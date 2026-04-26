-- DQL: Consultas, filtros, ordenacao e joins

SELECT * FROM alunos ORDER BY nome ASC;

SELECT * FROM alunos WHERE plano = 'Mensal';

SELECT * FROM alunos WHERE nome ILIKE '%silva%';

-- INNER JOIN
SELECT a.nome, a.email, pl.nome AS plano, pl.preco, pl.duracao_meses
FROM alunos a
INNER JOIN planos pl ON a.plano = pl.nome
ORDER BY pl.preco DESC;

-- LEFT JOIN
SELECT a.nome, a.plano,
       COALESCE(SUM(pg.valor), 0) AS total_pago,
       COUNT(pg.id)               AS qtd_pagamentos
FROM alunos a
LEFT JOIN pagamentos pg ON pg.aluno_id = a.id
GROUP BY a.nome, a.plano
ORDER BY a.nome;
