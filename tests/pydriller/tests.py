import json
import os
import subprocess as sbclone_repo
import platform
from git import Repo, RemoteProgress
from tqdm import tqdm
from datetime import datetime
from pydriller import Repository

class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()
    
    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

def user_home_directory():
    home_directory = os.path.expanduser("~")
    return home_directory

def repo_exists(repo_name: str, clone_path: str = user_home_directory() + '/GitHubClones') -> bool:
    clone_path = clone_path + '/' + repo_name.split('/')[1]
    if not os.path.exists(clone_path):
        repo_url = 'https://github.com/' + repo_name
        print(f'\nCreating directory: {clone_path}\n')
        os.makedirs(clone_path)
        print(f'\nCloning repo: {repo_url}\n')
        Repo.clone_from(repo_url, clone_path, progress=CloneProgress())
        print(f'\nRepo cloned: {clone_path}\n')
        return False
    else:
        print(f'\nRepo already exists: {clone_path}\n')
        return True
    
def convert_to_iso8601(date):
    return date.isoformat()

def get_commits_pydriller(repo_name: str, 
                          start_date: str = None, 
                          end_date: str = None, 
                          max_workers: int = 4, 
                          clone_path: str = user_home_directory()) -> list:
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
    else:
        start_date = datetime.min  # Define start_date como a data mínima possível
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
    else:
        end_date = datetime.now()  # Define end_date como a data e hora atuais
    
    if repo_exists(repo_name, clone_path):
        print('Repositório já clonado')
        repo_path = os.path.join(clone_path, repo_name.split('/')[1])
    else:
        print('Clonando repositório...')
        repo_path = 'https://github.com/' + repo_name
    
    repo = Repository(repo_path, since=start_date, to=end_date).traverse_commits()
    
    commits = list(repo)
    
    essential_commits = [{
        'sha': commit.hash,
        'message': commit.msg,
        'date': convert_to_iso8601(commit.author_date), 
        'author': commit.author.name
    } for commit in commits]
    
    with open('commits.json', 'w') as f:
        json.dump(essential_commits, f, indent=4)
    
    return essential_commits
# Exemplo de uso
commits = get_commits_pydriller(repo_name='aisepucrio/stnl-dataminer', start_date='2024-07-18T00:00:01Z')


