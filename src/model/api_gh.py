import requests
from urllib.parse import urlparse, urlencode
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

class GitHubAPI:
    def __init__(self):
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        self.auth = None
        self.tokens = None
        self.usernames = None
        self.current_token_index = 0
        self.load_tokens()
        self.rotate_token()

    def load_tokens(self):
        from dotenv import load_dotenv
        import os
        load_dotenv()
        try:
            self.tokens = os.getenv('TOKENS').split(',')
        except Exception as e:
            print('No GitHub tokens found. Please add them to the .env')
            exit(1)
        try:
            self.usernames = os.getenv('USERNAMES').split(',')
        except Exception as e:
            print('No GitHub usernames found. Please add them to the .env')
            exit(1)

    def rotate_token(self):
        self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
        self.auth = (self.usernames[self.current_token_index], self.tokens[self.current_token_index])
        print(f"Rotated to token {self.current_token_index + 1}")

    def get_repo_name(self, repo_url):
        try:
            path = urlparse(repo_url).path
            repo_name = path.lstrip('/')
            if len(repo_name.split('/')) != 2:
                raise ValueError("Invalid repository URL. Make sure it is in the format 'https://github.com/owner/repo'.")
            return repo_name
        except Exception as e:
            raise ValueError("Error parsing repository URL. Check the format and try again.")

    def get_total_pages(self, url, params=None):
        max_retries = len(self.tokens)
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = requests.get(f"{url}?per_page=1", headers=self.headers, auth=self.auth, params=params)
                response.raise_for_status()
                
                rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if rate_limit_remaining < 100:
                    print(f"Token limit is low ({rate_limit_remaining} remaining). Rotating token...")
                    self.rotate_token()
                    attempts += 1
                else:
                    if 'Link' in response.headers:
                        links = response.headers['Link'].split(',')
                        for link in links:
                            if 'rel="last"' in link:
                                last_page_url = link[link.find('<') + 1:link.find('>')]
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

    def get_all_pages(self, url, desc, params=None, date_key=None, start_date=None, end_date=None, max_workers=12):
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

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
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

    def fetch_page_data(self, url, date_key, start_date, end_date):
        max_retries = len(self.tokens)
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = requests.get(url, headers=self.headers, auth=self.auth)
                response.raise_for_status()

                rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                if rate_limit_remaining < 100:
                    self.rotate_token()
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
        print("All tokens have reached the limit.")
        return []

    def get_comments_with_initial(self, issue_url, initial_comment, issue_number, max_workers=12):
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

    def get_commits(self, repo_name, start_date, end_date, max_workers=12):
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

    def get_issues(self, repo_name, start_date, end_date, max_workers=12):
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

    def get_pull_requests(self, repo_name, start_date, end_date, max_workers=12):
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
                essential_pull_requests.append({
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'creator': pr['user']['login'],
                    'comments': comments
                })
        return essential_pull_requests

    def get_branches(self, repo_name, max_workers=12):
        url = f'https://api.github.com/repos/{repo_name}/branches'
        branches = self.get_all_pages(url, 'Fetching branches', max_workers=max_workers)
        essential_branches = [{
            'name': branch['name'],
            'sha': branch['commit']['sha']
        } for branch in branches if 'name' in branch and 'commit' in branch and 'sha' in branch['commit']]
        return essential_branches

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

