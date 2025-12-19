from backend.app import create_app, db
from sqlalchemy import text

app = create_app()

def atualizar():
    with app.app_context():
        print("--- ATUALIZANDO BANCO: CATÁLOGO E ORÇAMENTOS ---")
        
        with db.engine.connect() as conn:
            # 1. Expandir Tabela Catalogo
            colunas_novas = [
                ("marca", "VARCHAR(100)"),
                ("modelo", "VARCHAR(100)"),
                ("unidade", "VARCHAR(20) DEFAULT 'un'"), # un, metros, kg
                ("custo_compra", "FLOAT DEFAULT 0.0"), # Para saber o lucro
                ("valor_instalacao", "FLOAT DEFAULT 0.0"), # Custo de instalar este item
                ("estoque_atual", "INT DEFAULT 0")
            ]
            
            for col, tipo in colunas_novas:
                try:
                    conn.execute(text(f"ALTER TABLE catalogo ADD COLUMN {col} {tipo}"))
                    print(f"✔ Coluna '{col}' adicionada ao catálogo.")
                except Exception as e:
                    if "Duplicate" in str(e): print(f"✔ Coluna '{col}' já existia.")
                    else: print(f"⚠️ Erro em '{col}': {e}")

            # 2. Criar Tabela de Orçamentos (Cabeçalho)
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS orcamentos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        cliente_id INT,
                        data_criacao DATETIME,
                        status VARCHAR(50) DEFAULT 'Pendente',
                        valor_total_produtos FLOAT,
                        valor_total_servicos FLOAT,
                        valor_final FLOAT,
                        observacoes TEXT,
                        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                    )
                """))
                print("✔ Tabela 'orcamentos' criada.")
            except Exception as e:
                print(f"Erro orcamentos: {e}")

            # 3. Criar Tabela de Itens do Orçamento
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS orcamento_itens (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        orcamento_id INT,
                        catalogo_id INT,
                        quantidade FLOAT,
                        valor_unitario FLOAT,
                        subtotal FLOAT,
                        FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id),
                        FOREIGN KEY (catalogo_id) REFERENCES catalogo(id)
                    )
                """))
                print("✔ Tabela 'orcamento_itens' criada.")
            except Exception as e:
                print(f"Erro itens: {e}")

        print("--- BANCO ATUALIZADO COM SUCESSO ---")

if __name__ == "__main__":
    atualizar()