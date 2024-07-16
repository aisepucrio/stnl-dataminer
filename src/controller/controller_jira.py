# controller_jira.py
from model.api_jira import JiraAPI
from tkinter import messagebox
from dotenv import load_dotenv
import os

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
