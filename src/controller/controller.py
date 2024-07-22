from model.api import GitHubAPI, JiraAPI
from database.database import Database
from dotenv import load_dotenv
from tkinter import messagebox
import os
import json

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Classe base para controladores
class BaseController:
    def __init__(self):
        # Carrega variáveis de ambiente do arquivo .env
        load_dotenv()
        # Flag para parar o processo
        self.stop_process_flag = False

    # Método para obter o caminho de salvamento dos dados
    def get_save_path(self):
        # Recarregar as variáveis de ambiente
        load_dotenv()
        # Retorna o caminho de salvamento, padrão é a pasta Downloads do usuário
        return os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Downloads"))

    # Método para salvar dados em formato JSON
    def save_to_json(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    # Método para parar o processo de coleta de dados
    def stop_process(self):
        self.stop_process_flag = True

# Controlador para interação com GitHub
class GitHubController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.db = Database()
        self.max_workers_default = int(os.getenv('MAX_WORKERS', '4'))
        self.api = GitHubAPI(view)

    # Método para coletar dados do repositório GitHub
    def collect_data(self, repo_url, start_date, end_date, options, max_workers=None, update_progress_callback=None, progress_step=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        repo_name = self.api.get_repo_name(repo_url)
        self.db.create_schema_and_tables(repo_name)
        
        # Formata as datas de início e fim no formato ISO
        start_date_iso = start_date.strftime('%Y-%m-%d') + 'T00:00:01Z'
        end_date_iso = end_date.strftime('%Y-%m-%d') + 'T23:59:59Z'

        data = {}

        # Coleta de commits
        if options.get('commits'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['commits'] = self.api.get_commits_pydriller(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_commits(repo_name, data['commits'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de issues
        if options.get('issues'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['issues'] = self.api.get_issues(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_issues(repo_name, data['issues'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de pull requests
        if options.get('pull_requests'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['pull_requests'] = self.api.get_pull_requests(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_pull_requests(repo_name, data['pull_requests'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de branches
        if options.get('branches'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['branches'] = self.api.get_branches(repo_name, max_workers)
            self.db.insert_branches(repo_name, data['branches'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Salva os dados coletados em um arquivo JSON
        save_path = self.get_save_path()
        print(f'Saving data to {save_path}')
        file_path = os.path.join(save_path, f"{repo_name.replace('/', '_').replace('-', '_')}.json")
        print(f'Saving data to {file_path}')
        self.save_to_json(data, file_path)
        messagebox.showinfo("Success", f"Data has been successfully mined and saved to {file_path}")
        
        return data

# Controlador para interação com Jira
class JiraController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.api = JiraAPI()

    # Método para minerar dados do Jira
    def mine_data(self, url, start_date, end_date, task_types, update_progress_callback=None, progress_step=None):
        jira_domain, project_key = self.api.extract_jira_domain_and_key(url)
        start_date = self.view.start_date_entry.get_date()
        end_date = self.view.end_date_entry.get_date()
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        if not task_types:
            messagebox.showerror("Error", "Please select at least one issue type.")
            return

        custom_field_mapping = self.api.search_custom_fields(jira_domain)

        all_issues = {}
        for task_type in task_types:
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                messagebox.showinfo("Stopped", "Data collection was stopped by the user.")
                return

            tasks = self.api.collect_tasks(jira_domain, project_key, task_type, start_date_str, end_date_str, lambda: self.stop_process_flag)
            tasks = self.api.remove_null_fields(tasks)
            tasks = self.api.replace_ids(tasks, custom_field_mapping)
            all_issues[task_type] = tasks

            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

            print(f"Collected {len(tasks)} {task_type}(s)")

        # Salva os dados coletados em um arquivo JSON
        save_path = self.get_save_path()
        self.api.save_to_json(all_issues, os.path.join(save_path, f'{project_key.lower()}_issues.json'))
        messagebox.showinfo("Success", f"Data has been successfully mined and saved to {os.path.join(save_path, project_key.lower() + '_issues.json')}")

        return all_issues
