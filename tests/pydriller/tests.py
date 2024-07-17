from datetime import datetime
import json
from pydriller import Repository

def convert_to_iso8601(date):
    return date.isoformat()

def get_commits_pydriller(repo_name, start_date, end_date, max_workers=None, max_workers_default=4) -> list:
    if max_workers is None:
        max_workers = max_workers_default

    repo_url = 'https://github.com/' + repo_name

    # Convert ISO8601 format to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
    end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')

    print(start_date, end_date)

    repo = Repository(repo_url, since=start_date, to=end_date).traverse_commits()

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
commits = get_commits_pydriller('brenonevs/prs-pricemonitor', '2023-07-15T00:00:01Z', '2024-07-17T23:59:59Z')
