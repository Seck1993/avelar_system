import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .extensions import db
from .models import Usuario, Cliente, Catalogo, Mensalidade, Venda, Despesa, Ocorrencia, Configuracao, Cidade, Bairro, Funcionario, Veiculo, Contrato, Orcamento, ItemOrcamento

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

    @app.route('/service-worker.js')
    def service_worker(): return send_from_directory(app.static_folder, 'service-worker.js')
    @app.route('/offline')
    def offline(): return render_template('offline.html')

    # --- CATÁLOGO AVANÇADO ---
    @app.route('/catalogo')
    @login_required
    def catalogo():
        # Separa produtos e serviços para as abas
        produtos = Catalogo.query.filter_by(tipo='Produto').all()
        servicos = Catalogo.query.filter_by(tipo='Serviço').all()
        return render_template('catalogo.html', produtos=produtos, servicos=servicos)

    @app.route('/novo_item_catalogo', methods=['POST'])
    @login_required
    def novo_item_catalogo():
        try:
            novo = Catalogo(
                tipo=request.form['tipo'],
                item=request.form['item'],
                marca=request.form.get('marca'),
                modelo=request.form.get('modelo'),
                descricao=request.form.get('descricao'),
                unidade=request.form.get('unidade', 'un'),
                valor=float(request.form['valor']),
                custo_compra=float(request.form.get('custo_compra') or 0),
                valor_instalacao=float(request.form.get('valor_instalacao') or 0)
            )
            db.session.add(novo)
            db.session.commit()
            flash('Item adicionado ao catálogo.', 'success')
        except Exception as e:
            flash(f'Erro ao adicionar: {str(e)}', 'danger')
        return redirect(url_for('catalogo'))

    @app.route('/excluir_item_catalogo/<int:id>')
    @login_required
    def excluir_item_catalogo(id):
        try:
            db.session.delete(Catalogo.query.get(id))
            db.session.commit()
            flash('Item removido.', 'success')
        except:
            flash('Erro: Item em uso.', 'danger')
        return redirect(url_for('catalogo'))

    # --- ORÇAMENTOS ---
    @app.route('/novo_orcamento')
    @login_required
    def novo_orcamento():
        return render_template('novo_orcamento.html', 
                             clientes=Cliente.query.order_by(Cliente.nome).all(),
                             catalogo=Catalogo.query.order_by(Catalogo.item).all())

    @app.route('/salvar_orcamento', methods=['POST'])
    @login_required
    def salvar_orcamento():
        try:
            orc = Orcamento(
                cliente_id=request.form['cliente_id'],
                observacoes=request.form['observacoes'],
                valor_final=float(request.form.get('total_final', 0)),
                status='Pendente'
            )
            db.session.add(orc)
            db.session.flush()

            itens_id = request.form.getlist('itens_id[]')
            itens_qtd = request.form.getlist('itens_qtd[]')
            itens_valor = request.form.getlist('itens_valor[]')

            total_prod = 0
            total_serv = 0

            for i in range(len(itens_id)):
                cat_id = int(itens_id[i])
                qtd = float(itens_qtd[i])
                vlr = float(itens_valor[i])
                subtotal = qtd * vlr
                
                item_cat = Catalogo.query.get(cat_id)
                if item_cat.tipo == 'Produto': total_prod += subtotal
                else: total_serv += subtotal

                novo_item = ItemOrcamento(
                    orcamento_id=orc.id,
                    catalogo_id=cat_id,
                    quantidade=qtd,
                    valor_unitario=vlr,
                    subtotal=subtotal
                )
                db.session.add(novo_item)

            orc.valor_total_produtos = total_prod
            orc.valor_total_servicos = total_serv
            
            db.session.commit()
            flash('Orçamento criado com sucesso!', 'success')
            return redirect(url_for('vendas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar orçamento: {str(e)}', 'danger')
            return redirect(url_for('novo_orcamento'))

    # --- COMERCIAL / CONTRATOS ---
    @app.route('/vendas')
    @login_required
    def vendas():
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        return render_template('vendas.html', 
                             vendas=Venda.query.order_by(Venda.data.desc()).all(),
                             contratos=Contrato.query.filter_by(ativo=True).all(),
                             # Tenta buscar orçamentos, se a tabela ainda nao existir não quebra
                             orcamentos=Orcamento.query.order_by(Orcamento.data_criacao.desc()).all() if Orcamento.query.first() else [],
                             clientes=Cliente.query.order_by(Cliente.nome).all(),
                             catalogo=Catalogo.query.all())

    @app.route('/novo_contrato', methods=['POST'])
    @login_required
    def novo_contrato():
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        try:
            servico = Catalogo.query.get(request.form['servico_id'])
            desconto = float(request.form['desconto'] or 0)
            valor_final = servico.valor - desconto
            
            duracao = request.form['tipo_duracao']
            dt_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d')
            dt_fim = None
            if duracao == '12 Meses': dt_fim = dt_inicio + timedelta(days=365)
            elif duracao == '24 Meses': dt_fim = dt_inicio + timedelta(days=730)
            
            novo_c = Contrato(
                cliente_id=request.form['cliente_id'],
                servico_id=servico.id,
                data_inicio=dt_inicio,
                data_fim=dt_fim,
                tipo_duracao=duracao,
                valor_original=servico.valor,
                desconto=desconto,
                valor_final=valor_final,
                ativo=True
            )
            db.session.add(novo_c)
            db.session.commit()
            flash('Serviço vinculado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao vincular: {str(e)}', 'danger')
        return redirect(url_for('vendas'))

    @app.route('/nova_venda', methods=['POST'])
    @login_required
    def nova_venda():
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        try:
            db.session.add(Venda(
                cliente_id=request.form['cliente_id'],
                descricao=request.form['descricao'],
                valor_total=float(request.form['valor']),
                data=datetime.now()
            ))
            db.session.commit()
            flash('Venda registrada.', 'success')
        except:
            flash('Erro ao registrar venda.', 'danger')
        return redirect(url_for('vendas'))

    # --- CADASTROS GERAIS (INSERÇÃO) ---
    @app.route('/cadastros', methods=['GET', 'POST'])
    @login_required
    def cadastros():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        if request.method == 'POST':
            tipo = request.form.get('tipo_cadastro')
            try:
                if tipo == 'cidade':
                    db.session.add(Cidade(nome=request.form['nome']))
                elif tipo == 'bairro':
                    db.session.add(Bairro(nome=request.form['nome'], cidade_id=request.form['cidade_id']))
                elif tipo == 'funcionario':
                    dt_nasc = None
                    if request.form.get('data_nascimento'): dt_nasc = datetime.strptime(request.form['data_nascimento'], '%Y-%m-%d')
                    db.session.add(Funcionario(
                        nome=request.form['nome'], cargo=request.form['cargo'],
                        cpf=request.form.get('cpf'), rg=request.form.get('rg'),
                        cnh=request.form.get('cnh'), telefone=request.form.get('telefone'),
                        endereco=request.form.get('endereco'), data_nascimento=dt_nasc
                    ))
                elif tipo == 'veiculo':
                    db.session.add(Veiculo(descricao=request.form['descricao'], placa=request.form['placa']))
                elif tipo == 'cliente':
                    db.session.add(Cliente(
                        nome=request.form['nome'], bairro_id=request.form['bairro_id'],
                        endereco=request.form['endereco'], complemento=request.form.get('complemento'),
                        telefone=request.form.get('telefone'), app_monitoramento=request.form.get('app_monitoramento'),
                        ativo=True
                    ))
                db.session.commit()
                flash('Cadastrado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro: {str(e)}', 'danger')
            return redirect(url_for('cadastros'))
        return render_template('cadastros.html', cidades=Cidade.query.order_by(Cidade.nome).all(), bairros=Bairro.query.join(Cidade).order_by(Cidade.nome, Bairro.nome).all())

    # --- LISTAGENS OPERACIONAIS ---
    @app.route('/operacional/clientes')
    @login_required
    def op_clientes(): return render_template('operacional/lista_clientes.html', clientes=Cliente.query.order_by(Cliente.nome).all(), bairros=Bairro.query.all())
    @app.route('/operacional/equipe')
    @login_required
    def op_equipe(): return render_template('operacional/lista_equipe.html', funcionarios=Funcionario.query.all())
    @app.route('/operacional/frota')
    @login_required
    def op_frota(): return render_template('operacional/lista_frota.html', veiculos=Veiculo.query.all())
    @app.route('/operacional/rotas')
    @login_required
    def op_rotas(): return render_template('operacional/lista_rotas.html', bairros=Bairro.query.join(Cidade).all(), cidades=Cidade.query.all())

    @app.route('/excluir_cadastro/<tipo>/<int:id>')
    @login_required
    def excluir_cadastro(tipo, id):
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        try:
            if tipo == 'contrato':
                c = Contrato.query.get(id)
                c.ativo = False; c.data_fim = datetime.now()
            elif tipo == 'orcamento': db.session.delete(Orcamento.query.get(id))
            elif tipo == 'catalogo': db.session.delete(Catalogo.query.get(id))
            elif tipo == 'funcionario': db.session.delete(Funcionario.query.get(id))
            elif tipo == 'veiculo': db.session.delete(Veiculo.query.get(id))
            elif tipo == 'bairro': db.session.delete(Bairro.query.get(id))
            elif tipo == 'cidade': db.session.delete(Cidade.query.get(id))
            elif tipo == 'cliente': db.session.delete(Cliente.query.get(id))
            elif tipo == 'despesa': db.session.delete(Despesa.query.get(id))
            db.session.commit()
            flash('Item excluído/cancelado.', 'success')
        except:
            db.session.rollback()
            flash('Erro ao excluir.', 'danger')
        return redirect(request.referrer)

    @app.route('/editar_cadastro', methods=['POST'])
    @login_required
    def editar_cadastro():
        if current_user.cargo != 'Admin': return redirect(url_for('home'))
        tipo = request.form.get('tipo')
        id_item = request.form.get('id')
        campo1 = request.form.get('campo1')
        campo2 = request.form.get('campo2')
        try:
            if tipo == 'funcionario':
                f = Funcionario.query.get(id_item)
                f.nome = campo1; f.cargo = campo2
                if request.form.get('cpf'): f.cpf = request.form.get('cpf')
                if request.form.get('telefone'): f.telefone = request.form.get('telefone')
            elif tipo == 'veiculo':
                v = Veiculo.query.get(id_item); v.descricao = campo1; v.placa = campo2
            elif tipo == 'cliente':
                c = Cliente.query.get(id_item); c.nome = campo1; c.endereco = campo2
            elif tipo == 'bairro':
                b = Bairro.query.get(id_item); b.nome = campo1
                if request.form.get('cidade_id'): b.cidade_id = request.form.get('cidade_id')
            db.session.commit()
            flash('Editado com sucesso.', 'success')
        except:
            flash('Erro ao editar.', 'danger')
        return redirect(request.referrer)

    @app.route('/')
    @login_required
    def home():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        hoje = datetime.now()
        receita_fixa = db.session.query(func.sum(Contrato.valor_final)).filter_by(ativo=True).scalar() or 0
        receita_vendas = db.session.query(func.sum(Venda.valor_total)).filter(func.extract('month', Venda.data)==hoje.month).scalar() or 0
        despesa_mes = db.session.query(func.sum(Despesa.valor)).filter(func.extract('month', Despesa.data)==hoje.month, Despesa.tipo_operacao == 'Saida').scalar() or 0
        return render_template('index.html', now=hoje.strftime('%d/%m/%Y'), receita=receita_fixa+receita_vendas, despesa=despesa_mes, saldo=(receita_fixa+receita_vendas)-despesa_mes, receita_bairros=[], ocorrencias=Ocorrencia.query.limit(5).all())

    @app.route('/financeiro')
    @login_required
    def financeiro():
        if current_user.cargo != 'Admin': return redirect(url_for('painel_cliente'))
        filtro = request.args.get('periodo', 'mes')
        hoje = datetime.now()
        data_inicio = hoje.replace(day=1)
        lancamentos = Despesa.query.filter(Despesa.data >= data_inicio.date()).all()
        fluxo_lista = []
        total_entrada = 0; total_saida = 0
        for l in lancamentos:
            fluxo_lista.append({'id': l.id, 'data': l.data, 'tipo': l.tipo_operacao, 'categoria': l.categoria, 'descricao': l.descricao, 'valor': l.valor, 'origem': 'Lançamento', 'vinculo': '-'})
            if l.tipo_operacao == 'Entrada': total_entrada += l.valor
            else: total_saida += l.valor
        fluxo_lista.sort(key=lambda x: x['data'], reverse=True)
        return render_template('financeiro.html', fluxo=fluxo_lista, total_entrada=total_entrada, total_saida=total_saida, saldo=total_entrada-total_saida, filtro_atual=filtro, funcionarios=Funcionario.query.all(), veiculos=Veiculo.query.all())

    @app.route('/novo_lancamento', methods=['POST'])
    @login_required
    def novo_lancamento():
        vec_id = request.form.get('veiculo_id'); func_id = request.form.get('funcionario_id')
        db.session.add(Despesa(data=datetime.strptime(request.form['data'], '%Y-%m-%d'), categoria=request.form['categoria'], descricao=request.form['descricao'], valor=float(request.form['valor']), tipo_operacao=request.form.get('tipo_operacao'), tipo='Empresa', veiculo_id=int(vec_id) if vec_id else None, funcionario_id=int(func_id) if func_id else None))
        db.session.commit()
        return redirect(url_for('financeiro'))

    @app.route('/configuracoes', methods=['GET', 'POST'])
    @login_required
    def configuracoes():
        conf = Configuracao.query.first() or Configuracao()
        if request.method == 'POST':
            conf.nome_empresa = request.form['nome_empresa']
            if 'logo' in request.files and request.files['logo'].filename:
                f = request.files['logo']; fname = secure_filename("logo_sistema.jpg")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname)); conf.logo_path = f"uploads/{fname}"
            db.session.add(conf); db.session.commit()
            return redirect(url_for('configuracoes'))
        return render_template('configuracoes.html', conf=conf)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = Usuario.query.filter_by(email=request.form['email']).first()
            if user and user.check_senha(request.form['senha']): login_user(user); return redirect(url_for('home'))
            flash('Erro login', 'danger')
        return render_template('login.html')
    @app.route('/logout')
    def logout(): logout_user(); return redirect(url_for('login'))
    @app.route('/ocorrencias')
    def listar_ocorrencias(): return render_template('ocorrencias.html', ocorrencias=Ocorrencia.query.all())
    @app.route('/nova_ocorrencia', methods=['POST'])
    def nova_ocorrencia(): return redirect(url_for('listar_ocorrencias'))
    @app.route('/painel_cliente')
    def painel_cliente(): return render_template('cliente_painel.html', cliente=Cliente.query.get(current_user.cliente_id))
    @app.route('/clientes')
    def clientes(): return redirect(url_for('op_clientes'))
    @app.route('/novo_cliente')
    def novo_cliente(): return redirect(url_for('cadastros'))

    return app