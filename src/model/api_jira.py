import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import json

load_dotenv()

EMAIL = os.getenv('EMAIL')
API_TOKEN = os.getenv('API_TOKEN')

def extract_jira_domain_and_key(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path_parts = parsed_url.path.split('/')
    project_key = path_parts[path_parts.index('projects') + 1] if 'projects' in path_parts else None
    return domain, project_key

def identify_platform(url):
    if 'atlassian.net' in url:
        return 'jira'
    elif 'github.com' in url:
        return 'github'
    return None

def search_custom_fields(jira_domain, auth):
    url = f"https://{jira_domain}/rest/api/2/field"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    fields = response.json()
    return {field['id']: field['name'] for field in fields if field['id'].startswith('customfield')}

def collect_tasks(jira_domain, project_key, task_type, auth, start_date, end_date, stop_collecting):
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
        response = requests.get(url, params=query, auth=auth)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error response: {response.text}")
            raise e
        issues = response.json()['issues']
        all_issues.extend(issues)
        start_at += max_results
        if len(issues) < max_results:
            break

    return all_issues

def remove_null_fields(issues):
    if not issues:
        return issues

    keys_to_remove = set(issues[0]['fields'].keys())
    for issue in issues:
        keys_to_remove &= {key for key, value in issue['fields'].items() if value is None}

    for issue in issues:
        for key in keys_to_remove:
            del issue['fields'][key]

    return issues

def replace_ids(issues, custom_field_mapping):
    for issue in issues:
        fields = issue['fields']
        for field_id, field_name in custom_field_mapping.items():
            if field_id in fields:
                fields[field_name] = fields.pop(field_id)
    return issues

def save_to_json(data, filename):
    load_dotenv()  # Recarregar as variáveis de ambiente
    save_path = os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Desktop"))
    full_path = os.path.join(save_path, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
