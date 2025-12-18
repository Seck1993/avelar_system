import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .extensions import db
from .models import Usuario, Cliente, Catalogo, Mensalidade, Venda, Despesa, Ocorrencia, Configuracao, Cidade, Bairro, Funcionario, Veiculo

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave-secreta-avelar-123'
    
    # BANCO DE DADOS
    db_usuario = 'avelarsecurity'
    db_senha = '8sLP63XU!5BPRt.' 
    db_host = 'avelarsecurity.mysql.pythonanywhere-services.com'
    db_nome = 'avelarsecurity$avelar_system'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_usuario}:{db_senha}@{db_host}/{db_nome}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    @app.context_processor
    def inject_config():
        try:
            conf = Configuracao.query.first()
            return dict(sistema=conf if conf else {'nome_empresa': 'Avelar', 'cor_primaria': '#d32f2f'})
        except:
            return dict(sistema={'nome_empresa': 'Avelar', 'cor_primaria': '#d32f2f'})
    
    # --- FUNÇÃO PARA POPULAR CIDADES RS ---
    def popular_cidades_rs():
        principais = [
            "Santa Cruz do Sul", "Vera Cruz", "Rio Pardo", "Venâncio Aires", 
            "Candelária", "Passo do Sobrado", "Vale do Sol", "Lajeado", 
            "Santa Maria", "Porto Alegre", "Canoas", "Novo Hamburgo"
        ]
        if Cidade.query.count() == 0:
            for nome in principais:
                db.session.add(Cidade(nome=nome, uf='RS'))
            db.session.commit()

    with app.app_context():
        try:
            popular_cidades_rs()
        except:
            pass

    @app.route('/service-worker.js')
    def service_worker():
        return send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')

    @app.route('/offline')
    def offline(): return render_template('offline.html')

    # --- NOVA TELA: CADASTROS GERAIS (ATUALIZADO) ---
    @app.route('/cadastros', methods=['GET', 'POST'])
    @login_required
    def cadastros():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        
        # POST: CRIAÇÃO
        if request.method == 'POST':
            tipo = request.form.get('tipo_cadastro')
            
            if tipo == 'cidade':
                db.session.add(Cidade(nome=request.form['nome']))
            
            elif tipo == 'bairro':
                db.session.add(Bairro(nome=request.form['nome'], cidade_id=request.form['cidade_id']))
            
            elif tipo == 'funcionario':
                db.session.add(Funcionario(nome=request.form['nome'], cargo=request.form['cargo']))
            
            elif tipo == 'veiculo':
                db.session.add(Veiculo(descricao=request.form['descricao'], placa=request.form['placa']))
            
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('cadastros'))

        # GET: LEITURA (Incluindo inativos para gestão)
        return render_template('cadastros.html', 
                             cidades=Cidade.query.order_by(Cidade.nome).all(),
                             bairros=Bairro.query.join(Cidade).order_by(Cidade.nome, Bairro.nome).all(),
                             funcionarios=Funcionario.query.order_by(Funcionario.nome).all(), 
                             veiculos=Veiculo.query.all())

    # --- ROTAS DE EDIÇÃO E EXCLUSÃO (ESSENCIAIS PARA CORRIGIR O ERRO) ---
    @app.route('/excluir_cadastro/<tipo>/<int:id>')
    @login_required
    def excluir_cadastro(tipo, id):
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        
        try:
            if tipo == 'funcionario':
                item = Funcionario.query.get(id)
                item.ativo = not item.ativo # Toggle Ativo/Inativo
                msg = f'Funcionário {item.nome} {"ativado" if item.ativo else "desativado"}.'
                
            elif tipo == 'veiculo':
                item = Veiculo.query.get(id)
                item.ativo = not item.ativo # Toggle Ativo/Inativo
                msg = f'Veículo {item.descricao} {"ativado" if item.ativo else "desativado"}.'
                
            elif tipo == 'bairro':
                item = Bairro.query.get(id)
                db.session.delete(item) # Exclusão real
                msg = 'Rota removida com sucesso.'
                
            elif tipo == 'cidade':
                item = Cidade.query.get(id)
                db.session.delete(item) # Exclusão real
                msg = 'Cidade removida.'
            
            db.session.commit()
            flash(msg, 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao excluir: Verifique se há clientes ou registros vinculados a este item.', 'danger')

        return redirect(url_for('cadastros'))

    @app.route('/editar_cadastro', methods=['POST'])
    @login_required
    def editar_cadastro():
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        
        tipo = request.form.get('tipo')
        id_item = request.form.get('id')
        campo1 = request.form.get('campo1') # Nome / Descrição
        campo2 = request.form.get('campo2') # Cargo / Placa
        cidade_id = request.form.get('cidade_id')
        
        try:
            if tipo == 'funcionario':
                f = Funcionario.query.get(id_item)
                f.nome = campo1
                f.cargo = campo2
            
            elif tipo == 'veiculo':
                v = Veiculo.query.get(id_item)
                v.descricao = campo1
                v.placa = campo2
            
            elif tipo == 'bairro':
                b = Bairro.query.get(id_item)
                b.nome = campo1
                if cidade_id: b.cidade_id = cidade_id
                
            db.session.commit()
            flash('Alteração salva com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao editar: {str(e)}', 'danger')
            
        return redirect(url_for('cadastros'))

    # --- HOME DASHBOARD ---
    @app.route('/')
    @login_required
    def home():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        hoje = datetime.now()
        mes_atual = hoje.strftime('%m/%Y')
        
        receita_total = (db.session.query(func.sum(Mensalidade.valor)).filter_by(status='Pago', mes_referencia=mes_atual).scalar() or 0) + \
                        (db.session.query(func.sum(Venda.valor_total)).filter(func.extract('month', Venda.data)==hoje.month).scalar() or 0)

        despesa_total = db.session.query(func.sum(Despesa.valor)).filter(
            func.extract('month', Despesa.data)==hoje.month, 
            func.extract('year', Despesa.data)==hoje.year, 
            Despesa.tipo=='Empresa'
        ).scalar() or 0

        receita_por_bairro = db.session.query(Bairro.nome, func.sum(Mensalidade.valor))\
            .join(Cliente, Cliente.bairro_id == Bairro.id)\
            .join(Mensalidade, Mensalidade.cliente_id == Cliente.id)\
            .filter(Mensalidade.status=='Pago', Mensalidade.mes_referencia==mes_atual)\
            .group_by(Bairro.nome).all()

        return render_template('index.html', 
                             now=hoje.strftime('%d/%m/%Y'),
                             receita=receita_total, despesa=despesa_total, saldo=receita_total-despesa_total,
                             receita_bairros=receita_por_bairro,
                             ocorrencias=Ocorrencia.query.order_by(Ocorrencia.data.desc()).limit(5).all())

    # --- FINANCEIRO ---
    @app.route('/financeiro')
    @login_required
    def financeiro():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        return render_template('financeiro.html', 
                             despesas=Despesa.query.order_by(Despesa.data.desc()).limit(100).all(),
                             mensalidades=Mensalidade.query.limit(50).all(),
                             veiculos=Veiculo.query.filter_by(ativo=True).all(),
                             funcionarios=Funcionario.query.filter_by(ativo=True).all())

    @app.route('/nova_despesa', methods=['POST'])
    @login_required
    def nova_despesa():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        
        vec_id = request.form.get('veiculo_id')
        func_id = request.form.get('funcionario_id')

        nova = Despesa(
            data=datetime.strptime(request.form['data'], '%Y-%m-%d'),
            categoria=request.form['categoria'],
            descricao=request.form['descricao'],
            valor=float(request.form['valor']),
            tipo=request.form['tipo'],
            veiculo_id=int(vec_id) if vec_id else None,
            funcionario_id=int(func_id) if func_id else None
        )
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('financeiro'))

    @app.route('/clientes')
    @login_required
    def clientes():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        return render_template('clientes.html', clientes=Cliente.query.all())

    @app.route('/novo_cliente', methods=['GET', 'POST'])
    @login_required
    def novo_cliente():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        if request.method == 'POST':
            try:
                novo = Cliente(
                    nome=request.form['nome'],
                    bairro_id=request.form['bairro_id'],
                    endereco=request.form['endereco'],
                    complemento=request.form.get('complemento'),
                    valor_mensal=float(request.form['valor_mensal'] if request.form['valor_mensal'] else 0),
                    ativo=True
                )
                db.session.add(novo)
                db.session.commit()
                flash('Cliente cadastrado com sucesso!', 'success')
                return redirect(url_for('clientes'))
            except Exception as e:
                flash(f'Erro: {str(e)}', 'danger')
        
        return render_template('novo_cliente.html', 
                             cidades=Cidade.query.order_by(Cidade.nome).all(),
                             bairros=Bairro.query.all())

    @app.route('/configuracoes', methods=['GET', 'POST'])
    @login_required
    def configuracoes():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        conf = Configuracao.query.first() or Configuracao()
        if request.method == 'POST':
            conf.nome_empresa = request.form['nome_empresa']
            conf.cor_primaria = request.form['cor_primaria']
            if 'logo' in request.files and request.files['logo'].filename:
                file = request.files['logo']
                filename = secure_filename("logo_sistema.jpg")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conf.logo_path = f"uploads/{filename}"
            db.session.add(conf)
            db.session.commit()
            return redirect(url_for('configuracoes'))
        return render_template('configuracoes.html', conf=conf)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = Usuario.query.filter_by(email=request.form['email']).first()
            if user and user.check_senha(request.form['senha']):
                login_user(user)
                return redirect(url_for('home')) if user.cargo == 'Admin' else redirect(url_for('painel_cliente'))
            flash('Erro no login', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/catalogo')
    @login_required
    def catalogo(): return render_template('catalogo.html', itens=Catalogo.query.all())

    @app.route('/novo_item', methods=['GET', 'POST'])
    @login_required
    def novo_item():
        if request.method == 'POST':
            db.session.add(Catalogo(tipo=request.form['tipo'], item=request.form['nome'], descricao=request.form['descricao'], valor=float(request.form['preco'])))
            db.session.commit()
            return redirect(url_for('catalogo'))
        return render_template('novo_item.html')

    @app.route('/vendas')
    @login_required
    def vendas(): return render_template('vendas.html', vendas=Venda.query.all())

    @app.route('/nova_venda', methods=['GET', 'POST'])
    @login_required
    def nova_venda():
        if request.method == 'POST': return redirect(url_for('vendas'))
        return render_template('nova_venda.html', clientes=Cliente.query.all(), produtos=Catalogo.query.all())

    @app.route('/ocorrencias')
    @login_required
    def listar_ocorrencias(): return render_template('ocorrencias.html', ocorrencias=Ocorrencia.query.order_by(Ocorrencia.data.desc()).all())

    @app.route('/nova_ocorrencia', methods=['GET', 'POST'])
    @login_required
    def nova_ocorrencia():
        if request.method == 'POST': return redirect(url_for('listar_ocorrencias'))
        return render_template('nova_ocorrencia.html', clientes=Cliente.query.all())

    @app.route('/painel_cliente')
    @login_required
    def painel_cliente():
        if current_user.cargo == 'Admin': return redirect(url_for('home'))
        if not current_user.cliente_id: return "Erro: Conta não vinculada", 403
        cli = Cliente.query.get(current_user.cliente_id)
        return render_template('cliente_painel.html', cliente=cli, mensalidades=Mensalidade.query.filter_by(cliente_id=cli.id).all())

    return app