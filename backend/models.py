from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# --- TABELA DE USUÁRIOS ---
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256)) # Aumentei o tamanho por segurança
    nome = db.Column(db.String(100))
    cargo = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)

    def set_senha(self, senha):
        # MUDANÇA AQUI: Forçando método compatível
        self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

# --- TABELA DE PERSONALIZAÇÃO ---
class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    id = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column(db.String(100), default="Avelar Security")
    cor_primaria = db.Column(db.String(20), default="#d32f2f")
    logo_path = db.Column(db.String(200), default="img/Logo.png")
    fundo_login = db.Column(db.String(200), default="")
    fundo_dashboard = db.Column(db.String(200), default="")

# --- TABELAS DO SISTEMA ---
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(200))
    bairro = db.Column(db.String(100)) 
    cpf = db.Column(db.String(20))
    telefone = db.Column(db.String(30))
    app_monitoramento = db.Column(db.String(50))
    qtd_cameras = db.Column(db.Integer, default=0)
    valor_mensal = db.Column(db.Float, default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    
    mensalidades = db.relationship('Mensalidade', backref='cliente', lazy=True)
    vendas = db.relationship('Venda', backref='cliente', lazy=True)
    ocorrencias = db.relationship('Ocorrencia', backref='cliente', lazy=True)
    usuario_login = db.relationship('Usuario', backref='dados_cliente', uselist=False)

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
    data = db.Column(db.Date, default=datetime.utcnow)
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
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20))

class Ocorrencia(db.Model):
    __tablename__ = 'ocorrencias'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    descricao = db.Column(db.Text)
    responsavel = db.Column(db.String(100))
    
class Catalogo(db.Model):
    __tablename__ = 'catalogo'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    item = db.Column(db.String(150))
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float)
