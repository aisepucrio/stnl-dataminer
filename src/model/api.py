import requests
import os
import json
import shutil
import tempfile
import datetime
import customtkinter as ctk
import regex as re
import threading
from tqdm import tqdm
from pydriller import Repository
from urllib.parse import urlparse, urlencode
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from git import Repo, RemoteProgress, GitCommandError

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

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

# Classe base para interações com APIs
class BaseAPI:
    def __init__(self):
        load_dotenv()

    # Método para obter o caminho de salvamento
    def get_save_path(self):
        load_dotenv()
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

# Classe para interações com a API do Jira
class JiraAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.email = os.getenv('EMAIL')
        self.api_token = os.getenv('API_TOKEN')

    # Extrai domínio e chave do projeto Jira a partir da URL
    def extract_jira_domain_and_key(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_parts = parsed_url.path.split('/')
        project_key = path_parts[path_parts.index('projects') + 1] if 'projects' in path_parts else None
        return domain, project_key

    # Busca campos customizados do Jira
    def search_custom_fields(self, jira_domain):
        url = f"https://{jira_domain}/rest/api/2/field"
        auth = (self.email, self.api_token)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        fields = response.json()
        return {field['id']: field['name'] for field in fields if field['id'].startswith('customfield')}

    # Coleta tarefas do Jira
    def collect_tasks(self, jira_domain, project_key, task_type, start_date, end_date, stop_collecting):
        all_issues = []
        start_at = 0
        max_results = 50

        jql = f'project={project_key} AND issuetype={task_type}'
        if start_date and end_date:
            jql += f' AND created >= "{start_date}" AND created <= "{end_date}"'

        while True:
            if stop_collecting():
                print("Data collection stopped by user.")
                break

            url = f"https://{jira_domain}/rest/api/2/search"
            query = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results
            }
            auth = (self.email, self.api_token)
            try:
                response = requests.get(url, params=query, auth=auth)
            except Exception as e:
                print(f"Error fetching data from URL: {url} - {str(e)}")
                break

            issues = response.json()['issues']
            all_issues.extend(issues)
            start_at += max_results
            if len(issues) < max_results:
                break

        return all_issues

    # Remove campos nulos das tarefas
    def remove_null_fields(self, issues):
        if not issues:
            return issues

        keys_to_remove = set(issues[0]['fields'].keys())
        for issue in issues:
            keys_to_remove &= {key for key, value in issue['fields'].items() if value is None}

        for issue in issues:
            for key in keys_to_remove:
                del issue['fields'][key]

        return issues

    # Substitui IDs por nomes amigáveis
    def replace_ids(self, issues, custom_field_mapping):
        for issue in issues:
            fields = issue['fields']
            for field_id, field_name in custom_field_mapping.items():
                if field_id in fields:
                    fields[field_name] = fields.pop(field_id)
        return issues

