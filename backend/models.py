from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# -----------------------------------------------------------------------------
# TABELAS BÁSICAS / CADASTROS AUXILIARES
# -----------------------------------------------------------------------------

class Cidade(db.Model):
    __tablename__ = 'cidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), default='RS')
    bairros = db.relationship('Bairro', backref='cidade', lazy=True)

class Bairro(db.Model):
    __tablename__ = 'bairros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'))
    clientes = db.relationship('Cliente', backref='bairro_obj', lazy=True)

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)
    cpf = db.Column(db.String(20))
    rg = db.Column(db.String(20))
    cnh = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256))
    nome = db.Column(db.String(100))
    cargo = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    
    def set_senha(self, senha): 
        self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
    
    def check_senha(self, senha): 
        return check_password_hash(self.senha_hash, senha)

class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    id = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column(db.String(100), default="Avelar Security")
    cor_primaria = db.Column(db.String(20), default="#d32f2f")
    logo_path = db.Column(db.String(200), default="img/Logo.png")
    fundo_login = db.Column(db.String(200), default="")
    fundo_dashboard = db.Column(db.String(200), default="")

# -----------------------------------------------------------------------------
# TABELAS PRINCIPAIS (CLIENTES, CATÁLOGO, FINANCEIRO)
# -----------------------------------------------------------------------------

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairros.id'), nullable=True)
    endereco = db.Column(db.String(200))
    complemento = db.Column(db.String(100))
    cpf = db.Column(db.String(20))
    telefone = db.Column(db.String(30))
    app_monitoramento = db.Column(db.String(50))
    qtd_cameras = db.Column(db.Integer, default=0)
    
    # Campos antigos mantidos para compatibilidade, mas não usados na nova lógica
    valor_mensal = db.Column(db.Float, default=0.0) 
    dia_vencimento = db.Column(db.Integer, default=10)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    contratos = db.relationship('Contrato', backref='cliente', lazy=True)
    mensalidades = db.relationship('Mensalidade', backref='cliente', lazy=True)
    vendas = db.relationship('Venda', backref='cliente', lazy=True)
    orcamentos = db.relationship('Orcamento', backref='cliente', lazy=True)
    ocorrencias = db.relationship('Ocorrencia', backref='cliente', lazy=True)

class Catalogo(db.Model):
    __tablename__ = 'catalogo'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50)) # 'Serviço' ou 'Produto'
    item = db.Column(db.String(150))
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float) # Preço de Venda
    
    # Campos Avançados
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    unidade = db.Column(db.String(20), default='un')
    custo_compra = db.Column(db.Float, default=0.0)
    valor_instalacao = db.Column(db.Float, default=0.0)
    estoque_atual = db.Column(db.Integer, default=0)

class Contrato(db.Model):
    __tablename__ = 'contratos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    servico_id = db.Column(db.Integer, db.ForeignKey('catalogo.id'))
    
    data_inicio = db.Column(db.Date, default=datetime.utcnow)
    data_fim = db.Column(db.Date, nullable=True)
    tipo_duracao = db.Column(db.String(50)) # 'Mensal', 'Anual', 'Até Cancelar'
    
    valor_original = db.Column(db.Float)
    desconto = db.Column(db.Float, default=0.0)
    valor_final = db.Column(db.Float)
    ativo = db.Column(db.Boolean, default=True)
    
    servico = db.relationship('Catalogo')

# -----------------------------------------------------------------------------
# ORÇAMENTOS
# -----------------------------------------------------------------------------

class Orcamento(db.Model):
    __tablename__ = 'orcamentos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pendente')
    
    valor_total_produtos = db.Column(db.Float, default=0.0)
    valor_total_servicos = db.Column(db.Float, default=0.0)
    valor_final = db.Column(db.Float, default=0.0)
    observacoes = db.Column(db.Text)
    
    itens = db.relationship('ItemOrcamento', backref='orcamento', lazy=True, cascade="all, delete-orphan")

class ItemOrcamento(db.Model):
    __tablename__ = 'orcamento_itens'
    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('orcamentos.id'))
    catalogo_id = db.Column(db.Integer, db.ForeignKey('catalogo.id'))
    
    quantidade = db.Column(db.Float)
    valor_unitario = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    
    produto = db.relationship('Catalogo')

# -----------------------------------------------------------------------------
# FINANCEIRO E VENDAS
# -----------------------------------------------------------------------------

class Mensalidade(db.Model):
    __tablename__ = 'mensalidades'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    mes_referencia = db.Column(db.String(20))
    valor = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pendente')
    data_pagamento = db.Column(db.Date)

class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow) # Mudado para DateTime para pegar hora
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    descricao = db.Column(db.String(200))
    valor_total = db.Column(db.Float)
    forma_pagamento = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Concluído')

class Despesa(db.Model):
    __tablename__ = 'despesas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.utcnow)
    categoria = db.Column(db.String(100))
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=True)
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float, nullable=False)
    tipo_operacao = db.Column(db.String(20), default='Saida') 
    tipo = db.Column(db.String(20), default='Empresa')
    
    veiculo = db.relationship('Veiculo')
    funcionario = db.relationship('Funcionario')

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    titulo = db.Column(db.String(100)) # Adicionado para evitar erro se app.py pedir
    descricao = db.Column(db.Text)
    responsavel = db.Column(db.String(100))