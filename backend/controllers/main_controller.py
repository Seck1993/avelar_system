from flask import Blueprint, render_template, request, redirect, url_for
from backend.models.cliente import Cliente
from backend.models.operacional import Ocorrencia
from backend.models.financeiro import Despesa
from backend.extensions import db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    # Estatísticas Rápidas para o Painel
    total_clientes = Cliente.query.filter_by(ativo=True).count()
    total_ocorrencias = Ocorrencia.query.count()
    
    # Soma de despesas do mês atual (Exemplo simplificado)
    total_despesas = db.session.query(func.sum(Despesa.valor)).scalar() or 0.0
    
    return render_template('index.html', 
                           total_clientes=total_clientes, 
                           total_ocorrencias=total_ocorrencias,
                           total_despesas=total_despesas)

@main_bp.route('/clientes')
def listar_clientes():
    # Busca todos os clientes ativos
    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template('clientes.html', clientes=clientes)

@main_bp.route('/ocorrencias')
def listar_ocorrencias():
    # Busca as últimas 50 ocorrências
    ocorrencias = Ocorrencia.query.order_by(Ocorrencia.data.desc()).limit(50).all()
    return render_template('ocorrencias.html', ocorrencias=ocorrencias)

@main_bp.route('/financeiro')
def financeiro():
    despesas = Despesa.query.order_by(Despesa.data.desc()).limit(50).all()
    return render_template('financeiro.html', despesas=despesas)