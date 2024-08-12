import requests
import os
import subprocess
from dotenv import load_dotenv

class GitHubAPI:
    
    _BASE_URL = "http://127.0.0.1:8000/github"  # Constante de classe, não deve ser alterada

    def __init__(self):
        self.start_uvicorn_server()

    @property
    def BASE_URL(self):
        return self._BASE_URL
    
    def start_uvicorn_server(self):
        try:
            print("Starting Uvicorn server...")
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    ["uvicorn", "main:app", "--reload"],
                    cwd="api",
                    creationflags=subprocess.CREATE_NO_WINDOW  # Oculta o prompt no Windows
                )
            else:  # Unix/Linux
                subprocess.Popen(
                    ["uvicorn", "main:app", "--reload"],
                    cwd="api",
                    stdout=subprocess.DEVNULL,  # Redireciona a saída padrão para ocultá-la
                    stderr=subprocess.DEVNULL   # Redireciona o erro padrão para ocultá-lo
                )
            print("Uvicorn server started.")
        except Exception as e:
            print(f"Error starting Uvicorn server: {e}")

    def check_internet_connection(self):
        try:
            response = requests.get(f"{self.BASE_URL}/check-internet-connection")
            if response.status_code == 200:
                print(f'Internet connection: {response.json()}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error checking internet connection: {e}")

    def check_remaining_requests(self, token):
        try:
            response = requests.get(f"{self.BASE_URL}/check-remaining-requests/{token}")
            if response.status_code == 200:
                try:
                    print(f'Remaining requests: {response.json()["remaining_requests"]}')
                    return response.json()
                except Exception as e:
                    print(f"Error processing JSON: {e}")
            else:
                print(f"HTTP Error: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"Error checking remaining requests: {e}")

    def get_github_credentials(self):
        try:
            response = requests.get(f"{self.BASE_URL}/get-github-credentials")
            if response.status_code == 200:
                print(f'GitHub credentials: {response.json()}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting GitHub credentials: {e}")

    def get_max_workers(self):
        try:
            response = requests.get(f"{self.BASE_URL}/get-max-workers")
            if response.status_code == 200:
                print(f'MAX_WORKERS: {response.json()}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting MAX_WORKERS: {e}")

    def get_tokens(self):
        try:
            response = requests.get(f"{self.BASE_URL}/get-tokens")
            if response.status_code == 200:
                print(f'Tokens: {response.json()}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting tokens: {e}")

    def set_max_workers(self, max_workers):
        try:
            response = requests.get(f"{self.BASE_URL}/set-max-workers-to/{max_workers}")
            if response.status_code == 200:
                print(f'MAX_WORKERS updated to {max_workers}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error setting MAX_WORKERS: {e}")

    def set_save_path(self, save_path):
        try:
            response = requests.post(f"{self.BASE_URL}/set-save-path/{save_path}")
            if response.status_code == 200:
                load_dotenv()
                save_path = os.getenv("SAVE_PATH")
                print(f'SAVE_PATH updated to {save_path}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error setting SAVE_PATH: {e}")

    def set_usage_of_database(self, database_usage=True):
        try:
            response = requests.post(f"{self.BASE_URL}/set-usage-of-database/{database_usage}")
            if response.status_code == 200:
                print(f'Database usage: {response.json()}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error setting database usage: {e}")

    def add_github_credentials(self, username, token):
        try:
            response = requests.post(f"{self.BASE_URL}/add_github_credentials/{username}/{token}")
            if response.status_code == 200:
                print(f'Token {token} added to {username}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error adding GitHub credentials: {e}")

    def get_commits(self, repo_name="aisepucrio/stnl-dataminer", start_date="2023-01-01", end_date="2024-07-31"):
        try:
            print(f'Getting commits from {repo_name} from {start_date} to {end_date}')
            repo_name = repo_name.replace("/", "_")
            response = requests.get(f"{self.BASE_URL}/get-commits/{repo_name}/{start_date}/{end_date}")
            if response.status_code == 200:
                load_dotenv()
                save_path = os.getenv("SAVE_PATH")
                print(f'Commits saved in {save_path}')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting commits: {e}")

    def get_branches(self, repo_name="aisepucrio/stnl-dataminer"):
        try:
            print(f'Getting branches from {repo_name}')
            repo_name = repo_name.replace("/", "_")
            response = requests.get(f"{self.BASE_URL}/get-branches/{repo_name}")
            if response.status_code == 200:
                load_dotenv()
                save_path = os.getenv("SAVE_PATH")
                print(f'Branches saved in {save_path} as {repo_name}_branches.json')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting branches: {e}")

    def get_pull_requests(self, repo_name="aisepucrio/stnl-dataminer", start_date="2023-01-01", end_date="2024-07-31"):
        try:
            print(f'Getting pull requests from {repo_name} from {start_date} to {end_date}')
            repo_name = repo_name.replace("/", "_")
            response = requests.get(f"{self.BASE_URL}/get-pull-requests/{repo_name}/{start_date}/{end_date}")
            if response.status_code == 200:
                load_dotenv()
                save_path = os.getenv("SAVE_PATH")
                print(f'Pull requests saved in {save_path} as {repo_name}_pull_requests.json')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting pull requests: {e}")

    def get_issues(self, repo_name="aisepucrio/stnl-dataminer", start_date="2023-01-01", end_date="2024-07-31"):
        try:
            print(f'Getting issues from {repo_name} from {start_date} to {end_date}')
            repo_name = repo_name.replace("/", "_")
            response = requests.get(f"{self.BASE_URL}/get-issues/{repo_name}/{start_date}/{end_date}")
            if response.status_code == 200:
                load_dotenv()
                save_path = os.getenv("SAVE_PATH")
                print(f'Issues saved in {save_path} as {repo_name}_issues.json')
                return response.json()
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting issues: {e}")