# Classe para interações com a API do GitHub
class GitHubAPI(BaseAPI):
    def __init__(self, view=None):
        super().__init__()
        self.view = view
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.auth = None
        self.tokens = None
        self.usernames = None
        self.current_token_index = 0
        self.load_tokens()
        self.rotate_token()
        self.max_workers_default = int(os.getenv('MAX_WORKERS', '12'))

    # Função para validar token do GitHub
    def validate_tokens(self, tokens):
        github_token_regex = re.compile(r'ghp_[a-zA-Z0-9]{36}')
        for token in tokens:
            if not github_token_regex.match(token):
                print(f"Invalid GitHub token: '{token}'. Please check the .env file.")
                exit(1)

    # Carrega tokens do GitHub
    def load_tokens(self):
        try:
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

    # Rotaciona tokens para evitar limite de requisições
    def rotate_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
        self.auth = (self.usernames[self.current_token_index], self.tokens[self.current_token_index])
        print(f"Rotated to token {self.current_token_index + 1}")

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
        if max_workers is None:
            max_workers = self.max_workers_default
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
                    attempts += 1
                else:
                    data = response.json()
                    if date_key and start_date and end_date:
                        return [item for item in data if start_date <= datetime.strptime(item[date_key], '%Y-%m-%dT%H:%M:%SZ').date() <= end_date]
                    return data
            except requests.exceptions.RequestException as e:
                if e.response is not None and e.response.status_code == 403:
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

    # Obtém commits de um repositório no GitHub
    def get_commits(self, repo_name, start_date, end_date, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers_default

        url = f'https://api.github.com/repos/{repo_name}/commits'
        params = {
            'since': f'{start_date}T00:00:01Z',
            'until': f'{end_date}T23:59:59Z',
            'per_page': 35
        }
        commits = self.get_all_pages(url, 'Fetching commits', params, max_workers=max_workers)
        essential_commits = [{
            'sha': commit['sha'],
            'message': commit['commit']['message'],
            'date': commit['commit']['author']['date'], 
            'author': commit['commit']['author']['name']
        } for commit in commits if 'sha' in commit and 'commit' in commit and 'message' in commit['commit'] and 'author' in commit['commit'] and 'date' in commit['commit']['author'] and 'name' in commit['commit']['author']]

        return essential_commits
    
    # Obtém diretório inicial do usuário
    @staticmethod
    def user_home_directory():
        home_directory = os.path.expanduser("~")
        return home_directory

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
            self.ask_to_update_repo(clone_path)
            return True 

    # Pergunta ao usuário se deseja atualizar o repositório existente
    def ask_to_update_repo(self, repo_path):
        popup = ctk.CTkToplevel()
        popup.title("Repository Exists")
        popup.geometry("400x200")

        label = ctk.CTkLabel(popup, text="The repository already exists and may be outdated.\nDo you want to update it?")
        label.pack(pady=20)

        update_button = ctk.CTkButton(popup, text="Update", command=lambda: self.update_repo(repo_path, popup))
        update_button.pack(side="left", padx=20, pady=20)

        skip_button = ctk.CTkButton(popup, text="Skip", command=popup.destroy)
        skip_button.pack(side="right", padx=20, pady=20)

        popup.wait_window()

    # Atualiza o repositório local
    def update_repo(self, repo_path, popup):
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            print(f'\nRepo updated: {repo_path}\n')
        except GitCommandError as e:
            print(f'Error updating repo: {e}')
        popup.destroy()

    # Converte data para formato ISO 8601
    def convert_to_iso8601(self, date):
        return date.isoformat()

    # Obtém commits usando a biblioteca Pydriller
    def get_commits_pydriller(self, repo_name: str, start_date: str, end_date: str, max_workers: int | None = 4, clone_path: str | None  = None) -> list:

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
        else:
            start_date = datetime.min

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
        else:
            end_date = datetime.now()

        if max_workers is None:
            max_workers = self.max_workers_default

        if clone_path is None:
            clone_path = GitHubAPI.user_home_directory() + '/GitHubClones'

        if self.repo_exists(repo_name, clone_path):
            repo = Repository(clone_path + '/' + repo_name.split('/')[1], since=start_date, to=end_date).traverse_commits()
        else:
            repo_url = 'https://github.com/' + repo_name
            repo = Repository(repo_url, since=start_date, to=end_date).traverse_commits()

        commits = list(repo)

        essential_commits = [{
            'sha': commit.hash,
            'message': commit.msg,
            'date': self.convert_to_iso8601(commit.author_date),
            'author': commit.author.name
        } for commit in commits]

        return essential_commits
    
    # Obtém issues do repositório
    def get_issues(self, repo_name, start_date, end_date, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers_default
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
        return essential_issues

    # Obtém pull requests do repositório
    def get_pull_requests(self, repo_name, start_date, end_date, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        url = f'https://api.github.com/repos/{repo_name}/pulls'
        params = {
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
                
                labels = [label['name'] for label in pr.get('labels', [])]

                essential_pull_requests.append({
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'creator': pr['user']['login'],
                    'comments': comments,
                    'labels': labels  # Adicionando labels ao dicionário
                })
        return essential_pull_requests

    # Obtém branches do repositório
    def get_branches(self, repo_name, max_workers=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        url = f'https://api.github.com/repos/{repo_name}/branches'
        branches = self.get_all_pages(url, 'Fetching branches', max_workers=max_workers)
        essential_branches = [{
            'name': branch['name'],
            'sha': branch['commit']['sha']
        } for branch in branches if 'name' in branch and 'commit' in branch and 'sha' in branch['commit']]
        return essential_branches
