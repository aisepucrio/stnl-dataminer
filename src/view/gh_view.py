import customtkinter as ctk
import threading
from controller.gh_controller import GitHubController
from view.base_view import BaseView

# Classe para a aplicação de mineração de dados do GitHub
class GitHubApp(BaseView):
    def __init__(self, menu_app):
        super().__init__(menu_app, title="GitHub Data Miner", url_label="Repository URL", url_placeholder='Enter GitHub repository URL')
        self.controller = GitHubController(self) 
        self.center_window()

        # Definir valor padrão para o campo de entrada de URL
        self.url_entry.insert(0, "https://github.com/aisepucrio/stnl-dataminer")
        
        # Adiciona opções de mineração específicas do GitHub
        self.commits_switch = ctk.CTkSwitch(self.mining_options_frame, text="Commits", font=self.default_font)
        self.commits_switch.pack(pady=5, padx=20, anchor='w')
        self.issues_switch = ctk.CTkSwitch(self.mining_options_frame, text="Issues", font=self.default_font)
        self.issues_switch.pack(pady=5, padx=20, anchor='w')
        self.pull_requests_switch = ctk.CTkSwitch(self.mining_options_frame, text="Pull Requests", font=self.default_font)
        self.pull_requests_switch.pack(pady=5, padx=20, anchor='w')
        self.branches_switch = ctk.CTkSwitch(self.mining_options_frame, text="Branches", font=self.default_font)
        self.branches_switch.pack(pady=5, padx=20, anchor='w')

    # Função para iniciar a mineração de dados
    def mine_data(self):
        repo_url = self.url_entry.get()
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        max_workers = self.controller.max_workers_default 

        options = {
            'commits': self.commits_switch.get() == 1,
            'issues': self.issues_switch.get() == 1,
            'pull_requests': self.pull_requests_switch.get() == 1,
            'branches': self.branches_switch.get() == 1
        }

        # Função para coletar dados em uma thread separada
        def collect_data():
            try:

                self.result_label.configure(text="Retrieving information, please wait...")

                total_tasks = sum(options.values())
                self.progress_bar.set(0)
                progress_step = 1 / total_tasks if total_tasks > 0 else 1

                data = self.controller.collect_data(repo_url, start_date, end_date, options, max_workers, self.update_progress, progress_step)
                message = ""
                message += f"Commits: {len(data.get('commits', []))}\n"
                message += f"Issues: {len(data.get('issues', []))}\n"
                message += f"Pull Requests: {len(data.get('pull_requests', []))}\n"
                message += f"Branches: {len(data.get('branches', []))}\n"

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