import os
from controller.base_controller import BaseController
from model.jira_api import JiraAPI
#from database.database import Database
from dotenv import load_dotenv
from tkinter import messagebox

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Controlador para interação com Jira
class JiraController(BaseController):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.api = JiraAPI()

    # Método para minerar dados do Jira
    def mine_data(self, url, start_date, end_date, task_types, update_progress_callback=None, progress_step=None):
        self.stop_process_flag = False

        jira_domain, project_key = self.api.extract_jira_domain_and_key(url)
        start_date = self.view.start_date_entry.get_date()
        end_date = self.view.end_date_entry.get_date()
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        if not task_types:
            messagebox.showerror("Error", "Please select at least one issue type.")
            return None

        custom_field_mapping = self.api.search_custom_fields(jira_domain)

        all_issues = {}
        for task_type in task_types:
            if self.stop_process_flag:
                print("Data collection stopped by user.")
                messagebox.showinfo("Stopped", "Data collection was stopped by the user.")
                return None

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
