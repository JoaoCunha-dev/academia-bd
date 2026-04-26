import psycopg2
import getpass
import os

# ═══════════════════════════════════════════════
#  CONFIGURACAO DO BANCO DE DADOS
#  ← ALTERE A SENHA AQUI
# ═══════════════════════════════════════════════
DB_CONFIG = {
    "host":     "localhost",
    "database": "Academia_db",
    "user":     "postgres",
    "password": "academia123",
    "port":     "5432"
}

# Usuarios do sistema (usuario: senha)
USUARIOS = {
    "admin":     "1234",
    "professor": "senha"
}


# ════════════════════════════════════════════════
#  UTILITARIOS
# ════════════════════════════════════════════════

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def linha(char="═", tam=55):
    print(char * tam)

def titulo(texto):
    limpar()
    linha()
    print(f"  {texto}")
    linha()
    print()

def pausar():
    input("\n  Pressione ENTER para continuar...")

def conectar():
    return psycopg2.connect(**DB_CONFIG)


# ════════════════════════════════════════════════
#  CRIACAO DAS TABELAS (roda na primeira vez)
# ════════════════════════════════════════════════

def criar_tabelas():
    sql = """
    CREATE TABLE IF NOT EXISTS planos (
        id             SERIAL PRIMARY KEY,
        nome           VARCHAR(50)    NOT NULL UNIQUE,
        preco          NUMERIC(10,2)  NOT NULL,
        duracao_meses  INT            NOT NULL
    );

    CREATE TABLE IF NOT EXISTS alunos (
        id             SERIAL PRIMARY KEY,
        nome           VARCHAR(100)   NOT NULL,
        email          VARCHAR(100)   UNIQUE,
        telefone       VARCHAR(20),
        plano          VARCHAR(50),
        data_cadastro  DATE           DEFAULT CURRENT_DATE
    );

    CREATE TABLE IF NOT EXISTS pagamentos (
        id              SERIAL PRIMARY KEY,
        aluno_id        INT REFERENCES alunos(id) ON DELETE CASCADE,
        plano_id        INT REFERENCES planos(id),
        data_pagamento  DATE           DEFAULT CURRENT_DATE,
        valor           NUMERIC(10,2)
    );

    INSERT INTO planos (nome, preco, duracao_meses) VALUES
        ('Mensal',      99.90,  1),
        ('Trimestral', 249.90,  3),
        ('Anual',      799.90, 12)
    ON CONFLICT (nome) DO NOTHING;
    """
    conn = conectar()
    cur  = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# ════════════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════════════

def login():
    limpar()
    linha("═")
    print("      SISTEMA DE ACADEMIA — LOGIN")
    linha("═")
    print()

    for tentativa in range(1, 4):
        print(f"  Tentativa {tentativa}/3")
        usuario = input("  Usuario : ").strip()
        senha   = getpass.getpass("  Senha   : ")

        if USUARIOS.get(usuario) == senha:
            print(f"\n  Bem-vindo, {usuario}!")
            pausar()
            return usuario

        print("  ✗ Usuario ou senha incorretos.\n")

    print("\n  Muitas tentativas. Encerrando.")
    return None


# ════════════════════════════════════════════════
#  ALUNOS — CRUD
# ════════════════════════════════════════════════

