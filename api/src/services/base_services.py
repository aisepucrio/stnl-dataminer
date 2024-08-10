import os
import json
import socket
from tkinter import messagebox
from dotenv import load_dotenv, set_key, find_dotenv

# Classe base para interações com APIs
class BaseAPI:
    def __init__(self):
        self.load_env()

    # Método para recarregar variáveis de ambiente
    def load_env(self):
        load_dotenv()

    # Método para salvar dados em formato JSON
    def save_to_json(self, data, filename):
        save_path = self.get_save_path()
        full_path = os.path.join(save_path, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Método para verificar se há conexão com a internet
    def check_internet_connection(self, timeout=5):
        print("\nChecking internet connection...\n")
        try:
            # Tenta se conectar ao servidor DNS do Google
            socket.setdefaulttimeout(timeout)
            host = socket.gethostbyname("8.8.8.8")  # Endereço IP do servidor DNS do Google
            s = socket.create_connection((host, 53), timeout)
            print("\nYou are connected to the internet\n")
            s.close()
            return "You are connected to the internet"
        except OSError:
            print("You are not connected to the internet")
            return "You are not connected to the internet"
        
    def set_max_workers(self, max_workers):
        # Primeiro, alterar o valor na variável de ambiente
        print(f'Actual max workers: {os.environ.get("MAX_WORKERS", "not set")}')
        os.environ["MAX_WORKERS"] = str(max_workers)
        print(f'New max workers: {os.environ["MAX_WORKERS"]}')

        # Agora, atualizar o valor no arquivo .env
        dotenv_path = find_dotenv()
        if dotenv_path:
            set_key(dotenv_path, "MAX_WORKERS", str(max_workers))
            print(f'MAX_WORKERS updated in {dotenv_path}')
        else:
            print('.env file not found')
    
