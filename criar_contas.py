from backend.app import create_app
from backend.extensions import db
from backend.models import Usuario, Cliente

app = create_app()

with app.app_context():
    print("\n--- INICIANDO VERIFICACAO DE CONTAS ---\n")

    # 1. GARANTIR ADMIN
    admin = Usuario.query.filter_by(email='admin@avelar.com').first()
    if not admin:
        admin = Usuario(nome='Administrador', email='admin@avelar.com', cargo='Admin')
        admin.set_senha('admin123')
        db.session.add(admin)
        print("✅ ADMIN CRIADO.")
    else:
        admin.set_senha('admin123') # Garante a senha certa
        print("✅ ADMIN JA EXISTIA (Senha resetada para admin123).")

    # 2. GARANTIR CLIENTE
    # Verifica se já criou o perfil do cliente antes do erro
    cli = Cliente.query.filter_by(nome='Cliente Teste').first()
    if not cli:
        cli = Cliente(
            nome='Cliente Teste', 
            bairro='Centro', 
            endereco='Rua Teste, 100',
            valor_mensal=150.00,
            ativo=True
        )
        db.session.add(cli)
        db.session.commit() # Salva para ter o ID
        print("✅ PERFIL DO CLIENTE CRIADO.")
    else:
        print("✅ PERFIL DO CLIENTE JA EXISTIA.")

    # Verifica o Login do Cliente
    user_cli = Usuario.query.filter_by(email='cliente@avelar.com').first()
    if not user_cli:
        user_cli = Usuario(
            nome='Cliente Teste', 
            email='cliente@avelar.com', 
            cargo='Cliente', 
            cliente_id=cli.id
        )
        user_cli.set_senha('123456')
        db.session.add(user_cli)
        print("✅ LOGIN DO CLIENTE CRIADO.")
    else:
        user_cli.set_senha('123456') # Garante a senha
        print("✅ LOGIN DO CLIENTE JA EXISTIA (Senha resetada para 123456).")

    db.session.commit()
    print("\n--- TUDO PRONTO! PODE LOGAR ---")
