import customtkinter as ctk
import threading
from controller.jira_controller import JiraController
from view.base_view import BaseView
from tkinter import Listbox, MULTIPLE

# Classe para a aplicação de mineração de dados do Jira
class JiraApp(BaseView):
    def __init__(self, menu_app):
        super().__init__(menu_app, title="Jira Data Miner", url_label="Project URL", url_placeholder="Enter Jira project URL")
        self.controller = JiraController(self)
        self.center_window()

        # Definir valor padrão para o campo de entrada de URL
        #self.url_entry.insert(0, "https://stone-puc.atlassian.net/jira/software/c/projects/CSTONE/boards/3?isInsightsOpen=true")
        self.url_entry.insert(0, "https://spark-project.atlassian.net/jira/software/c/projects/SPARK/issues")
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

        # Botão para carregar tipos de issues adicionais
        self.load_types_button = ctk.CTkButton(self, text="Load Issue Types", command=self.load_issue_types, font=self.default_font, corner_radius=8)
        self.load_types_button.pack(pady=7, padx=10)

        # Listbox para tipos de issue adicionais
        self.additional_task_types_label = ctk.CTkLabel(self, text="Additional Task Types", font=self.default_font)
        self.additional_task_types_label.pack(pady=5, padx=10)
        self.additional_task_types = Listbox(self, selectmode=MULTIPLE, font=self.default_font)
        self.additional_task_types.pack(pady=7, padx=10)

    # Função para carregar tipos de issues adicionais
    def load_issue_types(self):
        url = self.url_entry.get()
        issue_types = self.controller.load_issue_types(url)
        standard_types = ['Epic', 'Story', 'Task', 'Sub-task', 'Bug']
        additional_types = [untranslated_name for translated_name, untranslated_name in issue_types.items() if untranslated_name not in standard_types]
        
        print(f"Additional types: {additional_types}")  # Debug statement

        self.additional_task_types.delete(0, 'end')  # Limpa a listbox antes de adicionar novos itens
        for item in additional_types:
            self.additional_task_types.insert('end', item)
        if additional_types:
            self.additional_task_types.selection_set(0)  # Define o valor padrão para o primeiro item

    # Função para obter os itens selecionados no Listbox
    def get_selected_additional_task_types(self):
        return [self.additional_task_types.get(i) for i in self.additional_task_types.curselection()]

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

        additional_task_types = self.get_selected_additional_task_types()
        print(f"Additional task types: {additional_task_types}")

        # Função para coletar dados em uma thread separada
        def collect_data():
            try:
                self.result_label.configure(text="Retrieving information, please wait...")

                total_tasks = len(task_types) + len(additional_task_types)
                self.progress_bar.set(0)
                progress_step = 1 / total_tasks if total_tasks > 0 else 1

                data = self.controller.mine_data(url, start_date, end_date, task_types, additional_task_types, self.update_progress, progress_step)
                if data is None:
                    self.result_label.configure(text="Process stopped by the user.")
                    return

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