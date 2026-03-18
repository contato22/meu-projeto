from flask import Flask, jsonify, request, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'erp_awq.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # Vendas / CRM
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        empresa TEXT,
        status TEXT DEFAULT 'ativo',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS oportunidades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        titulo TEXT NOT NULL,
        valor REAL DEFAULT 0,
        estagio TEXT DEFAULT 'prospeccao',
        probabilidade INTEGER DEFAULT 0,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        descricao TEXT,
        valor REAL DEFAULT 0,
        status TEXT DEFAULT 'pendente',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')

    # Financeiro
    c.execute('''CREATE TABLE IF NOT EXISTS lancamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL DEFAULT 0,
        categoria TEXT,
        status TEXT DEFAULT 'pendente',
        vencimento TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # RH / Pessoas
    c.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cargo TEXT,
        departamento TEXT,
        email TEXT,
        salario REAL DEFAULT 0,
        status TEXT DEFAULT 'ativo',
        admissao TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed data
    clientes = c.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
    if clientes == 0:
        c.executemany('INSERT INTO clientes (nome, email, telefone, empresa, status) VALUES (?,?,?,?,?)', [
            ('João Silva', 'joao@empresa.com', '(11) 99999-1111', 'Tech Solutions', 'ativo'),
            ('Maria Oliveira', 'maria@negocio.com', '(21) 98888-2222', 'Negócio Digital', 'ativo'),
            ('Carlos Souza', 'carlos@corp.com', '(31) 97777-3333', 'Corp SA', 'ativo'),
            ('Ana Lima', 'ana@startup.io', '(41) 96666-4444', 'Startup IO', 'lead'),
            ('Pedro Costa', 'pedro@indústria.com', '(51) 95555-5555', 'Indústria BR', 'inativo'),
        ])
        c.executemany('INSERT INTO oportunidades (cliente_id, titulo, valor, estagio, probabilidade) VALUES (?,?,?,?,?)', [
            (1, 'Implementação ERP', 45000, 'proposta', 70),
            (2, 'Consultoria Digital', 12000, 'negociacao', 85),
            (3, 'Licença Anual', 8500, 'fechamento', 95),
            (4, 'Projeto Piloto', 5000, 'prospeccao', 30),
        ])
        c.executemany('INSERT INTO pedidos (cliente_id, descricao, valor, status) VALUES (?,?,?,?)', [
            (1, 'Módulo de Estoque', 15000, 'aprovado'),
            (2, 'Treinamento Equipe', 3500, 'concluido'),
            (3, 'Suporte Premium', 1200, 'pendente'),
        ])
        c.executemany('INSERT INTO lancamentos (descricao, tipo, valor, categoria, status, vencimento) VALUES (?,?,?,?,?,?)', [
            ('Pagamento Cliente Tech Solutions', 'receita', 15000, 'Vendas', 'pago', '2026-03-10'),
            ('Salários Março', 'despesa', 42000, 'RH', 'pendente', '2026-03-30'),
            ('Aluguel Escritório', 'despesa', 5500, 'Infraestrutura', 'pago', '2026-03-05'),
            ('Serviços de Consultoria', 'receita', 12000, 'Serviços', 'pendente', '2026-03-25'),
            ('Licenças de Software', 'despesa', 2300, 'TI', 'pendente', '2026-03-20'),
            ('Recebimento Pedido #2', 'receita', 3500, 'Vendas', 'pago', '2026-03-12'),
            ('Marketing Digital', 'despesa', 4000, 'Marketing', 'pendente', '2026-03-28'),
        ])
        c.executemany('INSERT INTO funcionarios (nome, cargo, departamento, email, salario, status, admissao) VALUES (?,?,?,?,?,?,?)', [
            ('Ana Pereira', 'Gerente de Vendas', 'Comercial', 'ana.p@awq.com', 8500, 'ativo', '2022-03-01'),
            ('Bruno Martins', 'Dev Backend', 'TI', 'bruno@awq.com', 7200, 'ativo', '2021-06-15'),
            ('Carla Nunes', 'Analista Financeiro', 'Financeiro', 'carla@awq.com', 6800, 'ativo', '2023-01-10'),
            ('Diego Alves', 'Designer UX', 'Produto', 'diego@awq.com', 6000, 'ativo', '2022-09-20'),
            ('Elena Rocha', 'Atendimento', 'Comercial', 'elena@awq.com', 4500, 'ativo', '2024-02-05'),
            ('Fábio Torres', 'Analista RH', 'RH', 'fabio@awq.com', 5500, 'ferias', '2021-11-30'),
        ])

    conn.commit()
    conn.close()


# ─── Frontend ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route('/api/dashboard')
def dashboard():
    conn = get_db()
    c = conn.cursor()

    total_clientes = c.execute("SELECT COUNT(*) FROM clientes WHERE status='ativo'").fetchone()[0]
    total_oportunidades = c.execute("SELECT COUNT(*) FROM oportunidades").fetchone()[0]
    pipeline = c.execute("SELECT SUM(valor) FROM oportunidades").fetchone()[0] or 0
    receitas = c.execute("SELECT SUM(valor) FROM lancamentos WHERE tipo='receita' AND status='pago'").fetchone()[0] or 0
    despesas = c.execute("SELECT SUM(valor) FROM lancamentos WHERE tipo='despesa' AND status='pago'").fetchone()[0] or 0
    total_funcionarios = c.execute("SELECT COUNT(*) FROM funcionarios WHERE status='ativo'").fetchone()[0]
    pedidos_mes = c.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    ult_lancamentos = c.execute(
        "SELECT descricao, tipo, valor, status FROM lancamentos ORDER BY id DESC LIMIT 5"
    ).fetchall()

    conn.close()
    return jsonify({
        'kpis': {
            'clientes_ativos': total_clientes,
            'oportunidades': total_oportunidades,
            'pipeline': pipeline,
            'receita_paga': receitas,
            'despesa_paga': despesas,
            'saldo': receitas - despesas,
            'funcionarios': total_funcionarios,
            'pedidos': pedidos_mes,
        },
        'ultimos_lancamentos': [dict(r) for r in ult_lancamentos],
    })


# ─── Clientes ────────────────────────────────────────────────────────────────

@app.route('/api/clientes', methods=['GET'])
def list_clientes():
    conn = get_db()
    rows = conn.execute('SELECT * FROM clientes ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/clientes', methods=['POST'])
def create_cliente():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO clientes (nome, email, telefone, empresa, status) VALUES (?,?,?,?,?)',
        (data['nome'], data.get('email', ''), data.get('telefone', ''),
         data.get('empresa', ''), data.get('status', 'ativo'))
    )
    conn.commit()
    row = conn.execute('SELECT * FROM clientes WHERE id=?', (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    data = request.json
    conn = get_db()
    conn.execute(
        'UPDATE clientes SET nome=?, email=?, telefone=?, empresa=?, status=? WHERE id=?',
        (data['nome'], data.get('email', ''), data.get('telefone', ''),
         data.get('empresa', ''), data.get('status', 'ativo'), id)
    )
    conn.commit()
    row = conn.execute('SELECT * FROM clientes WHERE id=?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(row))


@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    conn = get_db()
    conn.execute('DELETE FROM clientes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── Oportunidades ───────────────────────────────────────────────────────────

@app.route('/api/oportunidades', methods=['GET'])
def list_oportunidades():
    conn = get_db()
    rows = conn.execute('''
        SELECT o.*, c.nome as cliente_nome
        FROM oportunidades o LEFT JOIN clientes c ON o.cliente_id = c.id
        ORDER BY o.id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/oportunidades', methods=['POST'])
def create_oportunidade():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO oportunidades (cliente_id, titulo, valor, estagio, probabilidade) VALUES (?,?,?,?,?)',
        (data['cliente_id'], data['titulo'], data.get('valor', 0),
         data.get('estagio', 'prospeccao'), data.get('probabilidade', 0))
    )
    conn.commit()
    row = conn.execute('SELECT o.*, c.nome as cliente_nome FROM oportunidades o LEFT JOIN clientes c ON o.cliente_id=c.id WHERE o.id=?', (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/oportunidades/<int:id>', methods=['DELETE'])
def delete_oportunidade(id):
    conn = get_db()
    conn.execute('DELETE FROM oportunidades WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── Pedidos ─────────────────────────────────────────────────────────────────

@app.route('/api/pedidos', methods=['GET'])
def list_pedidos():
    conn = get_db()
    rows = conn.execute('''
        SELECT p.*, c.nome as cliente_nome
        FROM pedidos p LEFT JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.id DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/pedidos', methods=['POST'])
def create_pedido():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO pedidos (cliente_id, descricao, valor, status) VALUES (?,?,?,?)',
        (data['cliente_id'], data['descricao'], data.get('valor', 0), data.get('status', 'pendente'))
    )
    conn.commit()
    row = conn.execute('SELECT p.*, c.nome as cliente_nome FROM pedidos p LEFT JOIN clientes c ON p.cliente_id=c.id WHERE p.id=?', (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/pedidos/<int:id>', methods=['DELETE'])
def delete_pedido(id):
    conn = get_db()
    conn.execute('DELETE FROM pedidos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── Financeiro ──────────────────────────────────────────────────────────────

@app.route('/api/lancamentos', methods=['GET'])
def list_lancamentos():
    conn = get_db()
    rows = conn.execute('SELECT * FROM lancamentos ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/lancamentos', methods=['POST'])
def create_lancamento():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO lancamentos (descricao, tipo, valor, categoria, status, vencimento) VALUES (?,?,?,?,?,?)',
        (data['descricao'], data['tipo'], data.get('valor', 0),
         data.get('categoria', ''), data.get('status', 'pendente'), data.get('vencimento', ''))
    )
    conn.commit()
    row = conn.execute('SELECT * FROM lancamentos WHERE id=?', (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/lancamentos/<int:id>', methods=['DELETE'])
def delete_lancamento(id):
    conn = get_db()
    conn.execute('DELETE FROM lancamentos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── Funcionários ────────────────────────────────────────────────────────────

@app.route('/api/funcionarios', methods=['GET'])
def list_funcionarios():
    conn = get_db()
    rows = conn.execute('SELECT * FROM funcionarios ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/funcionarios', methods=['POST'])
def create_funcionario():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO funcionarios (nome, cargo, departamento, email, salario, status, admissao) VALUES (?,?,?,?,?,?,?)',
        (data['nome'], data.get('cargo', ''), data.get('departamento', ''),
         data.get('email', ''), data.get('salario', 0),
         data.get('status', 'ativo'), data.get('admissao', ''))
    )
    conn.commit()
    row = conn.execute('SELECT * FROM funcionarios WHERE id=?', (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/funcionarios/<int:id>', methods=['PUT'])
def update_funcionario(id):
    data = request.json
    conn = get_db()
    conn.execute(
        'UPDATE funcionarios SET nome=?, cargo=?, departamento=?, email=?, salario=?, status=? WHERE id=?',
        (data['nome'], data.get('cargo', ''), data.get('departamento', ''),
         data.get('email', ''), data.get('salario', 0), data.get('status', 'ativo'), id)
    )
    conn.commit()
    row = conn.execute('SELECT * FROM funcionarios WHERE id=?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(row))


@app.route('/api/funcionarios/<int:id>', methods=['DELETE'])
def delete_funcionario(id):
    conn = get_db()
    conn.execute('DELETE FROM funcionarios WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
