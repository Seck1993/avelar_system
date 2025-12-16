from backend.app import create_app
from backend.extensions import db
from backend.models import Usuario

app = create_app()

with app.app_context():
    print("\n" + "="*40)
    print("DIAGNÓSTICO DE LOGIN AVELAR")
    print("="*40)
    
    # 1. Verifica qual banco está usando
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"📡 Banco Conectado: {db_url.split('@')[1] if '@' in db_url else 'SQLite Local'}")

    # 2. Limpeza Radical: Remove admin se existir
    old_admin = Usuario.query.filter_by(email='admin@avelar.com').first()
    if old_admin:
        print("🗑️  Admin antigo encontrado. Removendo...")
        db.session.delete(old_admin)
        db.session.commit()
    
    # 3. Criação Limpa
    print("✨ Criando novo Admin do zero...")
    novo_admin = Usuario(
        nome='Admin Supremo', 
        email='admin@avelar.com', 
        cargo='Admin'
    )
    # Define a senha
    novo_admin.set_senha('123456')
    db.session.add(novo_admin)
    db.session.commit()
    
    # 4. A PROVA REAL (Teste de senha)
    # Vamos buscar o usuário que acabamos de criar e testar a senha
    teste_user = Usuario.query.filter_by(email='admin@avelar.com').first()
    
    if teste_user:
        print(f"👤 Usuário encontrado: {teste_user.email}")
        print(f"🔑 Hash salvo no banco: {teste_user.senha_hash[:20]}...")
        
        # Testar a senha
        if teste_user.check_senha('123456'):
            print("\n✅ SUCESSO ABSOLUTO: A senha '123456' foi validada pelo sistema!")
        else:
            print("\n❌ ERRO CRÍTICO: A senha foi salva mas não valida. Problema de criptografia.")
    else:
        print("\n❌ ERRO: O usuário não foi salvo no banco.")

    print("="*40 + "\n")