def cadastrar_aluno():
    titulo("CADASTRAR ALUNO")
    nome     = input("  Nome completo : ").strip()
    email    = input("  Email         : ").strip()
    telefone = input("  Telefone      : ").strip()
    print("  Planos: 1-Mensal  2-Trimestral  3-Anual")
    op = input("  Escolha (1/2/3): ").strip()
    plano = {"1": "Mensal", "2": "Trimestral", "3": "Anual"}.get(op, "Mensal")

    if not nome:
        print("\n  ✗ Nome e obrigatorio.")
        pausar()
        return

    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO alunos (nome, email, telefone, plano) VALUES (%s,%s,%s,%s)",
            (nome, email or None, telefone or None, plano)
        )
        conn.commit()
        cur.close(); conn.close()
        print("\n  ✓ Aluno cadastrado com sucesso!")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def listar_alunos(retornar=False):
    titulo("LISTA DE ALUNOS")
    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute(
            "SELECT id, nome, email, telefone, plano, data_cadastro "
            "FROM alunos ORDER BY nome"
        )
        rows = cur.fetchall()
        cur.close(); conn.close()

        if not rows:
            print("  Nenhum aluno cadastrado.")
            if retornar:
                return []
            pausar()
            return

        print(f"  {'ID':<5} {'Nome':<25} {'Email':<28} {'Telefone':<15} {'Plano'}")
        linha("─")
        for r in rows:
            print(f"  {r[0]:<5} {r[1]:<25} {str(r[2] or '—'):<28} "
                  f"{str(r[3] or '—'):<15} {r[4]}")
        linha("─")
        print(f"  Total: {len(rows)} aluno(s)")

        if retornar:
            return rows
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
        if retornar:
            return []
    if not retornar:
        pausar()


def atualizar_aluno():
    rows = listar_alunos(retornar=True)
    if not rows:
        pausar()
        return

    print()
    try:
        id_aluno = int(input("  ID do aluno a atualizar: ").strip())
    except ValueError:
        print("  ✗ ID invalido.")
        pausar()
        return

    ids = [r[0] for r in rows]
    if id_aluno not in ids:
        print("  ✗ ID nao encontrado.")
        pausar()
        return

    print("  (Deixe em branco para nao alterar)")
    novo_nome     = input("  Novo nome     : ").strip()
    novo_email    = input("  Novo email    : ").strip()
    novo_telefone = input("  Novo telefone : ").strip()
    print("  Planos: 1-Mensal  2-Trimestral  3-Anual  (Enter=manter)")
    op = input("  Escolha       : ").strip()
    novo_plano = {"1": "Mensal", "2": "Trimestral", "3": "Anual"}.get(op)

    try:
        conn = conectar()
        cur  = conn.cursor()
        # Busca dados atuais
        cur.execute("SELECT nome, email, telefone, plano FROM alunos WHERE id=%s", (id_aluno,))
        atual = cur.fetchone()

        nome     = novo_nome     or atual[0]
        email    = novo_email    or atual[1]
        telefone = novo_telefone or atual[2]
        plano    = novo_plano    or atual[3]

        cur.execute(
            "UPDATE alunos SET nome=%s, email=%s, telefone=%s, plano=%s WHERE id=%s",
            (nome, email, telefone, plano, id_aluno)
        )
        conn.commit()
        cur.close(); conn.close()
        print("\n  ✓ Aluno atualizado com sucesso!")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def deletar_aluno():
    rows = listar_alunos(retornar=True)
    if not rows:
        pausar()
        return

    print()
    try:
        id_aluno = int(input("  ID do aluno a deletar: ").strip())
    except ValueError:
        print("  ✗ ID invalido.")
        pausar()
        return

    ids_nomes = {r[0]: r[1] for r in rows}
    if id_aluno not in ids_nomes:
        print("  ✗ ID nao encontrado.")
        pausar()
        return

    confirma = input(f"  Deletar '{ids_nomes[id_aluno]}'? (s/n): ").strip().lower()
    if confirma != "s":
        print("  Operacao cancelada.")
        pausar()
        return

    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute("DELETE FROM alunos WHERE id=%s", (id_aluno,))
        conn.commit()
        cur.close(); conn.close()
        print("\n  ✓ Aluno deletado com sucesso!")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def buscar_aluno():
    titulo("BUSCAR ALUNO")
    print("  1. Buscar por nome")
    print("  2. Buscar por plano")
    print("  3. Buscar por email")
    op = input("\n  Opcao: ").strip()

    try:
        conn = conectar()
        cur  = conn.cursor()

        if op == "1":
            termo = input("  Parte do nome: ").strip()
            cur.execute(
                "SELECT id, nome, email, telefone, plano FROM alunos "
                "WHERE nome ILIKE %s ORDER BY nome",
                (f"%{termo}%",)
            )
        elif op == "2":
            print("  Planos: 1-Mensal  2-Trimestral  3-Anual")
            p = input("  Escolha: ").strip()
            plano = {"1": "Mensal", "2": "Trimestral", "3": "Anual"}.get(p, "Mensal")
            cur.execute(
                "SELECT id, nome, email, telefone, plano FROM alunos "
                "WHERE plano=%s ORDER BY nome",
                (plano,)
            )
        elif op == "3":
            termo = input("  Parte do email: ").strip()
            cur.execute(
                "SELECT id, nome, email, telefone, plano FROM alunos "
                "WHERE email ILIKE %s ORDER BY nome",
                (f"%{termo}%",)
            )
        else:
            print("  ✗ Opcao invalida.")
            pausar()
            return

        rows = cur.fetchall()
        cur.close(); conn.close()

        print()
        if not rows:
            print("  Nenhum resultado encontrado.")
        else:
            print(f"  {'ID':<5} {'Nome':<25} {'Email':<28} {'Telefone':<15} {'Plano'}")
            linha("─")
            for r in rows:
                print(f"  {r[0]:<5} {r[1]:<25} {str(r[2] or '—'):<28} "
                      f"{str(r[3] or '—'):<15} {r[4]}")
            linha("─")
            print(f"  {len(rows)} resultado(s) encontrado(s)")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


