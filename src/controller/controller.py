from model.api import GitHubAPI, JiraAPI
from database.database_gh import Database
from dotenv import load_dotenv
from tkinter import messagebox
import os

load_dotenv()

class GitHubController:
    def __init__(self):
        self.api = GitHubAPI()
        self.db = Database()
        self.stop_process_flag = False
        self.max_workers_default = int(os.getenv('MAX_WORKERS', '12'))
        load_dotenv()

    def get_save_path(self):
        load_dotenv()  # Recarregar as variáveis de ambiente
        return os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Desktop"))

    def collect_data(self, repo_url, start_date, end_date, options, max_workers=None, update_progress_callback=None, progress_step=None):
        if max_workers is None:
            max_workers = self.max_workers_default
        print(f"Number of workers being used: {max_workers}")
        repo_name = self.api.get_repo_name(repo_url)
        self.db.create_schema_and_tables(repo_name)
        
        start_date_iso = start_date.strftime('%Y-%m-%d') + 'T00:00:01Z'
        end_date_iso = end_date.strftime('%Y-%m-%d') + 'T23:59:59Z'

        data = {}

        if options.get('commits'):
            data['commits'] = self.api.get_commits(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_commits(repo_name, data['commits'])
            update_progress_callback(progress_step)

        if options.get('issues'):
            data['issues'] = self.api.get_issues(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_issues(repo_name, data['issues'])
            update_progress_callback(progress_step)

        if options.get('pull_requests'):
            data['pull_requests'] = self.api.get_pull_requests(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_pull_requests(repo_name, data['pull_requests'])
            update_progress_callback(progress_step)

        if options.get('branches'):
            data['branches'] = self.api.get_branches(repo_name, max_workers)
            self.db.insert_branches(repo_name, data['branches'])
            update_progress_callback(progress_step)

        save_path = self.get_save_path()
        file_path = os.path.join(save_path, f"{repo_name.replace('/', '_').replace('-', '_')}.json")
        self.api.save_to_json(data, file_path)
        
        return data

    def stop_process(self):
        self.stop_process_flag = True

class JiraController:
    def __init__(self, view):
        self.view = view
        self.api = JiraAPI()
        self.stop_collecting = False
        load_dotenv()

    def get_save_path(self):
        load_dotenv()  # Recarregar as variáveis de ambiente
        return os.getenv('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Desktop"))

    def confirm_selection(self):
        url = self.view.url_entry.get().strip()
        platform = self.api.identify_platform(url)

        if platform == 'jira':
            jira_domain, project_key = self.api.extract_jira_domain_and_key(url)
            self.view.show_jira_options(jira_domain, project_key)
        elif platform == 'github':
            repo_url = url  # Aqui você pode implementar a lógica para extrair o nome do repositório do GitHub
            self.view.show_github_options(url)
        else:
            messagebox.showerror("Error", "Invalid URL. Please enter a valid Jira or GitHub URL.")

    def stop_mining(self):
        self.stop_collecting = True

    def mine_data_jira(self, jira_domain, project_key):
        start_date = self.view.start_date_entry.get_date()
        end_date = self.view.end_date_entry.get_date()
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        task_types = []
        if self.view.epics_switch.get():
            task_types.append('Epic')
        if self.view.user_stories_switch.get():
            task_types.append('Story')
        if self.view.tasks_switch.get():
            task_types.append('Task')
        if self.view.subtasks_switch.get():
            task_types.append('Sub-task')
        if self.view.bugs_switch.get():
            task_types.append('Bug')
        if self.view.enablers_switch.get():
            task_types.append('Enabler')

        if not task_types:
            messagebox.showerror("Error", "Please select at least one issue type.")
            return

        custom_field_mapping = self.api.search_custom_fields(jira_domain)

        all_issues = {}
        for task_type in task_types:
            if self.stop_collecting:
                print("Data collection stopped by user.")
                messagebox.showinfo("Stopped", "Data collection was stopped by the user.")
                return

            tasks = self.api.collect_tasks(jira_domain, project_key, task_type, start_date_str, end_date_str, lambda: self.stop_collecting)
            tasks = self.api.remove_null_fields(tasks)
            tasks = self.api.replace_ids(tasks, custom_field_mapping)
            all_issues[task_type] = tasks
            print(f"Collected {len(tasks)} {task_type}(s)")

        save_path = self.get_save_path()
        self.api.save_to_json(all_issues, os.path.join(save_path, f'{project_key.lower()}_issues.json'))
        messagebox.showinfo("Success", f"Data has been successfully mined and saved to {os.path.join(save_path, project_key.lower() + '_issues.json')}")