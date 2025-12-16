import os
import shutil

print("--- INICIANDO CORREÇÃO AUTOMÁTICA ---")

# 1. Renomear arquivos que ficaram como .txt
arquivos_para_renomear = [
    "app.py.txt", 
    "config.py.txt", 
    "extensions.py.txt",
    "models/cliente.py.txt", 
    "models/financeiro.py.txt", 
    "models/operacional.py.txt"
]

print("\n>>> Passo 1: Corrigindo extensões (.txt -> .py)")
for nome_errado in arquivos_para_renomear:
    # Verifica se o arquivo existe (mesmo que em subpastas ou raiz)
    if os.path.exists(nome_errado):
        nome_certo = nome_errado.replace(".txt", "")
        try:
            os.rename(nome_errado, nome_certo)
            print(f"✅ Corrigido: {nome_errado} -> {nome_certo}")
        except Exception as e:
            print(f"❌ Erro ao renomear {nome_errado}: {e}")
    else:
        print(f"⚠️ Arquivo não encontrado (talvez já esteja certo): {nome_errado}")

# 2. Mover arquivos para a pasta 'backend'
print("\n>>> Passo 2: Movendo arquivos para a pasta 'backend'")

# Cria a pasta backend se não existir
if not os.path.exists("backend"):
    os.makedirs("backend")
    print("📂 Pasta 'backend' criada.")

itens_para_mover = [
    "app.py", 
    "config.py", 
    "extensions.py", 
    "__init__.py",
    "controllers", 
    "models", 
    "services"
]

for item in itens_para_mover:
    destino = os.path.join("backend", item)
    
    # Só move se o item existir na raiz e NÃO existir no destino ainda
    if os.path.exists(item):
        if not os.path.exists(destino):
            try:
                shutil.move(item, destino)
                print(f"🚚 Movido: {item} -> backend/{item}")
            except Exception as e:
                print(f"❌ Erro ao mover {item}: {e}")
        else:
            print(f"ℹ️ {item} já está dentro de backend.")
    else:
        print(f"⚠️ Item não encontrado na raiz: {item}")

print("\n--- PRONTO! TENTE RODAR O SISTEMA AGORA ---")
print("Comando: python run.py")