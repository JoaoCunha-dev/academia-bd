# Sistema de Gerenciamento de Academia

## Descricao
Sistema para gerenciar alunos de uma academia.
Permite cadastrar, listar, atualizar, deletar e buscar alunos,
alem de registrar pagamentos e gerar relatorios com JOIN.

## Tecnologias
- Python 3.14
- PostgreSQL 18
- psycopg2-binary
- Tkinter
- pgAdmin 4

## Como Executar

1. Instalar dependencia:
pip install psycopg2-binary

2. Criar o banco no pgAdmin 4:
- Criar banco: Academia_db
- Executar: ddl/criar_tabelas.sql
- Executar: dml/dados.sql

3. Configurar senha em src/sistema_academia.py:
"password": "SUA_SENHA"

4. Rodar sistema console:
python src/sistema_academia.py

5. Rodar interface grafica:
python src/interface_academia.py

## Login
- Usuario: admin | Senha: 1234
- Usuario: professor | Senha: senha

## Prints
(adicione os prints aqui)

## Video
(adicione o link do video aqui)