# ════════════════════════════════════════════════
#  PAGAMENTOS
# ════════════════════════════════════════════════

def registrar_pagamento():
    titulo("REGISTRAR PAGAMENTO")

    try:
        conn = conectar()
        cur  = conn.cursor()

        cur.execute("SELECT id, nome FROM alunos ORDER BY nome")
        alunos = cur.fetchall()
        if not alunos:
            print("  ✗ Nenhum aluno cadastrado.")
            pausar()
            return

        print("  ALUNOS DISPONIVEIS:")
        for a in alunos:
            print(f"    {a[0]}. {a[1]}")

        try:
            aluno_id = int(input("\n  ID do aluno: ").strip())
        except ValueError:
            print("  ✗ ID invalido.")
            pausar()
            return

        cur.execute("SELECT id, nome, preco FROM planos ORDER BY preco")
        planos = cur.fetchall()
        print("\n  PLANOS:")
        for p in planos:
            print(f"    {p[0]}. {p[1]} — R$ {p[2]:.2f}")

        try:
            plano_id = int(input("\n  ID do plano: ").strip())
        except ValueError:
            print("  ✗ ID invalido.")
            pausar()
            return

        try:
            valor = float(input("  Valor pago (R$): ").strip().replace(",", "."))
        except ValueError:
            print("  ✗ Valor invalido.")
            pausar()
            return

        cur.execute(
            "INSERT INTO pagamentos (aluno_id, plano_id, valor) VALUES (%s,%s,%s)",
            (aluno_id, plano_id, valor)
        )
        conn.commit()
        cur.close(); conn.close()
        print("\n  ✓ Pagamento registrado com sucesso!")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def listar_pagamentos():
    titulo("PAGAMENTOS — INNER JOIN (alunos + planos)")
    try:
        conn = conectar()
        cur  = conn.cursor()
        # ── INNER JOIN ───────────────────────────────────────────
        cur.execute("""
            SELECT pg.id,
                   a.nome        AS aluno,
                   pl.nome       AS plano,
                   pg.valor,
                   pg.data_pagamento
            FROM pagamentos pg
            INNER JOIN alunos a  ON pg.aluno_id = a.id
            INNER JOIN planos pl ON pg.plano_id  = pl.id
            ORDER BY pg.data_pagamento DESC
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()

        if not rows:
            print("  Nenhum pagamento registrado.")
        else:
            print(f"  {'ID':<5} {'Aluno':<25} {'Plano':<14} "
                  f"{'Valor':>10}  {'Data'}")
            linha("─")
            for r in rows:
                print(f"  {r[0]:<5} {r[1]:<25} {r[2]:<14} "
                      f"R${float(r[3]):>8.2f}  {r[4]}")
            linha("─")
            total = sum(float(r[3]) for r in rows)
            print(f"  Total recebido: R$ {total:.2f}")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


# ════════════════════════════════════════════════
#  RELATORIOS COM JOIN
# ════════════════════════════════════════════════

def relatorio_left_join():
    titulo("RELATORIO — LEFT JOIN (todos os alunos)")
    print("  Mostra TODOS os alunos, mesmo sem pagamento registrado.\n")
    try:
        conn = conectar()
        cur  = conn.cursor()
        # ── LEFT JOIN ────────────────────────────────────────────
        cur.execute("""
            SELECT a.nome,
                   a.plano,
                   COALESCE(SUM(pg.valor), 0)    AS total_pago,
                   COUNT(pg.id)                  AS qtd_pagamentos
            FROM alunos a
            LEFT JOIN pagamentos pg ON pg.aluno_id = a.id
            GROUP BY a.nome, a.plano
            ORDER BY a.nome
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()

        print(f"  {'Nome':<25} {'Plano':<14} {'Total Pago':>12}  {'Pagamentos'}")
        linha("─")
        for r in rows:
            pago = f"R$ {float(r[2]):.2f}"
            print(f"  {r[0]:<25} {r[1]:<14} {pago:>12}  {r[3]} pgto(s)")
        linha("─")
        print(f"  Total de alunos: {len(rows)}")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def relatorio_inner_join():
    titulo("RELATORIO — INNER JOIN (alunos com detalhe do plano)")
    print("  Mostra so alunos que tem plano correspondente na tabela planos.\n")
    try:
        conn = conectar()
        cur  = conn.cursor()
        # ── INNER JOIN ───────────────────────────────────────────
        cur.execute("""
            SELECT a.nome,
                   a.email,
                   pl.nome        AS plano,
                   pl.preco,
                   pl.duracao_meses
            FROM alunos a
            INNER JOIN planos pl ON a.plano = pl.nome
            ORDER BY pl.preco DESC, a.nome
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()

        if not rows:
            print("  Nenhum resultado.")
        else:
            print(f"  {'Nome':<25} {'Email':<28} {'Plano':<14} "
                  f"{'Preco':>9}  {'Duracao'}")
            linha("─")
            for r in rows:
                print(f"  {r[0]:<25} {str(r[1] or '—'):<28} {r[2]:<14} "
                      f"R${float(r[3]):>7.2f}  {r[4]} mes(es)")
            linha("─")
            print(f"  Total: {len(rows)} aluno(s)")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


def relatorio_filtro_ordenado():
    titulo("RELATORIO — FILTRO E ORDENACAO")
    print("  Ordenar por:")
    print("  1. Nome (A-Z)")
    print("  2. Plano")
    print("  3. Data de cadastro (mais recente)")
    op = input("\n  Opcao: ").strip()

    ordem = {
        "1": "a.nome ASC",
        "2": "a.plano ASC, a.nome ASC",
        "3": "a.data_cadastro DESC",
    }.get(op, "a.nome ASC")

    print("\n  Filtrar por plano? (Enter = todos)")
    plano_filtro = input("  Mensal / Trimestral / Anual: ").strip()

    try:
        conn = conectar()
        cur  = conn.cursor()
        sql = f"""
            SELECT a.id, a.nome, a.plano, a.data_cadastro,
                   COUNT(pg.id) AS pagamentos
            FROM alunos a
            LEFT JOIN pagamentos pg ON pg.aluno_id = a.id
            WHERE 1=1
        """
        params = []
        if plano_filtro:
            sql += " AND a.plano ILIKE %s"
            params.append(f"%{plano_filtro}%")
        sql += f" GROUP BY a.id, a.nome, a.plano, a.data_cadastro ORDER BY {ordem}"

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close(); conn.close()

        print()
        if not rows:
            print("  Nenhum resultado.")
        else:
            print(f"  {'ID':<5} {'Nome':<25} {'Plano':<14} "
                  f"{'Cadastro':<12} {'Pagamentos'}")
            linha("─")
            for r in rows:
                print(f"  {r[0]:<5} {r[1]:<25} {r[2]:<14} "
                      f"{str(r[3]):<12} {r[4]} pgto(s)")
            linha("─")
            print(f"  Total: {len(rows)} aluno(s)")
    except Exception as e:
        print(f"\n  ✗ Erro: {e}")
    pausar()


# ════════════════════════════════════════════════
#  MENUS
# ════════════════════════════════════════════════

def menu_alunos():
    while True:
        titulo("MENU — ALUNOS")
        print("  1. Cadastrar aluno")
        print("  2. Listar todos os alunos")
        print("  3. Atualizar aluno")
        print("  4. Deletar aluno")
        print("  5. Buscar aluno")
        print("  0. Voltar")
        print()
        op = input("  Opcao: ").strip()
        if   op == "1": cadastrar_aluno()
        elif op == "2": listar_alunos()
        elif op == "3": atualizar_aluno()
        elif op == "4": deletar_aluno()
        elif op == "5": buscar_aluno()
        elif op == "0": break
        else: print("  ✗ Opcao invalida."); pausar()


def menu_pagamentos():
    while True:
        titulo("MENU — PAGAMENTOS")
        print("  1. Registrar pagamento")
        print("  2. Listar pagamentos (INNER JOIN)")
        print("  0. Voltar")
        print()
        op = input("  Opcao: ").strip()
        if   op == "1": registrar_pagamento()
        elif op == "2": listar_pagamentos()
        elif op == "0": break
        else: print("  ✗ Opcao invalida."); pausar()


def menu_relatorios():
    while True:
        titulo("MENU — RELATORIOS")
        print("  1. Todos os alunos com pagamentos (LEFT JOIN)")
        print("  2. Alunos com detalhe do plano (INNER JOIN)")
        print("  3. Filtro e ordenacao personalizada")
        print("  0. Voltar")
        print()
        op = input("  Opcao: ").strip()
        if   op == "1": relatorio_left_join()
        elif op == "2": relatorio_inner_join()
        elif op == "3": relatorio_filtro_ordenado()
        elif op == "0": break
        else: print("  ✗ Opcao invalida."); pausar()


def menu_principal(usuario):
    while True:
        titulo(f"ACADEMIA PRO — Bem-vindo, {usuario}")
        print("  1. Alunos       (Cadastrar, Listar, Atualizar, Deletar, Buscar)")
        print("  2. Pagamentos   (Registrar, Listar)")
        print("  3. Relatorios   (LEFT JOIN, INNER JOIN, Filtros)")
        print("  0. Sair")
        print()
        op = input("  Opcao: ").strip()
        if   op == "1": menu_alunos()
        elif op == "2": menu_pagamentos()
        elif op == "3": menu_relatorios()
        elif op == "0":
            limpar()
            print("  Encerrando o sistema. Ate logo!\n")
            break
        else:
            print("  ✗ Opcao invalida.")
            pausar()


# ════════════════════════════════════════════════
#  INICIO
# ════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        criar_tabelas()
    except Exception as e:
        print(f"\n  ✗ Erro ao conectar ao banco: {e}")
        print("  Verifique a senha e se o PostgreSQL esta rodando.")
        input("\n  Pressione ENTER para sair...")
        exit(1)

    usuario = login()
    if usuario:
        menu_principal(usuario)
