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

        # Inicializa com as opções de mineração padrão
        self.init_default_mining_options()

        # Inicializar variável para a URL
        self.last_url = ""

        # Inicializar variável para os tipos de issues
        self.last_issuetypes = {}

        # Iniciar monitoramento da URL
        self.monitor_url()

        # Definir valor padrão para o campo de entrada de URL
        #self.url_entry.insert(0, "https://stone-puc.atlassian.net/jira/software/c/projects/CSTONE/boards/3?isInsightsOpen=true")
        self.url_entry.insert(0, "https://spark-project.atlassian.net/jira/software/c/projects/SPARK/issues")

    def init_default_mining_options(self):
        # Inicializa switches padrão
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

    def update_mining_options(self, issue_types):
        # Limpar os switches existentes
        for widget in self.mining_options_frame.winfo_children():
            widget.destroy()

        # Recriar switches para todos os tipos disponíveis no projeto
        row_index = 0
        for translated_name, untranslated_name in issue_types.items():
            switch = ctk.CTkSwitch(self.mining_options_frame, text=untranslated_name, font=self.default_font)
            switch.grid(row=row_index, column=0, padx=20, pady=5, sticky='w')
            row_index += 1

    def monitor_url(self):
        # Monitora a URL e tenta carregar os tipos de issues se for válida
        current_url = self.url_entry.get()
        if current_url != self.last_url:
            self.last_url = current_url  
            jira_domain, project_key = self.controller.api.extract_jira_domain_and_key(current_url)
            if jira_domain and project_key:
                issuetypes = self.controller.load_issue_types(current_url)
                if issuetypes != self.last_issuetypes:
                    self.last_issuetypes = issuetypes
                    self.update_mining_options(issuetypes)
        self.after(3000, self.monitor_url)  # Verifica a URL a cada 3 segundo

    # Função para iniciar a mineração de dados
    def mine_data(self):
        url = self.url_entry.get()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        task_types = []
        for widget in self.mining_options_frame.winfo_children():
            if isinstance(widget, ctk.CTkSwitch):
                if widget.get() == 1:
                    task_types.append(widget.cget("text"))

        # Função para coletar dados em uma thread separada
        def collect_data():
            try:
                self.result_label.configure(text="Retrieving information, please wait...")

                total_tasks = len(task_types)
                self.progress_bar.set(0)
                progress_step = 1 / total_tasks if total_tasks > 0 else 1

                data = self.controller.mine_data(url, start_date, end_date, task_types, self.update_progress, progress_step)
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