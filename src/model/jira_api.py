import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from model.base_api import BaseAPI
from requests.auth import HTTPBasicAuth
import re

# Classe para interações com a API do Jira
class JiraAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.reload_env()
        self.email = os.getenv('EMAIL')
        self.api_token = os.getenv('API_TOKEN')

    # Método para validar o token do Jira
    def validate_jira_token(self, api_token):
        # Define o padrão regex para o token fornecido
        padrao = r'^ATATT3xFfGF0[a-zA-Z0-9_\-]+=[0-9A-F]+$'
        
        # Verifica se o token corresponde ao padrão
        return bool(re.match(padrao, api_token))

    # Método para recarregar variáveis de ambiente
    def reload_env(self):
        super().reload_env()
        self.email = os.getenv('EMAIL')
        self.api_token = os.getenv('API_TOKEN')

    # Extrai domínio e chave do projeto Jira a partir da URL
    def extract_jira_domain_and_key(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_parts = parsed_url.path.split('/')
        
        project_key = None
        
        if 'projects' in path_parts:
            # Caso da URL 1 e URL 2
            project_key = path_parts[path_parts.index('projects') + 1]
        elif 'browse' in path_parts:
            # Caso da URL 3
            project_key = path_parts[path_parts.index('browse') + 1].split('-')[0]
        
        return domain, project_key

    # Busca campos customizados do Jira
    def search_custom_fields(self, jira_domain):
        self.reload_env()
        url = f"https://{jira_domain}/rest/api/2/field"
        auth = (self.email, self.api_token)
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        fields = response.json()
        return {field['id']: field['name'] for field in fields if field['id'].startswith('customfield')}
    
    # Busca tipos de tarefas do Jira
    def get_issuetypes(self, jira_domain, email, api_token):
        url = f"https://{jira_domain}/rest/api/3/issuetype"
        
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_token))
            response.raise_for_status()  # Lança uma exceção para códigos de status HTTP de erro
            issuetypes = response.json()
            
            # Filtra e remove duplicados com base no campo `name`
            unique_issuetypes = {}
            for issuetype in issuetypes:
                name = issuetype.get('name')
                #print(f"Name: {name}")
                untranslated_name = issuetype.get('untranslatedName')
                #print(f"Untranslated Name: {untranslated_name}")
                if name and untranslated_name and name not in unique_issuetypes:
                    unique_issuetypes[name] = untranslated_name
                #print(f"Unique: {unique_issuetypes}")
            return unique_issuetypes
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar: {e}")
            return None

    # Coleta tarefas do Jira
    def collect_tasks(self, jira_domain, project_key, task_type, start_date, end_date, stop_collecting):
        self.reload_env()
        all_issues = []
        start_at = 0
        max_results = 50

        jql = f'project={project_key} AND issuetype="{task_type}"'
        #print(f"Collecting tasks with JQL: {jql}")
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
            auth = HTTPBasicAuth(self.email, self.api_token)
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