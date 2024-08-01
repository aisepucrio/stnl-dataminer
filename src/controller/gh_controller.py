import os
from controller.base_controller import BaseController
from model.gh_api import GitHubAPI
from database.database import Database
from dotenv import load_dotenv
from tkinter import messagebox

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Controlador para interação com GitHub
class GitHubController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
        print(int(os.getenv('USE_DATABASE')))
        self.db = Database() if int(os.getenv('USE_DATABASE')) else None
        self.verify_database_credentials()
        self.max_workers_default = int(os.getenv('MAX_WORKERS', '4'))
        self.api = GitHubAPI(view)

    def verify_database_credentials(self):
        if self.db is not None and (self.db.conn is None and self.db.cursor is None):
            self.db = None

    # Método para coletar dados do repositório GitHub
    def collect_data(self, repo_url, start_date, end_date, options, max_workers=None, update_progress_callback=None, progress_step=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        repo_name = self.api.get_repo_name(repo_url)

        if self.db:
            self.db.create_schema_and_tables(repo_name)
        else:
            print("Skipping database operations due to connection issues.")
        
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
            if self.db:
                self.db.insert_commits(repo_name, data['commits'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de issues
        if options.get('issues'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['issues'] = self.api.get_issues(repo_name, start_date_iso, end_date_iso, max_workers)
            if self.db:
                self.db.insert_issues(repo_name, data['issues'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de pull requests
        if options.get('pull_requests'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['pull_requests'] = self.api.get_pull_requests(repo_name, start_date_iso, end_date_iso, max_workers)
            if self.db:
                self.db.insert_pull_requests(repo_name, data['pull_requests'])
            if update_progress_callback:
                self.view.after(0, update_progress_callback, progress_step)

        # Coleta de branches
        if options.get('branches'):
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                return
            data['branches'] = self.api.get_branches(repo_name, max_workers)
            if self.db:
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
