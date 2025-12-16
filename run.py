import sys
import os

# Força o Python a incluir a pasta atual no caminho de busca
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)