import os

print("--- DIAGNÓSTICO DE ARQUIVOS ---")
print(f"Pasta onde o script está rodando: {os.getcwd()}")
print("\nListando TUDO o que existe aqui dentro:")

for root, dirs, files in os.walk("."):
    for file in files:
        # Ignorar a pasta do ambiente virtual para não poluir a tela
        if "venv" in root:
            continue
        print(os.path.join(root, file))

print("---------------------------------")