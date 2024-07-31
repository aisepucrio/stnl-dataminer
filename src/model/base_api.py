import os
import json
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
    
    # Método para lidar com limite de requisições
    def handle_rate_limit(self, response):
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if rate_limit_remaining < 100:
            self.rotate_token()
        return rate_limit_remaining