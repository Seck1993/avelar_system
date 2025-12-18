from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# --- TABELAS AUXILIARES (MODULARES) ---
class Cidade(db.Model):
    __tablename__ = 'cidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), default='RS')
    bairros = db.relationship('Bairro', backref='cidade', lazy=True)

class Bairro(db.Model):
    __tablename__ = 'bairros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) # Será usado como ROTA
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'))
    clientes = db.relationship('Cliente', backref='bairro_obj', lazy=True)

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False) # Ex: Fiat Uno, Honda Titan
    placa = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)

# --- USUÁRIOS E CONFIG ---
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256))
    nome = db.Column(db.String(100))
    cargo = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    def set_senha(self, senha): self.senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
    def check_senha(self, senha): return check_password_hash(self.senha_hash, senha)

class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    id = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column(db.String(100), default="Avelar Security")
    cor_primaria = db.Column(db.String(20), default="#d32f2f")
    logo_path = db.Column(db.String(200), default="img/Logo.png")
    fundo_login = db.Column(db.String(200), default="")
    fundo_dashboard = db.Column(db.String(200), default="")

# --- TABELAS DO SISTEMA (ATUALIZADAS) ---
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    
    # VÍNCULO MODULAR COM BAIRRO (ROTA)
    bairro_id = db.Column(db.Integer, db.ForeignKey('bairros.id'), nullable=True)
    endereco = db.Column(db.String(200)) # Rua e Número
    complemento = db.Column(db.String(100)) # Apartamento, Bloco, etc.
    
    cpf = db.Column(db.String(20))
    telefone = db.Column(db.String(30))
    app_monitoramento = db.Column(db.String(50))
    qtd_cameras = db.Column(db.Integer, default=0)
    valor_mensal = db.Column(db.Float, default=0.0)
    dia_vencimento = db.Column(db.Integer, default=10)
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
    categoria = db.Column(db.String(100)) # Combustível, Salário, Manutenção...
    
    # VÍNCULOS MODULARES
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=True)
    
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