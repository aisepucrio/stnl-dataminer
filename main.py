import os
import subprocess
import sys
import keyboard
from tkinter import messagebox
        
def run_main_py():
    # Diretório atual
    current_dir = os.getcwd()
    
    # Caminho para a pasta 'src'
    src_dir = os.path.join(current_dir, 'src')
    
    # Verifica se a pasta 'src' existe
    if not os.path.isdir(src_dir):
        print(f"A pasta 'src' não existe no diretório atual: {current_dir}")
        return
    
    # Caminho para o arquivo main.py
    main_py_path = os.path.join(src_dir, 'main.py')
    
    # Verifica se o arquivo main.py existe
    if not os.path.isfile(main_py_path):
        print(f"O arquivo 'main.py' não existe na pasta 'src': {src_dir}")
        return
    
    # Executa o main.py usando o mesmo intérprete Python
    try:
        subprocess.run([sys.executable, main_py_path], check=True)
        print(f"Executado com sucesso: {main_py_path}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o arquivo main.py: {e}")

if __name__ == "__main__":
    run_main_py()
