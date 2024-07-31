import tkinter as tk
from view.menu_view import DataMinerApp
import os
import sys
from dotenv import load_dotenv

# Obtém o diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Muda para o diretório do script
os.chdir(script_dir)

print("O diretório do script é:", script_dir)

# Código a ser executado a partir do diretório do script
print("O diretório atual é:", os.getcwd())

load_dotenv()

if __name__ == "__main__":
    root = tk.Tk()
    app = DataMinerApp(root)
    root.mainloop()
