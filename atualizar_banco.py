import os
from backend.app import create_app
from backend.extensions import db
from backend.models import Cidade
from sqlalchemy import text

app = create_app()

def atualizar():
    with app.app_context():
        print("--- INICIANDO ATUALIZAÇÃO DO BANCO DE DADOS ---")
        
        # 1. Cria as tabelas que não existem (Cidades, Bairros, Funcionarios, Veiculos)
        # O SQLAlchemy ignora as tabelas que já existem, então isso é seguro.
        db.create_all()
        print("✅ Novas tabelas (Cidades, Bairros, etc) criadas.")

        # 2. Força a criação das colunas novas nas tabelas antigas (via SQL direto)
        # O db.create_all() NÃO altera tabelas existentes, por isso precisamos disso.
        with db.engine.connect() as conn:
            # A) Atualizar Tabela CLIENTES (Adicionar bairro_id e remover rota antiga se quiser)
            try:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN bairro_id INT"))
                conn.execute(text("ALTER TABLE clientes ADD CONSTRAINT fk_clientes_bairros FOREIGN KEY (bairro_id) REFERENCES bairros(id)"))
                print("✅ Tabela CLIENTES atualizada (Coluna bairro_id adicionada).")
            except Exception as e:
                print(f"ℹ️ Aviso em Clientes (provavelmente já atualizado): {e}")

            # B) Atualizar Tabela DESPESAS (Adicionar funcionario_id e veiculo_id)
            try:
                conn.execute(text("ALTER TABLE despesas ADD COLUMN funcionario_id INT"))
                conn.execute(text("ALTER TABLE despesas ADD CONSTRAINT fk_despesas_func FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)"))
                conn.execute(text("ALTER TABLE despesas ADD COLUMN veiculo_id INT"))
                conn.execute(text("ALTER TABLE despesas ADD CONSTRAINT fk_despesas_veic FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)"))
                print("✅ Tabela DESPESAS atualizada (Colunas funcionario/veiculo adicionadas).")
            except Exception as e:
                print(f"ℹ️ Aviso em Despesas (provavelmente já atualizado): {e}")
            
            # C) Atualizar Tabela CLIENTES (Adicionar complemento que faltava)
            try:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN complemento VARCHAR(100)"))
                print("✅ Tabela CLIENTES atualizada (Coluna complemento adicionada).")
            except:
                pass

            conn.commit()

        # 3. Popula as Cidades do RS (se estiver vazio)
        if Cidade.query.count() == 0:
            principais = [
                "Santa Cruz do Sul", "Vera Cruz", "Rio Pardo", "Venâncio Aires", 
                "Candelária", "Passo do Sobrado", "Vale do Sol", "Lajeado", 
                "Santa Maria", "Porto Alegre", "Canoas", "Novo Hamburgo"
            ]
            for nome in principais:
                db.session.add(Cidade(nome=nome, uf='RS'))
            db.session.commit()
            print("✅ Cidades do RS cadastradas automaticamente.")
        
        print("\n--- ATUALIZAÇÃO CONCLUÍDA COM SUCESSO ---")

if __name__ == "__main__":
    atualizar()