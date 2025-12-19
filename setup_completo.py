from backend.app import create_app, db
from backend.models import Usuario, Funcionario
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

def atualizar_banco():
    with app.app_context():
        print("--- INICIANDO CONFIGURAÇÃO DO BANCO DE DADOS ---")
        
        # 1. Cria todas as tabelas que não existem (Isso resolve o erro da tabela 'usuario')
        try:
            db.create_all()
            print("✔ Tabelas criadas/verificadas com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")

        # 2. Cria o Usuário Admin se não existir
        try:
            admin_email = "admin@avelar.com"
            admin = Usuario.query.filter_by(email=admin_email).first()
            if not admin:
                print("Criando usuário Admin padrão...")
                novo_admin = Usuario(
                    nome="Administrador",
                    email=admin_email,
                    cargo="Admin"
                )
                novo_admin.set_senha("admin123") # Senha padrão
                db.session.add(novo_admin)
                db.session.commit()
                print("✔ Usuário Admin criado: admin@avelar.com / admin123")
            else:
                print("✔ Usuário Admin já existe.")
        except Exception as e:
            print(f"❌ Erro ao verificar Admin: {e}")

        # 3. Atualiza a tabela de Funcionários com as novas colunas (CPF, RG, etc)
        # Isso é necessário porque o db.create_all() NÃO altera tabelas que já existem.
        print("Verificando colunas da tabela Funcionario...")
        with db.engine.connect() as conn:
            novas_colunas = [
                ("cpf", "VARCHAR(20)"),
                ("rg", "VARCHAR(20)"),
                ("cnh", "VARCHAR(20)"),
                ("data_nascimento", "DATE"),
                ("telefone", "VARCHAR(20)"),
                ("endereco", "VARCHAR(200)")
            ]
            
            for col, tipo in novas_colunas:
                try:
                    # Tenta adicionar a coluna. Se já existir, vai dar erro e cair no except, o que é normal.
                    conn.execute(text(f"ALTER TABLE funcionario ADD COLUMN {col} {tipo}"))
                    print(f"  ➜ Coluna '{col}' adicionada.")
                except Exception as e:
                    # O erro 1060 significa "Duplicate column name", ou seja, já existe.
                    if "1060" in str(e) or "Duplicate column" in str(e):
                        print(f"  ✔ Coluna '{col}' já existe.")
                    else:
                        print(f"  ⚠️ Nota sobre '{col}': {e}")

        print("\n--- PROCESSO CONCLUÍDO ---")
        print("Agora você pode rodar o sistema normalmente.")

if __name__ == "__main__":
    atualizar_banco()