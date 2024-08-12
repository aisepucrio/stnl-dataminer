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
from dotenv import load_dotenv, set_key, find_dotenv
from git import Repo, RemoteProgress, GitCommandError
from tkinter import messagebox
from src.services.base_services import BaseAPI
from fastapi import HTTPException

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
        github_token_regex = re.compile(r'(ghp|gho|ghu|ghr|ghs|ghb|github_pat)_[a-zA-Z0-9]{36,40}')
        for token in tokens:
            if not github_token_regex.match(token):
                print(f"\nInvalid GitHub token: '{token}'. Please check the .env file.\n")

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
    def get_commits(self, repo_name: str | None = None, start_date: str | None = None, end_date: str | None = None, clone_path: str | None = None, output_path: str | None = None) -> str:
        try:
            print(f"\nProcessando repositório: {repo_name}\n")
            
            # Parsing dates
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_date = datetime.min

            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                end_date = datetime.now()

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
            
            self.save_to_json(essential_commits, f"{repo_name.replace('/', '_')}_commits.json")
            return essential_commits

        except Exception as e:
            print(f"Erro ao acessar o repositório: {e}")
            return f"Erro ao processar repositório '{repo_name}': {e}"

    def add_github_credentials(self, username, token):
        dotenv_path = find_dotenv()
        tokens = ""
        usernames = ""

        if dotenv_path:
            # Carregar os valores atuais das variáveis TOKENS e USERNAMES do arquivo .env
            tokens = os.environ.get("TOKENS", "")
            usernames = os.environ.get("USERNAMES", "")

            if tokens and usernames:
                print(f'Tokens atuais: {tokens}')
                print(f'Usernames atuais: {usernames}')
            else:
                print('Nenhum token ou username existente encontrado.')

            # Adicionar o novo token e username às listas
            if tokens:
                tokens += f",{token}"
                usernames += f",{username}"
            else:
                tokens = token
                usernames = username

            # Atualizar as variáveis de ambiente e no arquivo .env
            os.environ["TOKENS"] = tokens
            os.environ["USERNAMES"] = usernames
            set_key(dotenv_path, "TOKENS", tokens)
            set_key(dotenv_path, "USERNAMES", usernames)

            print(f'TOKENS atualizado em {dotenv_path}: {tokens}')
            print(f'USERNAMES atualizado em {dotenv_path}: {usernames}')
        else:
            print('.env file not found')

    def get_github_credentials(self):
        return self.usernames, self.tokens
    
    def check_remaining_requests(self, token):
        url = "https://api.github.com/rate_limit"
        headers = {
            'Authorization': f'token {token}'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            core_limit = data['rate']['remaining']
            return core_limit
        except requests.exceptions.RequestException as e:
            print(f'Error fetching rate limit: {e}')
            return 0
        
    def get_tokens(self):
        return self.tokens

    # Método para lidar com limite de requisições
    def handle_rate_limit(self, response):
        url = "https://api.github.com/rate_limit"
        headers = {
            "Authorization": f"token {self.tokens[self.current_token_index]}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            core_limit = data['rate']['remaining']
            print(f"\nRemaining requests: {core_limit}\n")
            return core_limit
        else:
            raise Exception(f"Error fetching rate limit: {response.status_code}, {response.text}")
        
    # Rotaciona tokens para evitar limite de requisições
    def rotate_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
        self.auth = (self.usernames[self.current_token_index], self.tokens[self.current_token_index])
        print(f"Rotated to token {self.current_token_index + 1}: {self.tokens[self.current_token_index]}")

    # Obtém nome do repositório a partir da URL
    def get_repo_name(self, repo_url):
        try:
            path = urlparse(repo_url).path
            repo_name = path.lstrip('/')
            if len(repo_name.split('/')) != 2:
                raise ValueError("Invalid repository URL. Make sure it is in the format 'https://github.com/owner/repo'.")
            return repo_name
        except Exception as e:
            raise ValueError("Error parsing repository URL. Check the format and try again.")

    # Obtém total de páginas de resultados
    def get_total_pages(self, url, params=None):
        max_retries = len(self.tokens)
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = requests.get(f"{url}?per_page=1", headers=self.headers, auth=self.auth, params=params)
                response.raise_for_status()
                
                rate_limit_remaining = self.handle_rate_limit(response)
                if rate_limit_remaining < 100:
                    print(f"Token limit is low ({rate_limit_remaining} remaining). Rotating token...")
                    attempts += 1
                else:
                    if 'Link' in response.headers:
                        links = response.headers['Link'].split(',')
                        for link in links:
                            if 'rel="last"' in link:
                                last_page_url = link[link.find('<') + 1:link.find('>'):]
                                return int(last_page_url.split('=')[-1])
                    return 1
            except requests.exceptions.RequestException as e:
                if e.response is not None and e.response.status_code == 403:
                    print(f"Token limit reached for token {self.current_token_index + 1}. Rotating token...")
                    self.rotate_token()
                    attempts += 1
                else:
                    raise Exception(f'Error fetching data from URL: {url} - {str(e)}')
            except Exception as e:
                raise Exception(f'Unexpected error: {str(e)}')
        raise Exception("All tokens have reached the limit.")
    
    # Obtém todas as páginas de resultados de uma requisição
    def get_all_pages(self, url, desc, params=None, date_key=None, start_date=None, end_date=None, max_workers=None):
        results = []
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date[:10], '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date[:10], '%Y-%m-%d').date()

        try:
            total_pages = self.get_total_pages(url, params)
        except Exception as e:
            print(e)
            return results

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for page in range(1, total_pages + 1):
                if params:
                    params['page'] = page
                    full_url = f"{url}?{urlencode(params)}"
                else:
                    full_url = f"{url}?page={page}"
                futures.append(executor.submit(self.fetch_page_data, full_url, date_key, start_date, end_date))

            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as e:
                    print(f"Error fetching page data: {str(e)}")

        if not results:
            print(f'No data found for {desc} in the given date range.')

        return results
    
    # Busca dados de uma página
    def fetch_page_data(self, url, date_key, start_date, end_date):
        max_retries = len(self.tokens)
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = requests.get(url, headers=self.headers, auth=self.auth)
                response.raise_for_status()

                rate_limit_remaining = self.handle_rate_limit(response)
                if rate_limit_remaining < 100:
                    print(f"Token limit is low ({rate_limit_remaining} remaining). Rotating token...")
                    attempts += 1
                else:
                    data = response.json()
                    if date_key and start_date and end_date:
                        return [item for item in data if start_date <= datetime.strptime(item[date_key], '%Y-%m-%dT%H:%M:%SZ').date() <= end_date]
                    return data
            except requests.exceptions.RequestException as e:
                if e.response is not None and e.response.status_code == 403:
                    print(f"The token requisition was rejected. Rotating token...")
                    self.rotate_token()
                    attempts += 1
                else:
                    print(f"Error fetching data from URL: {url} - {str(e)}")
                    return []
        print("All tokens have reached the limit. Fetch")
        return []
    
    # Obtém comentários de um issue ou pull request, incluindo o comentário inicial
    def get_comments_with_initial(self, issue_url, initial_comment, issue_number, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        comments = self.get_all_pages(issue_url, f'Fetching comments for issue/pr #{issue_number}', max_workers=max_workers)
        essential_comments = [{
            'user': initial_comment['user']['login'],
            'body': initial_comment['body'],
            'created_at': initial_comment['created_at']
        }]
        essential_comments.extend([{
            'user': comment['user']['login'],
            'body': comment['body'],
            'created_at': comment['created_at']
        } for comment in comments if 'user' in comment and 'login' in comment['user'] and 'body' in comment and 'created_at' in comment])
        return essential_comments
    
    # Obtém diretório inicial do usuário
    @staticmethod
    def user_home_directory():
        home_directory = os.path.expanduser("~")
        return home_directory

    # Função para clonar o repositório
    def clone_repo(self, repo_url, clone_path):
        if self.view:
            self.view.show_temp_message("Please wait while cloning the repository...")
        
        Repo.clone_from(repo_url, clone_path, progress=CloneProgress())
        if self.view:
            self.view.show_temp_message("Cloning complete.")

    # Resolve conflitos de forma automática
    def resolve_conflicts(self, repo):
        try:
            repo.git.merge('--abort')  # Aborta mesclagem anterior, se existir
        except GitCommandError:
            pass  # Ignora erros de abortar mesclagem

        try:
            repo.git.reset('--hard', 'origin/main')  # Reseta para o estado remoto
            repo.git.clean('-fd')  # Remove arquivos não rastreados
            repo.remotes.origin.pull()  # Tenta novamente o pull
            print('Conflicts resolved automatically by resetting to the remote state.')
        except GitCommandError as e:
            print(f'Error resolving conflicts: {e}')

    # Obtém issues do repositório
    def get_issues(self, repo_name, start_date, end_date):
        max_workers = int(self.get_max_workers())
        url = f'https://api.github.com/repos/{repo_name}/issues'
        params = {
            'since': f'{start_date}T00:00:01Z',
            'until': f'{end_date}T23:59:59Z',
            'per_page': 35
        }
        issues = self.get_all_pages(url, 'Fetching issues', params, 'created_at', start_date, end_date, max_workers=max_workers)
        essential_issues = []
        for issue in issues:
            if 'number' in issue and 'title' in issue and 'state' in issue and 'user' in issue and 'login' in issue['user']:
                issue_comments_url = issue['comments_url']
                initial_comment = {
                    'user': issue['user'],
                    'body': issue['body'],
                    'created_at': issue['created_at']
                }
                comments = self.get_comments_with_initial(issue_comments_url, initial_comment, issue['number'], max_workers)
                essential_issues.append({
                    'number': issue['number'],
                    'title': issue['title'],
                    'state': issue['state'],
                    'creator': issue['user']['login'],
                    'comments': comments
                })
        self.save_to_json(essential_issues, f"{repo_name.replace('/', '_')}_issues.json")
        return essential_issues
    
    # Obtém pull requests do repositório
    def get_pull_request_commits(self, repo_name, pull_number):
        url = f'https://api.github.com/repos/{repo_name}/pulls/{pull_number}/commits'
        return self.get_all_pages(url, f'Fetching commits for PR #{pull_number}')

    def get_pull_requests(self, repo_name, start_date, end_date):
        max_workers = int(self.get_max_workers())
        url = f'https://api.github.com/repos/{repo_name}/pulls'
        params = {
            'state': 'all',
            'state': 'all',
            'since': f'{start_date}T00:00:01Z',
            'until': f'{end_date}T23:59:59Z',
            'per_page': 35
        }
        pull_requests = self.get_all_pages(url, 'Fetching pull requests', params, 'created_at', start_date, end_date, max_workers=max_workers)
        essential_pull_requests = []
        for pr in pull_requests:
            if 'number' in pr and 'title' in pr and 'state' in pr and 'user' in pr and 'login' in pr['user']:
                pr_comments_url = pr['_links']['comments']['href']
                initial_comment = {
                    'user': pr['user'],
                    'body': pr['body'],
                    'created_at': pr['created_at']
                }
                comments = self.get_comments_with_initial(pr_comments_url, initial_comment, pr['number'], max_workers)

                # Adiciona commits relacionados ao PR
                commits = self.get_pull_request_commits(repo_name, pr['number'])

                labels = [label['name'] for label in pr.get('labels', [])]

                essential_pull_requests.append({
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'creator': pr['user']['login'],
                    'comments': comments,
                    'labels': labels,
                    'commits': commits  # Adiciona commits ao PR
                })
        self.save_to_json(essential_pull_requests, f"{repo_name.replace('/', '_')}_pull_requests.json")
        return essential_pull_requests

    # Obtém branches do repositório
    def get_branches(self, repo_name):
        try:
            max_workers = int(self.get_max_workers())
            url = f'https://api.github.com/repos/{repo_name}/branches'
            branches = self.get_all_pages(url, 'Fetching branches', max_workers=max_workers)
            essential_branches = [{
                'name': branch['name'],
                'sha': branch['commit']['sha']
            } for branch in branches if 'name' in branch and 'commit' in branch and 'sha' in branch['commit']]
            self.save_to_json(essential_branches, f"{repo_name.replace('/', '_')}_branches.json")
            return essential_branches
        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição ao GitHub: {e}")
            raise HTTPException(status_code=500, detail="Erro de comunicação com a API do GitHub.")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter branches do repositório.")
