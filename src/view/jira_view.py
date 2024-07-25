import customtkinter as ctk
import threading
from controller.jira_controller import JiraController
from view.base_view import BaseView

# Classe para a aplicação de mineração de dados do Jira
class JiraApp(BaseView):
    def __init__(self, menu_app):
        super().__init__(menu_app, title="Jira Data Miner", url_label="Project URL", url_placeholder="Enter Jira project URL")
        self.controller = JiraController(self)
        self.center_window()

        # Adiciona opções de mineração específicas do Jira
        self.epics_switch = ctk.CTkSwitch(self.mining_options_frame, text="Epics", font=self.default_font)
        self.epics_switch.pack(pady=5, padx=20, anchor='w')
        self.user_stories_switch = ctk.CTkSwitch(self.mining_options_frame, text="User Stories", font=self.default_font)
        self.user_stories_switch.pack(pady=5, padx=20, anchor='w')
        self.tasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Tasks", font=self.default_font)
        self.tasks_switch.pack(pady=5, padx=20, anchor='w')
        self.subtasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Sub-tasks", font=self.default_font)
        self.subtasks_switch.pack(pady=5, padx=20, anchor='w')
        self.bugs_switch = ctk.CTkSwitch(self.mining_options_frame, text="Bugs", font=self.default_font)
        self.bugs_switch.pack(pady=5, padx=20, anchor='w')
        self.enablers_switch = ctk.CTkSwitch(self.mining_options_frame, text="Enablers", font=self.default_font)
        self.enablers_switch.pack(pady=5, padx=20, anchor='w')

    # Função para iniciar a mineração de dados
    def mine_data(self):
        url = self.url_entry.get()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        task_types = []
        if self.epics_switch.get() == 1:
            task_types.append('Epic')
        if self.user_stories_switch.get() == 1:
            task_types.append('Story')
        if self.tasks_switch.get() == 1:
            task_types.append('Task')
        if self.subtasks_switch.get() == 1:
            task_types.append('Sub-task')
        if self.bugs_switch.get() == 1:
            task_types.append('Bug')
        if self.enablers_switch.get() == 1:
            task_types.append('Enabler')

        # Função para coletar dados em uma thread separada
        def collect_data():
            try:
                self.result_label.configure(text="Retrieving information, please wait...")

                total_tasks = len(task_types)
                self.progress_bar.set(0)
                progress_step = 1 / total_tasks if total_tasks > 0 else 1

                data = self.controller.mine_data(url, start_date, end_date, task_types, self.update_progress, progress_step)
                message = ""
                for task_type, tasks in data.items():
                    message += f"{task_type}: {len(tasks)}\n"
                self.result_label.configure(text=message.strip())
            except ValueError as ve:
                self.result_label.configure(text=str(ve))
                
        thread = threading.Thread(target=collect_data)
        thread.start()

    # Função para atualizar a barra de progresso
    def update_progress(self, step):
        current_value = self.progress_bar.get()
        self.progress_bar.set(current_value + step)

    # Função para parar o processo
    def stop_process(self):
        self.controller.stop_process()
        self.result_label.configure(text="Process stopped by the user.")