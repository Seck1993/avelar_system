#!/bin/bash

# Define o caminho da pasta
CAMINHO="/home/avelarsecurity/avelar_system"
DATA_HORA=$(date '+%Y-%m-%d %H:%M:%S')

echo "--- Iniciando Backup para o GitHub: $DATA_HORA ---"

# 1. Entra na pasta
cd "$CAMINHO" || { echo "Erro: Pasta não encontrada"; exit 1; }

# 2. Configura usuário (caso o PythonAnywhere tenha esquecido)
# Isso evita erro de "quem é você?"
git config --global user.email "seu_email@exemplo.com"
git config --global user.name "Avelar Security"

# 3. Adiciona TODAS as alterações (novos arquivos, edições, exclusões)
echo "Adicionando arquivos..."
git add .

# 4. Verifica se tem algo para salvar
if git diff-index --quiet HEAD --; then
    echo "Nenhuma alteração encontrada para salvar."
else
    # 5. Cria o pacote (Commit)
    echo "Salvando alterações (Commit)..."
    git commit -m "Backup automático PythonAnywhere: $DATA_HORA"

    # 6. Envia para o GitHub
    echo "Enviando para o GitHub (Push)..."
    git push origin main
fi

echo "=========================================="
