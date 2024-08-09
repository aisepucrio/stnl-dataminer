import requests
import os
import datetime
import customtkinter as ctk
import regex as re
import threading
import json
from tqdm import tqdm
from pydriller import Repository
from urllib.parse import urlparse, urlencode
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from git import Repo, RemoteProgress, GitCommandError
from tkinter import messagebox
from src.services.base_services import BaseAPI

# Classe para mostrar progresso ao clonar repositórios
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()
    
    # Atualiza barra de progresso
    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

class GitHubAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.auth = None
        self.tokens = None
        self.usernames = None
        self.current_token_index = 0
        self.load_tokens()
    
    # Converte data para formato ISO 8601
    def convert_to_iso8601(self, date):
        return date.isoformat()


    def load_tokens(self):
        try:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
            print(env_path)

            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')

            self.tokens = os.getenv('TOKENS').split(',')
            self.validate_tokens(self.tokens)
        except Exception as e:
            print('No GitHub tokens found. Please add them to the .env')
            exit(1)
        try:
            self.usernames = os.getenv('USERNAMES').split(',')
        except Exception as e:
            print('No GitHub usernames found. Please add them to the .env')
            exit(1)

    # Função para validar token do GitHub
    def validate_tokens(self, tokens):
        github_token_regex = re.compile(r'(ghp|gho|ghu|ghr|ghs|ghb|github_pat)_[a-zA-Z0-9]{36}')
        for token in tokens:
            if not github_token_regex.match(token):
                print(f"Invalid GitHub token: '{token}'. Please check the .env file.")
                messagebox.showinfo("Error", f"Invalid GitHub token: '{token}'. Please check the .env file.")
                exit(1)

    # Obtém diretório inicial do usuário
    @staticmethod
    def user_home_directory():
        home_directory = os.path.expanduser("~")
        return home_directory
    
    # Atualiza o repositório local
    def update_repo(self, repo_path):
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            
            # Tenta fazer pull
            origin.pull()
            print(f'\nRepo updated: {repo_path}\n')
        except GitCommandError as e:
            if 'CONFLICT' in str(e):
                print(f'Conflict detected: {e}')
                # Resolve conflitos de forma automática usando estratégia de mesclagem
                self.resolve_conflicts(repo)
            else:
                print(f'Error updating repo: {e}')
    
    # Verifica se o repositório já existe no diretório especificado
    def repo_exists(self, repo_name: str, clone_path: str | None = None) -> bool:
        if clone_path is None:
            clone_path = GitHubAPI.user_home_directory() + '/GitHubClones'
        else:
            clone_path = clone_path + '/' + repo_name.split('/')[1]

        if not os.path.exists(clone_path):
            repo_url = 'https://github.com/' + repo_name
            print(f'\nCreating directory: {clone_path}\n')
            os.makedirs(clone_path)
            
            print(f'\nCloning repo: {repo_url}\n')
            clone_thread = threading.Thread(target=self.clone_repo, args=(repo_url, clone_path))
            clone_thread.start()
            clone_thread.join()  # Espera a thread terminar
            
            print(f'\nRepo cloned: {clone_path}\n')
            return False
        else:
            print(f'\nRepo already exists: {clone_path}\n')
            self.update_repo(clone_path)
            return True 

    # Obtém commits usando a biblioteca Pydriller
    def get_commits_pydriller(self, repo_name: str | None = None, start_date: str | None = None, end_date: str | None = None, clone_path: str | None = None, output_path: str | None = None) -> str:
        try:
            print(f"\nProcessando repositório: {repo_name}\n")
            
            # Parsing dates
            start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ') if start_date else datetime.min
            end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ') if end_date else datetime.now()

            clone_path = clone_path if clone_path is not None else os.path.join(self.user_home_directory(), 'GitHubClones')

            # Define o caminho de saída
            output_path = output_path if output_path else os.path.join(os.getcwd(), f"{repo_name.replace('/', '_')}_commits.json")

            # Check if repository exists locally
            if self.repo_exists(repo_name, clone_path):
                repo_path = os.path.join(clone_path, repo_name.split('/')[1])
                repo = Repository(repo_path, since=start_date, to=end_date).traverse_commits()
            else:
                repo_url = f'https://github.com/{repo_name}'
                repo = Repository(repo_url, since=start_date, to=end_date).traverse_commits()

            print("\nIniciando processamento dos commits...\n")
            essential_commits = []
            
            for commit in repo:
                commit_data = {
                    'sha': commit.hash,
                    'message': commit.msg,
                    'date': self.convert_to_iso8601(commit.author_date),
                    'author': {
                        'name': None,
                        'email': None
                    },
                    'committer': {
                        'name': None,
                        'email': None
                    },
                    'lines': {
                        'insertions': commit.insertions,
                        'deletions': commit.deletions,
                        'files': commit.files
                    },
                    'in_main_branch': commit.in_main_branch,
                    'merge': commit.merge,
                    'dmm_unit_size': None,
                    'dmm_unit_complexity': None,
                    'dmm_unit_interfacing': None,
                    'modified_files': []
                }
                
                # Process author
                try:
                    commit_data['author']['name'] = commit.author.name
                    commit_data['author']['email'] = commit.author.email
                except Exception as e:
                    print(f"\nErro ao processar autor do commit {commit.hash}: {e}\n")
                
                # Process committer
                try:
                    commit_data['committer']['name'] = commit.committer.name
                    commit_data['committer']['email'] = commit.committer.email
                except Exception as e:
                    print(f"\nErro ao processar committer do commit {commit.hash}: {e}\n")
                
                # Process DMM metrics
                try:
                    commit_data['dmm_unit_size'] = commit.dmm_unit_size
                    commit_data['dmm_unit_complexity'] = commit.dmm_unit_complexity
                    commit_data['dmm_unit_interfacing'] = commit.dmm_unit_interfacing
                except Exception as e:
                    print(f"\nErro ao processar DMM metrics do commit {commit.hash}: {e}\n")
                
                # Process modified files
                for mod in commit.modified_files:
                    try:
                        mod_data = {
                            'old_path': mod.old_path,
                            'new_path': mod.new_path,
                            'filename': mod.filename,
                            'change_type': mod.change_type.name,
                            'diff': mod.diff,
                            'added_lines': mod.added_lines,
                            'deleted_lines': mod.deleted_lines,
                            'complexity': mod.complexity,
                            'methods': []
                        }
                        
                        # Process methods
                        for method in mod.methods:
                            try:
                                method_data = {
                                    'name': method.name,
                                    'complexity': method.complexity,
                                    'max_nesting': None
                                }
                                try:
                                    method_data['max_nesting'] = method.max_nesting
                                except AttributeError:
                                    pass
                                
                                mod_data['methods'].append(method_data)
                            except Exception as e:
                                print(f"\nErro ao processar método {method.name} do arquivo {mod.filename} no commit {commit.hash}: {e}\n")

                        commit_data['modified_files'].append(mod_data)
                    except Exception as e:
                        print(f"\nErro ao processar arquivo modificado {mod.filename} no commit {commit.hash}: {e}\n")

                essential_commits.append(commit_data)
            
            # Salvando os commits no arquivo JSON
            with open(output_path, 'w') as outfile:
                json.dump(essential_commits, outfile, indent=4)
            
            print(f"\nCommits salvos com sucesso em {output_path}\n")
            return f"Commits do repositório '{repo_name}' entre {start_date.isoformat()} e {end_date.isoformat()} salvos com sucesso em {output_path}"

        except Exception as e:
            print(f"Erro ao acessar o repositório: {e}")
            return f"Erro ao processar repositório '{repo_name}': {e}"

    def get_tokens(self):
        return self.tokens

            
