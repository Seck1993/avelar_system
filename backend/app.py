import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename # Para salvar imagens
from .extensions import db
from .models import Usuario, Cliente, Catalogo, Mensalidade, Venda, Despesa, Ocorrencia, Configuracao

def create_app():
    app = Flask(__name__)
    
    # --- CONFIGURAÇÃO ---
    app.config['SECRET_KEY'] = 'chave-secreta-avelar-123'
    
    # BANCO DE DADOS
    db_usuario = 'avelarsecurity'
    db_senha = '8sLP63XU!5BPRt.' 
    db_host = 'avelarsecurity.mysql.pythonanywhere-services.com'
    db_nome = 'avelarsecurity$avelar_system'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_usuario}:{db_senha}@{db_host}/{db_nome}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 299

    # PASTA PARA SALVAR UPLOADS (Imagens de fundo)
    basedir = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Cria a pasta se não existir
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    db.init_app(app)
    
    # LOGIN
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message = "Por favor, faça login para acessar."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # --- INJETOR DE CONFIGURAÇÃO (DISPONÍVEL EM TODAS AS TELAS) ---
    @app.context_processor
    def inject_config():
        # Pega a configuração do banco, se não existir, cria uma padrão
        conf = Configuracao.query.first()
        if not conf:
            return dict(sistema={'nome_empresa': 'Avelar Security', 'cor_primaria': '#d32f2f'})
        return dict(sistema=conf)

    # --- CRIAÇÃO INICIAL ---
    with app.app_context():
        pass

    # --- ROTA DE CONFIGURAÇÕES ---
    @app.route('/configuracoes', methods=['GET', 'POST'])
    @login_required
    def configuracoes():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        
        conf = Configuracao.query.first()
        if not conf:
            conf = Configuracao()
            db.session.add(conf)
            db.session.commit()

        if request.method == 'POST':
            conf.nome_empresa = request.form['nome_empresa']
            conf.cor_primaria = request.form['cor_primaria']

            # Função para salvar imagens
            def salvar_imagem(file_input, nome_arquivo):
                file = request.files[file_input]
                if file and file.filename != '':
                    filename = secure_filename(nome_arquivo + ".jpg") # Força extensão JPG
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return f"uploads/{filename}"
                return None

            # Uploads
            if 'logo' in request.files:
                path = salvar_imagem('logo', 'logo_sistema')
                if path: conf.logo_path = path
            
            if 'fundo_login' in request.files:
                path = salvar_imagem('fundo_login', 'bg_login')
                if path: conf.fundo_login = path

            if 'fundo_dashboard' in request.files:
                path = salvar_imagem('fundo_dashboard', 'bg_dashboard')
                if path: conf.fundo_dashboard = path

            db.session.commit()
            flash('Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('configuracoes'))

        return render_template('configuracoes.html', conf=conf)

    # --- ROTAS DE AUTENTICAÇÃO ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']
            user = Usuario.query.filter_by(email=email).first()
            if user and user.check_senha(senha):
                login_user(user)
                return redirect(url_for('home')) if user.cargo == 'Admin' else redirect(url_for('painel_cliente'))
            else:
                flash('Usuário ou senha incorretos.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # --- DASHBOARD ---
    @app.route('/')
    @login_required
    def home():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        
        receita = (db.session.query(func.sum(Mensalidade.valor)).filter_by(status='Pago').scalar() or 0) + \
                  (db.session.query(func.sum(Venda.valor_total)).scalar() or 0)
        despesa = (db.session.query(func.sum(Despesa.valor)).filter_by(tipo='Empresa').scalar() or 0) + \
                  (db.session.query(func.sum(Despesa.valor)).filter_by(tipo='Pessoal').scalar() or 0)
        
        return render_template('index.html', 
                             now=datetime.now().strftime('%d/%m/%Y'),
                             receita=receita, despesa=despesa, saldo=receita-despesa,
                             total_clientes=Cliente.query.filter_by(ativo=True).count(),
                             ocorrencias=Ocorrencia.query.order_by(Ocorrencia.data.desc()).limit(5).all())

    # --- ROTAS RESTAURADAS (CRUCIAIS PARA CORRIGIR O ERRO 500) ---

    @app.route('/clientes')
    @login_required
    def clientes():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        lista_clientes = Cliente.query.all()
        return render_template('clientes.html', clientes=lista_clientes)

    @app.route('/catalogo')
    @login_required
    def catalogo():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        itens = Catalogo.query.all()
        return render_template('catalogo.html', itens=itens)

    @app.route('/financeiro')
    @login_required
    def financeiro():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        mensalidades = Mensalidade.query.all()
        despesas = Despesa.query.all()
        return render_template('financeiro.html', mensalidades=mensalidades, despesas=despesas)

    @app.route('/vendas')
    @login_required
    def vendas():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        vendas_realizadas = Venda.query.all()
        return render_template('vendas.html', vendas=vendas_realizadas)
    
    @app.route('/painel_cliente')
    @login_required
    def painel_cliente():
        # Rota para quem não é Admin visualizar suas faturas
        if current_user.cargo == 'Admin': return redirect(url_for('home'))
        
        mensalidades = []
        if current_user.cliente_id:
             mensalidades = Mensalidade.query.filter_by(cliente_id=current_user.cliente_id).all()
             
        return render_template('painel_cliente.html', mensalidades=mensalidades)

    return app