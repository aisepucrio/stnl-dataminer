import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Classe base para controladores
class BaseController:
    def __init__(self):
        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv()
        # Flag para parar o processo
        self.stop_process_flag = False

    # Método para obter o caminho de salvamento dos dados
    def get_save_path(self):
        # Recarregar as variáveis de ambiente
        self.reload_env()
        # Retorna o caminho de salvamento, padrão é a pasta Downloads do usuário
        return os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Downloads"))

    # Método para salvar dados em formato JSON
    def save_to_json(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    # Método para parar o processo de coleta de dados
    def stop_process(self):
        self.stop_process_flag = True

    # Método para recarregar as variáveis de ambiente
    def reload_env(self):
        load_dotenv(override=True)