import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from .extensions import db
from .models import Usuario, Cliente, Catalogo, Mensalidade, Venda, Despesa, Ocorrencia

def create_app():
    app = Flask(__name__)

    # Configuração
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        db.create_all()
        # Seeding do Catálogo (Se vazio)
        if not Catalogo.query.first():
            items = [
                ('Serviço', 'Monitoramento 24h', 'Acesso via App + Ronda Virtual', 100.00),
                ('Serviço', 'Ronda Presencial', 'Ronda física no local', 65.00),
                ('Produto', 'DVR 4 Canais', 'Intelbras HD 1T', 39.90),
                ('Produto', 'Câmera Wi-Fi', 'Modelo Interno/Externo', 19.90),
                ('Serviço', 'Instalação Kit 4 Câmeras', 'Mão de obra + Configuração', 450.00)
            ]
            for tipo, item, desc, val in items:
                db.session.add(Catalogo(tipo=tipo, item=item, descricao=desc, valor=val))
            db.session.commit()

    # --- ROTA HOME ---
    @app.route('/')
    def home():
        now = datetime.now().strftime('%d/%m/%Y')
        
        # Totais para o Dashboard
        receita_mensalidades = db.session.query(func.sum(Mensalidade.valor)).filter_by(status='Pago').scalar() or 0
        receita_vendas = db.session.query(func.sum(Venda.valor_total)).scalar() or 0
        receita_total = receita_mensalidades + receita_vendas
        
        despesa_empresa = db.session.query(func.sum(Despesa.valor)).filter_by(tipo='Empresa').scalar() or 0
        despesa_pessoal = db.session.query(func.sum(Despesa.valor)).filter_by(tipo='Pessoal').scalar() or 0
        
        saldo = receita_total - (despesa_empresa + despesa_pessoal)
        total_clientes = Cliente.query.filter_by(ativo=True).count()
        
        ultimas_ocorrencias = Ocorrencia.query.order_by(Ocorrencia.data.desc()).limit(5).all()

        return render_template('index.html', 
                             now=now,
                             receita=receita_total,
                             despesa=despesa_empresa,
                             pessoal=despesa_pessoal, # Passando pessoal para o template
                             saldo=saldo,
                             total_clientes=total_clientes,
                             ocorrencias=ultimas_ocorrencias)

    # --- ROTA CLIENTES ---
    @app.route('/clientes')
    def clientes():
        bairro = request.args.get('bairro')
        query = Cliente.query
        if bairro:
            query = query.filter_by(bairro=bairro)
        return render_template('clientes/lista.html', clientes=query.all())

    @app.route('/cliente/novo', methods=['GET', 'POST'])
    def novo_cliente():
        if request.method == 'POST':
            novo = Cliente(
                nome=request.form['nome'],
                bairro=request.form['bairro'],
                endereco=request.form['endereco'],
                telefone=request.form['telefone'],
                valor_mensal=float(request.form['valor_mensal'].replace(',','.') or 0),
                app_monitoramento=request.form.get('app'),
                qtd_cameras=int(request.form.get('qtd_cameras') or 0)
            )
            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('clientes'))
        return render_template('clientes/novo.html')

    # --- ROTA VENDAS ---
    @app.route('/vendas', methods=['GET', 'POST'])
    def vendas():
        if request.method == 'POST':
            nova_venda = Venda(
                cliente_id=int(request.form['cliente_id']),
                descricao=request.form['descricao'],
                valor_total=float(request.form['valor'].replace(',','.')),
                forma_pagamento=request.form['pagamento'],
                data=datetime.strptime(request.form['data'], '%Y-%m-%d')
            )
            db.session.add(nova_venda)
            db.session.commit()
            return redirect(url_for('vendas'))
            
        vendas_lista = Venda.query.order_by(Venda.data.desc()).all()
        clientes_lista = Cliente.query.all()
        return render_template('vendas/index.html', vendas=vendas_lista, clientes=clientes_lista)

    # --- ROTA CATALOGO ---
    @app.route('/catalogo')
    def catalogo():
        itens = Catalogo.query.all()
        return render_template('catalogo/index.html', itens=itens)

    # --- ROTA FINANCEIRO ---
    @app.route('/financeiro', methods=['GET', 'POST'])
    def financeiro():
        if request.method == 'POST':
            nova = Despesa(
                data=datetime.strptime(request.form['data'], '%Y-%m-%d'),
                categoria=request.form['categoria'],
                descricao=request.form['descricao'],
                valor=float(request.form['valor'].replace(',','.')),
                tipo=request.form['tipo']
            )
            db.session.add(nova)
            db.session.commit()
            return redirect(url_for('financeiro'))
            
        despesas = Despesa.query.order_by(Despesa.data.desc()).all()
        return render_template('financeiro/index.html', despesas=despesas)

    # --- ROTA OCORRÊNCIAS (RESTAURADA) ---
    @app.route('/ocorrencias', methods=['GET', 'POST'])
    def listar_ocorrencias():
        if request.method == 'POST':
            nova = Ocorrencia(
                cliente_id=int(request.form['cliente_id']),
                descricao=request.form['descricao'],
                responsavel=request.form['responsavel'],
                data=datetime.strptime(request.form['data'], '%Y-%m-%dT%H:%M')
            )
            db.session.add(nova)
            db.session.commit()
            return redirect(url_for('listar_ocorrencias'))

        lista = Ocorrencia.query.order_by(Ocorrencia.data.desc()).all()
        clientes = Cliente.query.all()
        return render_template('ocorrencias/lista.html', ocorrencias=lista, clientes=clientes)

    return app