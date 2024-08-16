import os
from controller.base_controller import BaseController
from model.jira_api import JiraAPI
#from database.database import Database
from dotenv import load_dotenv
from tkinter import messagebox

# Controlador para interação com Jira
class JiraController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.api = JiraAPI()
        self.loaded_issue_types = []

    # Método para carregar tipos de issue no dropdown
    def load_issue_types(self, url):
        jira_domain, project_key = self.api.extract_jira_domain_and_key(url)
        issuetypes = self.api.get_issuetypes(jira_domain, self.api.email, self.api.api_token)
        if not issuetypes:
            messagebox.showerror("Error", f"Could not fetch issue types for project '{project_key}'.")
            return []
        print(f"Loaded issue types: {issuetypes}")
        self.loaded_issue_types = issuetypes
        return self.loaded_issue_types

    # Método para minerar dados do Jira
    def mine_data(self, url, start_date, end_date, task_types, update_progress_callback=None, progress_step=None):
        # Recarrega as variáveis de ambiente antes de iniciar a mineração
        self.reload_env()
        self.stop_process_flag = False

        jira_domain, project_key = self.api.extract_jira_domain_and_key(url)
        start_date = self.view.start_date_entry.get_date()
        end_date = self.view.end_date_entry.get_date()
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        if not task_types:
            messagebox.showerror("Error", "Please select at least one issue type.")
            return None
        
        # Verifica se os tipos de issue existem no projeto
        if not self.loaded_issue_types:
            messagebox.showerror("Error", f"Could not fetch issue types for project '{project_key}'.")
            return None
        
        valid_task_types = list(self.loaded_issue_types.values())
        print(f"Valid task types: {valid_task_types}")
        invalid_task_types = [task_type for task_type in task_types if task_type not in valid_task_types]

        if invalid_task_types:
            messagebox.showinfo("Info", f"The following issue types are not found in the project '{project_key}': {', '.join(invalid_task_types)}. They will be skipped.")

        custom_field_mapping = self.api.search_custom_fields(jira_domain)

        all_issues = {}
        for task_type in task_types:
            if task_type not in valid_task_types:
                continue  # Pula tipos de issue inválidos

            if self.stop_process_flag:
                print("Data collection stopped by user.")
                messagebox.showinfo("Stopped", "Data collection was stopped by the user.")
                return None
            print(f"Collecting {task_type}s...")
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
