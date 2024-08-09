import customtkinter as ctk
import threading
from controller.jira_controller import JiraController
from view.base_view import BaseView
from PIL import Image

# Classe para a aplicação de mineração de dados do Jira
class JiraApp(BaseView):
    def __init__(self, menu_app):
        super().__init__(menu_app, title="Jira Data Miner", url_label="Project URL", url_placeholder="Enter Jira project URL")
        self.controller = JiraController(self)
        self.center_window()

        # Definir valor padrão para o campo de entrada de URL
        #self.url_entry.insert(0, "https://stone-puc.atlassian.net/jira/software/c/projects/CSTONE/boards/3?isInsightsOpen=true")
        self.url_entry.insert(0, "https://spark-project.atlassian.net/jira/software/c/projects/SPARK/issues")

        # Botão para carregar tipos de issues adicionais (com ícone, se disponível)
        #self.load_issues_icon = ctk.CTkImage(light_image=Image.open(r"view/icons/close.png"), size=(20, 20))
        self.load_issues_button = ctk.CTkButton(self, text="", command=self.load_issue_types, width=25, height=25) # Adicionar image=self.load_issues_icon
        self.load_issues_button.grid(row=2, column=1, padx=(5, 10), pady=7, sticky='e')

        # Adiciona opções de mineração específicas do Jira
        self.epics_switch = ctk.CTkSwitch(self.mining_options_frame, text="Epics", font=self.default_font)
        self.epics_switch.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        self.user_stories_switch = ctk.CTkSwitch(self.mining_options_frame, text="User Stories", font=self.default_font)
        self.user_stories_switch.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        self.tasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Tasks", font=self.default_font)
        self.tasks_switch.grid(row=2, column=0, padx=20, pady=5, sticky='w')
        self.subtasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Sub-tasks", font=self.default_font)
        self.subtasks_switch.grid(row=3, column=0, padx=20, pady=5, sticky='w')
        self.bugs_switch = ctk.CTkSwitch(self.mining_options_frame, text="Bugs", font=self.default_font)
        self.bugs_switch.grid(row=4, column=0, padx=20, pady=5, sticky='w')

        # Frame para os tipos de issue adicionais
        self.additional_issues_label = ctk.CTkLabel(self.additional_issues_frame, text="Additional Task Types", font=self.default_font)
        self.additional_issues_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        # Lista para armazenar os estados dos CTkCheckBox
        self.additional_issues_vars = []

    # Função para carregar tipos de issues adicionais
    def load_issue_types(self):
        url = self.url_entry.get()
        issue_types = self.controller.load_issue_types(url)
        standard_types = ['Epic', 'Story', 'Task', 'Sub-task', 'Bug']
        additional_types = [untranslated_name for translated_name, untranslated_name in issue_types.items() if untranslated_name not in standard_types]
        
        print(f"Additional types: {additional_types}")  # Debug statement

        # Limpa o frame antes de adicionar novos itens
        for widget in self.additional_issues_frame.winfo_children():
            widget.destroy()
        self.additional_issues_vars.clear()

        for item in additional_types:
            var = ctk.StringVar(value=item)
            chk = ctk.CTkCheckBox(self.additional_issues_frame, text=item, variable=var, onvalue=item, offvalue='')
            chk.pack(anchor='w', padx=10, pady=5)
            self.additional_issues_vars.append(var)

    # Função para obter os itens selecionados no CTkCheckBox
    def get_selected_additional_task_types(self):
        return [var.get() for var in self.additional_task_types_vars if var.get()]

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