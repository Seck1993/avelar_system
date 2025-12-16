from datetime import datetime
from .extensions import db

# --- ACESSO ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100))

# --- GESTÃO DE PREÇOS (Substitui planilha Tabela de Preço) ---
class Catalogo(db.Model):
    __tablename__ = 'catalogo'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50)) # Produto ou Serviço
    item = db.Column(db.String(150), nullable=False) # Ex: DVR 4 Canais, Câmera Wifi
    descricao = db.Column(db.String(200)) # Detalhes técnicos
    valor = db.Column(db.Float, nullable=False)

# --- CLIENTES & CONTRATOS (Substitui Cerro Alegre, Joao Alves e Ronda Virtual) ---
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(200))
    bairro = db.Column(db.String(100)) 
    cpf = db.Column(db.String(20))
    telefone = db.Column(db.String(30))
    
    # Dados do Contrato (Ronda Virtual)
    app_monitoramento = db.Column(db.String(50)) # ISIC Lite, Mibo, Intelbras
    qtd_cameras = db.Column(db.Integer, default=0)
    login_app = db.Column(db.String(100)) # Para facilitar suporte
    senha_app = db.Column(db.String(100))
    
    # Financeiro Recorrente
    valor_mensal = db.Column(db.Float, default=0.0)
    dia_vencimento = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)
    
    mensalidades = db.relationship('Mensalidade', backref='cliente', lazy=True)
    vendas = db.relationship('Venda', backref='cliente', lazy=True)
    ocorrencias = db.relationship('Ocorrencia', backref='cliente', lazy=True)

# --- FINANCEIRO (Vendas Avulsas e Mensalidades) ---
class Mensalidade(db.Model):
    __tablename__ = 'mensalidades'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    mes_referencia = db.Column(db.String(20))
    valor = db.Column(db.Float)
    status = db.Column(db.String(20), default='Pendente') # Pago, Pendente
    data_pagamento = db.Column(db.Date)

class Venda(db.Model): # Substitui planilha Vendas (Instalações)
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    descricao = db.Column(db.String(200)) # Ex: Instalação Kit 4 Câmeras
    valor_total = db.Column(db.Float)
    forma_pagamento = db.Column(db.String(50)) # 3x no Cartão, À vista
    status = db.Column(db.String(20), default='Concluído')

# --- DESPESAS (Substitui Gasto Diario/Empresa/Pessoal) ---
class Despesa(db.Model):
    __tablename__ = 'despesas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.utcnow)
    categoria = db.Column(db.String(100)) # Combustível, Peças, Pessoal
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20)) # Empresa ou Pessoal

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    descricao = db.Column(db.Text)
    responsavel = db.Column(db.String(100))