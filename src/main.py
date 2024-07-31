import tkinter as tk
from view.menu_view import DataMinerApp
import os
import sys
from dotenv import load_dotenv

def main():
    # Obtém o diretório onde o script está localizado
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Muda para o diretório do script
    os.chdir(script_dir)

    load_dotenv()

    if __name__ == "__main__":
        root = tk.Tk()
        app = DataMinerApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()
