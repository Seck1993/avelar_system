from backend.app import create_app, db
from sqlalchemy import text

app = create_app()

def corrigir_tudo():
    with app.app_context():
        print("--- INICIANDO CORREÇÃO GERAL DO BANCO DE DADOS ---")
        
        with db.engine.connect() as conn:
            
            # 1. CORRIGIR OCORRENCIAS (Erro atual)
            print("\n> Verificando tabela Ocorrências...")
            try:
                conn.execute(text("ALTER TABLE ocorrencias ADD COLUMN titulo VARCHAR(100)"))
                print("  ✔ Coluna 'titulo' adicionada.")
            except Exception as e:
                if "Duplicate" in str(e): print("  ✔ Coluna 'titulo' já existe.")
                else: print(f"  ⚠️ Nota: {e}")

            # 2. CORRIGIR CLIENTES (Garantia)
            print("\n> Verificando tabela Clientes...")
            colunas_cliente = [
                ("dia_vencimento", "INT DEFAULT 10"),
                ("valor_mensal", "FLOAT DEFAULT 0.0"),
                ("app_monitoramento", "VARCHAR(50)"),
                ("qtd_cameras", "INT DEFAULT 0")
            ]
            for col, tipo in colunas_cliente:
                try:
                    conn.execute(text(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}"))
                    print(f"  ✔ Coluna '{col}' adicionada.")
                except Exception as e:
                    if "Duplicate" in str(e): print(f"  ✔ Coluna '{col}' já existe.")
            
            # 3. CORRIGIR CATÁLOGO (Novos campos de produto)
            print("\n> Verificando tabela Catálogo...")
            colunas_catalogo = [
                ("marca", "VARCHAR(100)"),
                ("modelo", "VARCHAR(100)"),
                ("unidade", "VARCHAR(20) DEFAULT 'un'"),
                ("custo_compra", "FLOAT DEFAULT 0.0"),
                ("valor_instalacao", "FLOAT DEFAULT 0.0"),
                ("estoque_atual", "INT DEFAULT 0")
            ]
            for col, tipo in colunas_catalogo:
                try:
                    conn.execute(text(f"ALTER TABLE catalogo ADD COLUMN {col} {tipo}"))
                    print(f"  ✔ Coluna '{col}' adicionada.")
                except Exception as e:
                    if "Duplicate" in str(e): print(f"  ✔ Coluna '{col}' já existe.")

            # 4. CRIAR TABELAS DE ORÇAMENTO (Se não existirem)
            print("\n> Verificando tabelas de Orçamento...")
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
                print("  ✔ Tabela 'orcamentos' verificada.")
                
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
                print("  ✔ Tabela 'orcamento_itens' verificada.")
            except Exception as e:
                print(f"  ⚠️ Erro tabelas orcamento: {e}")

        print("\n--- PROCESSO CONCLUÍDO ---")
        print("Pode acessar o sistema. Se der erro novamente, recarregue a página.")

if __name__ == "__main__":
    corrigir_tudo()