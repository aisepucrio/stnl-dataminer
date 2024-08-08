import os
import json
import socket
from tkinter import messagebox
from dotenv import load_dotenv

# Classe base para interações com APIs
class BaseAPI:
    def __init__(self):
        self.reload_env()

    # Método para recarregar variáveis de ambiente
    def reload_env(self):
        load_dotenv(override=True)

    # Método para obter o caminho de salvamento
    def get_save_path(self):
        self.reload_env()
        return os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Downloads"))

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
            print("You are connected to the internet")
            s.close()
            pass
        except OSError:
            print("You are not connected to the internet")
            messagebox.showerror("Sem conexão com a internet", "Verifique sua conexão e tente novamente")
            exit(1) 
    
