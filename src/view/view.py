import customtkinter as ctk
import threading
import tkinter as tk
import os
import platform
from tkcalendar import DateEntry
from tkinter import PhotoImage
from PIL import Image, ImageTk, ImageDraw
from controller.controller import GitHubController, JiraController   
from dotenv import load_dotenv, set_key, dotenv_values
from tkinter import font as tkfont, messagebox, Toplevel, Listbox, filedialog

# Classe BaseView que serve como base para outras visualizações
class BaseView(ctk.CTk):
    def __init__(self, menu_app, title, url_label, url_placeholder):
        super().__init__()

        # Inicializa as variáveis principais da aplicação
        self.menu_app = menu_app
        self.title(title)
        self.width = 550
        self.height = 770
        self.geometry(f'{self.width}x{self.height}')
        self.configure(bg="black")

        # Adiciona um botão de voltar para navegar de volta ao menu
        self.back_button = ctk.CTkButton(
            self, text="← Back", command=self.back_to_menu,
            corner_radius=8, fg_color="#2e2e2e", hover_color="#4a4a4a",
            text_color="#ffffff", width=80, height=32, font=("Segoe UI", 12, "bold")
        )
        self.back_button.pack(pady=7, padx=10, anchor='nw')

        # Define a fonte padrão
        self.default_font = ctk.CTkFont(family="Segoe UI", size=12)

        # Rótulo e campo de entrada para URL
        self.url_label = ctk.CTkLabel(self, text=url_label, font=self.default_font)
        self.url_label.pack(pady=5)
        self.url_entry = ctk.CTkEntry(self, placeholder_text=url_placeholder, width=400, font=self.default_font)
        self.url_entry.pack(pady=7, padx=10)

        # Rótulos e campos de entrada para datas
        self.start_date_label = ctk.CTkLabel(self, text="Start Date (DD/MM/YYYY)", font=self.default_font)
        self.start_date_label.pack(pady=5, padx=10)
        self.start_date_entry = DateEntry(self, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(pady=7, padx=10)

        self.end_date_label = ctk.CTkLabel(self, text="End Date (DD/MM/YYYY)", font=self.default_font)
        self.end_date_label.pack(pady=5, padx=10)
        self.end_date_entry = DateEntry(self, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(pady=7, padx=10)

        # Frame para as opções de mineração
        self.mining_options_frame = ctk.CTkFrame(self)
        self.mining_options_frame.pack(pady=20)

        # Botão para iniciar a mineração de dados
        self.mine_button = ctk.CTkButton(self, text="Mine Data", command=self.mine_data, font=self.default_font, corner_radius=8)
        self.mine_button.pack(pady=7, padx=10)

        # Botão para parar o processo
        self.stop_button = ctk.CTkButton(self, text="Stop", command=self.stop_process, font=self.default_font, corner_radius=8, fg_color="red")
        self.stop_button.pack(pady=7, padx=10)

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0)

        # Rótulo para mostrar os resultados
        self.result_label = ctk.CTkLabel(self, text="", font=self.default_font)
        self.result_label.pack(pady=12, padx=10)

    # Função para mostrar uma mensagem temporária
    def show_temp_message(self, message, duration=3000):
        temp_label = ctk.CTkLabel(self, text=message, font=self.default_font)
        temp_label.pack(pady=12, padx=10)
        self.after(duration, temp_label.destroy)

    # Função para centralizar a janela na tela
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.width // 2)
        y = (self.winfo_screenheight() // 2) - (self.height // 2)
        self.geometry(f'{self.width}x{self.height}+{x}+{y}')

    # Função para voltar ao menu
    def back_to_menu(self):
        self.menu_app.deiconify()
        self.destroy()

    # Função de mineração de dados (a ser implementada nas subclasses)
    def mine_data(self):
        pass

    # Função para parar o processo (a ser implementada nas subclasses)
    def stop_process(self):
        pass

    # Função para executar a aplicação
    def run(self):
        self.mainloop()

# Classe para a aplicação de mineração de dados do Jira
class JiraDataMinerApp(BaseView):
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

# Classe para a aplicação de mineração de dados do GitHub
class GitHubRepoInfoApp(BaseView):
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

# Classe personalizada de Listbox
class CTkListbox(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.listbox = Listbox(self, bg='#2e2e2e', fg='#d4d4d4', highlightbackground='#3e3e3e', selectbackground='#3a7bd5', selectforeground='white', bd=0, relief='flat')
        self.listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
    def insert(self, *args):
        self.listbox.insert(*args)
        
    def delete(self, *args):
        self.listbox.delete(*args)
        
    def curselection(self):
        return self.listbox.curselection()
        
    def get(self, *args):
        return self.listbox.get(*args)

# Classe para a aplicação de configurações
class SettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Settings")
        self.geometry("800x600")  # Definindo dimensões específicas da janela
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.button_color = "#1e1e1e"

        # Adicionar o atributo para rastrear o estado do menu
        self.menu_window = None  # Adicionado para rastrear o estado do menu

        # Carrega variáveis de ambiente
        self.env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
        self.load_env()

        self.create_widgets()

        self.center_window()  # Centraliza a janela após criação dos widgets

        self.bind('<Unmap>', self.check_window_state)
        self.bind('<Map>', self.check_window_state)
        self.bind("<Configure>", self.on_window_move)

    def center_window(self):
        self.update_idletasks()
        width = 700  # Largura desejada
        height = 300  # Altura desejada
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # Função para carregar as variáveis de ambiente
    def load_env(self):
        default_env_content = """TOKENS=
USERNAMES=
EMAIL=
API_TOKEN=
SAVE_PATH=
MAX_WORKERS='4'
PG_HOST=opus.servehttp.com
PG_DATABASE=aise-stone
PG_USER=aise-stone
PG_PASSWORD=#St@n3L@b2@24!
PG_PORT=54321
"""
        if not os.path.exists(self.env_file):
            with open(self.env_file, 'w') as f:
                f.write(default_env_content)

        load_dotenv(self.env_file)

        env_values = dotenv_values(self.env_file)
        self.tokens = env_values.get('TOKENS', '').split(',')
        self.usernames = env_values.get('USERNAMES', '').split(',')
        self.emails = env_values.get('EMAIL', '').split(',')
        self.api_tokens = env_values.get('API_TOKEN', '').split(',')
        self.save_path = env_values.get('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Downloads"))
        max_workers_str = env_values.get('MAX_WORKERS', '4')
        self.max_workers = int(max_workers_str) if max_workers_str else 1

        # Garante que todas as chaves necessárias estão presentes no arquivo .env
        self.ensure_env_key('TOKENS')
        self.ensure_env_key('USERNAMES')
        self.ensure_env_key('EMAIL')
        self.ensure_env_key('API_TOKEN')
        self.ensure_env_key('SAVE_PATH')
        self.ensure_env_key('MAX_WORKERS', '4')
        self.ensure_env_key('PG_HOST', 'opus.servehttp.com')
        self.ensure_env_key('PG_DATABASE', 'aise-stone')
        self.ensure_env_key('PG_USER', 'aise-stone')
        self.ensure_env_key('PG_PASSWORD', '#St@n3L@b2@24!')
        self.ensure_env_key('PG_PORT', '54321')

    # Função para garantir que uma chave está presente no arquivo .env
    def ensure_env_key(self, key, default_value=''):
        if key not in dotenv_values(self.env_file):
            set_key(self.env_file, key, default_value)

    # Função para criar os widgets
    def create_widgets(self):
        # Tokens do GitHub
        self.github_token_label = ctk.CTkLabel(self, text="GitHub Tokens:")
        self.github_token_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.github_token_entry = ctk.CTkEntry(self, width=200)
        self.github_token_entry.grid(row=0, column=1, padx=10, pady=10)

        self.github_token_user_add_button = ctk.CTkButton(self, text="Add Token and User", command=self.add_github_token_and_user, fg_color=self.button_color)
        self.github_token_user_add_button.grid(row=0, column=2, padx=10, pady=10)

        self.github_token_edit_button = ctk.CTkButton(self, text="Edit", command=lambda: self.open_edit_menu('GitHub Token and User', self.github_token_edit_button), fg_color=self.button_color)
        self.github_token_edit_button.grid(row=0, column=3, padx=10, pady=10)

        # Usuários do GitHub
        self.github_user_label = ctk.CTkLabel(self, text="GitHub Users:")
        self.github_user_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.github_user_entry = ctk.CTkEntry(self, width=200)
        self.github_user_entry.grid(row=1, column=1, padx=10, pady=10)

        # Email da API
        self.api_email_label = ctk.CTkLabel(self, text="API Email:")
        self.api_email_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.api_email_entry = ctk.CTkEntry(self, width=200)
        self.api_email_entry.grid(row=2, column=1, padx=10, pady=10)

        self.api_email_token_add_button = ctk.CTkButton(self, text="Add Email and Token", command=self.add_api_email_and_token, fg_color=self.button_color)
        self.api_email_token_add_button.grid(row=2, column=2, padx=10, pady=10)

        self.api_email_edit_button = ctk.CTkButton(self, text="Edit", command=lambda: self.open_edit_menu('API Email and Token', self.api_email_edit_button), fg_color=self.button_color)
        self.api_email_edit_button.grid(row=2, column=3, padx=10, pady=10)

        # Token da API
        self.api_token_label = ctk.CTkLabel(self, text="API Token:")
        self.api_token_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.api_token_entry = ctk.CTkEntry(self, width=200)
        self.api_token_entry.grid(row=3, column=1, padx=10, pady=10)

        # Caminho de salvamento
        self.save_path_label = ctk.CTkLabel(self, text="Save Path:")
        self.save_path_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.save_path_entry = ctk.CTkEntry(self, width=200)
        self.save_path_entry.insert(0, self.save_path)
        self.save_path_entry.grid(row=4, column=1, padx=10, pady=10)

        self.save_path_button = ctk.CTkButton(self, text="Browse", command=self.browse_save_path, fg_color=self.button_color)
        self.save_path_button.grid(row=4, column=2, padx=10, pady=10)

        self.save_path_edit_button = ctk.CTkButton(self, text="Edit", command=lambda: self.open_edit_menu('Save Path', self.save_path_edit_button), fg_color=self.button_color)
        self.save_path_edit_button.grid(row=4, column=3, padx=10, pady=10)

        # Número máximo de trabalhadores
        self.max_workers_label = ctk.CTkLabel(self, text="Number of Max Workers:")
        self.max_workers_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.max_workers_entry = ctk.CTkEntry(self, width=200)
        self.max_workers_entry.insert(0, str(self.max_workers))
        self.max_workers_entry.grid(row=5, column=1, padx=10, pady=10)

        self.max_workers_add_button = ctk.CTkButton(self, text="Add", command=self.add_max_workers, fg_color=self.button_color)
        self.max_workers_add_button.grid(row=5, column=2, padx=10, pady=10)

        self.max_workers_edit_button = ctk.CTkButton(self, text="Edit", command=lambda: self.open_edit_menu('Max Workers', self.max_workers_edit_button), fg_color=self.button_color)
        self.max_workers_edit_button.grid(row=5, column=3, padx=10, pady=10)

    def open_edit_menu(self, item_type, button):
        if self.menu_window and self.menu_window.winfo_exists():
            self.menu_window.destroy()
            self.menu_window = None
            return

        self.menu_window = ctk.CTkToplevel(self)
        self.menu_window.overrideredirect(True)
        self.menu_window.associated_button = button
        self.update_menu_position()
        self.menu_window.configure(bg='#2e2e2e')

        self.menu_window.bind("<Destroy>", lambda e: setattr(self, 'menu_window', None))

        def close_menu(event):
            if self.menu_window and self.menu_window.winfo_exists():
                if not (self.menu_window.winfo_containing(event.x_root, event.y_root) or button.winfo_containing(event.x_root, event.y_root)):
                    self.menu_window.destroy()

        self.bind_all("<Button-1>", close_menu)

        if item_type == 'GitHub Token and User':
            ctk.CTkButton(self.menu_window, text="Edit GitHub Tokens", command=self.edit_github_token_window, fg_color=self.button_color).pack(fill='x')
            ctk.CTkButton(self.menu_window, text="Edit GitHub Users", command=self.edit_github_user_window, fg_color=self.button_color).pack(fill='x')
        elif item_type == 'API Email and Token':
            ctk.CTkButton(self.menu_window, text="Edit API Emails", command=self.edit_api_email_window, fg_color=self.button_color).pack(fill='x')
            ctk.CTkButton(self.menu_window, text="Edit API Tokens", command=self.edit_api_token_window, fg_color=self.button_color).pack(fill='x')
        elif item_type == 'Save Path':
            ctk.CTkButton(self.menu_window, text="Edit Save Path", command=self.browse_save_path, fg_color=self.button_color).pack(fill='x')
        elif item_type == 'Max Workers':
            ctk.CTkButton(self.menu_window, text="Edit Max Workers", command=self.add_max_workers, fg_color=self.button_color).pack(fill='x')

        self.menu_window.bind("<Destroy>", lambda e: self.unbind_all("<Button-1>"))

    # Function to update menu position
    def update_menu_position(self):
        if self.menu_window and self.menu_window.winfo_exists():
            button = self.menu_window.associated_button
            x = button.winfo_rootx()
            y = button.winfo_rooty() + button.winfo_height()
            self.menu_window.geometry(f"+{x}+{y}")

    # Function to close the menu when clicking outside
    def close_menu(self, event):
        if self.menu_window and self.menu_window.winfo_exists():
            if not (self.menu_window.winfo_containing(event.x_root, event.y_root) or self.winfo_containing(event.x_root, event.y_root)):
                self.menu_window.destroy()

    def check_window_state(self, event):
        if self.state() == 'withdrawn' or self.state() == 'iconic':
            if self.menu_window and self.menu_window.winfo_exists():
                self.menu_window.withdraw()
        elif self.state() == 'normal':
            if self.menu_window and self.menu_window.winfo_exists():
                self.menu_window.deiconify()
                
    # Método para rastrear a posição do menu suspenso
    def on_window_move(self, event):
        self.update_menu_position()

    # Função para atualizar o arquivo .env
    def update_env_file(self, key, value):
        value = value.strip().strip(',')
        set_key(self.env_file, key, value)
        if key == 'TOKENS':
            self.tokens = [t.strip() for t in value.split(',')] if value else []
        elif key == 'USERNAMES':
            self.usernames = [u.strip() for u in value.split(',')] if value else []
        elif key == 'EMAIL':
            self.emails = [e.strip() for e in value.split(',')] if value else []
        elif key == 'API_TOKEN':
            self.api_tokens = [a.strip() for a in value.split(',')] if value else []
        elif key == 'SAVE_PATH':
            self.save_path = value

    # Nova função para adicionar token e usuário do GitHub ao mesmo tempo
    def add_github_token_and_user(self):
        token = self.github_token_entry.get().strip()
        user = self.github_user_entry.get().strip()
        if token and user:
            if not self.tokens or (len(self.tokens) == 1 and self.tokens[0] == ''):
                self.tokens = [token]
                self.usernames = [user]
            else:
                self.tokens.append(token)
                self.usernames.append(user)
            self.update_env_file('TOKENS', ','.join(self.tokens))
            self.update_env_file('USERNAMES', ','.join(self.usernames))
            self.github_token_entry.delete(0, "end")
            self.github_user_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter both a GitHub token and user.")

    # Nova função para adicionar email e token da API ao mesmo tempo
    def add_api_email_and_token(self):
        email = self.api_email_entry.get().strip()
        token = self.api_token_entry.get().strip()
        if email and token:
            if not self.emails or (len(self.emails) == 1 and self.emails[0] == ''):
                self.emails = [email]
                self.api_tokens = [token]
            else:
                self.emails.append(email)
                self.api_tokens.append(token)
            self.update_env_file('EMAIL', ','.join(self.emails))
            self.update_env_file('API_TOKEN', ','.join(self.api_tokens))
            self.api_email_entry.delete(0, "end")
            self.api_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter both an API email and token.")

    # Função para navegar pelo caminho de salvamento
    def browse_save_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_entry.delete(0, "end")
            self.save_path_entry.insert(0, path)
            self.update_env_file('SAVE_PATH', path)

    # Função para adicionar o número máximo de trabalhadores
    def add_max_workers(self):
        max_workers_str = self.max_workers_entry.get()
        try:
            max_workers = int(max_workers_str)
            self.update_env_file('MAX_WORKERS', str(max_workers))
            self.max_workers_entry.delete(0, "end")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid integer for Max Workers.")

    # Função para abrir a janela de listbox
    def open_listbox_window(self, title, items, add_command):
        window = Toplevel(self)
        window.title(title)
        window.geometry("400x300")
        window.configure(bg='#2e2e2e')

        listbox_frame = CTkListbox(window)
        listbox_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.populate_listbox(listbox_frame.listbox, items)

        edit_button = ctk.CTkButton(window, text="Edit", command=lambda: self.edit_item(listbox_frame.listbox), fg_color=self.button_color)
        edit_button.pack(side="left", padx=10, pady=10)

        remove_button = ctk.CTkButton(window, text="Remove", command=lambda: self.remove_item(listbox_frame.listbox), fg_color=self.button_color)
        remove_button.pack(side="right", padx=10, pady=10)

    # Função para preencher a listbox
    def populate_listbox(self, listbox, items):
        for item in items:
            if item:
                listbox.insert('end', item)

    # Função para editar um item na listbox
    def edit_item(self, listbox):
        selected = listbox.curselection()
        if selected:
            item = listbox.get(selected)
            listbox.delete(selected)
            listbox.insert(selected, item)
        else:
            messagebox.showwarning("Warning", "Please select an item to edit.")

    # Função para remover um item da listbox
    def remove_item(self, listbox):
        selected = listbox.curselection()
        if selected:
            item = listbox.get(selected)
            listbox.delete(selected)
            self.remove_from_env(item)
        else:
            messagebox.showwarning("Warning", "Please select an item to remove.")

    # Função para remover um item do arquivo .env
    def remove_from_env(self, item):
        if item in self.tokens:
            self.tokens.remove(item)
            self.update_env_file('TOKENS', ','.join(self.tokens))
        elif item in self.usernames:
            self.usernames.remove(item)
            self.update_env_file('USERNAMES', ','.join(self.usernames))
        elif item in self.emails:
            self.emails.remove(item)
            self.update_env_file('EMAIL', ','.join(self.emails))
        elif item in self.api_tokens:
            self.api_tokens.remove(item)
            self.update_env_file('API_TOKEN', ','.join(self.api_tokens))

    # Função para adicionar um email da API à listbox
    def add_api_email_to_listbox(self, listbox):
        email = self.api_email_entry.get()
        if email:
            listbox.insert('end', email)
            self.api_email_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API email.")

    # Função para adicionar um token da API à listbox
    def add_api_token_to_listbox(self, listbox):
        token = self.api_token_entry.get()
        if token:
            listbox.insert('end', token)
            self.api_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API token.")

    # Função para abrir a janela de edição de tokens do GitHub
    def edit_github_token_window(self):
        self.open_listbox_window("Edit GitHub Tokens", self.tokens, self.add_github_token_to_listbox)

    # Função para abrir a janela de edição de usuários do GitHub
    def edit_github_user_window(self):
        self.open_listbox_window("Edit GitHub Users", self.usernames, self.add_github_user_to_listbox)

    # Função para abrir a janela de edição de emails da API
    def edit_api_email_window(self):
        self.open_listbox_window("Edit API Emails", self.emails, self.add_api_email_to_listbox)

    # Função para abrir a janela de edição de tokens da API
    def edit_api_token_window(self):
        self.open_listbox_window("Edit API Tokens", self.api_tokens, self.add_api_token_to_listbox)

    # Função para adicionar um token do GitHub à listbox
    def add_github_token_to_listbox(self, listbox):
        token = self.github_token_entry.get()
        if token:
            listbox.insert('end', token)
            self.github_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub token.")

    # Função para adicionar um usuário do GitHub à listbox
    def add_github_user_to_listbox(self, listbox):
        user = self.github_user_entry.get()
        if user:
            listbox.insert('end', user)
            self.github_user_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub user.")

# Classe principal da aplicação de mineração de dados
class DataMinerApp():
    def __init__(self, root):
        self.root = root
        self.root.title("Data Miner")
        self.root.configure(bg='#1e1e1e')

        if platform.system() == "Linux":
            self.root.iconphoto(True, PhotoImage(file='view/icons/datamining.png'))
        else:
            self.root.iconbitmap('view/icons/datamining.ico')

        self.window_width = 800
        self.window_height = 450
        self.center_window()

        self.bree_serif = tkfont.Font(family="Bree Serif", size=30, weight="bold")
        self.bree_serif_small = tkfont.Font(family="Bree Serif", size=15, weight="bold")

        self.image_refs = {}

        self.create_widgets()

    # Função para centralizar a janela na tela
    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')

    # Função para criar os widgets
    def create_widgets(self):
        title_label = tk.Label(self.root, text="Select a Platform", font=self.bree_serif, fg="#606060", bg='#1e1e1e')
        title_label.pack(pady=30)

        frame = tk.Frame(self.root, bg='#1e1e1e')
        frame.pack(pady=20)

        self.create_platform_button(frame, "view/icons/jira_icon_black.png", "JIRA", 0, 0, self.on_jira_click)
        self.create_platform_button(frame, "view/icons/gh_icon_black.png", "GitHub", 0, 1, self.on_github_click)

        self.create_settings_button()
        self.create_close_button()

    # Função para criar um botão de plataforma
    def create_platform_button(self, frame, image_path, label_text, row, column, click_command):
        try:
            image = Image.open(image_path)
            image = image.resize((180, 180), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading {label_text} image: {e}")
            photo = None

        circle_image = self.create_circle_image(200, (60, 60, 60), (0, 0, 0, 0))
        circle_photo = ImageTk.PhotoImage(circle_image)

        canvas = tk.Canvas(frame, width=250, height=250, bg='#1e1e1e', highlightthickness=0)
        canvas.grid(row=row, column=column, padx=60)
        canvas.create_image(125, 125, image=circle_photo)
        if photo:
            canvas.create_image(125, 125, image=photo)
        canvas.bind("<Button-1>", lambda e: click_command())
        canvas.bind("<Enter>", lambda e: self.zoom_in(e, canvas, image, label_text))
        canvas.bind("<Leave>", lambda e: self.zoom_out(e, canvas, photo))

        self.image_refs[f"{label_text}_circle"] = circle_photo
        self.image_refs[label_text] = photo

        canvas.circle_photo = circle_photo

    # Função para criar uma imagem circular
    def create_circle_image(self, diameter, color, bg_color):
        image = Image.new('RGBA', (diameter, diameter), bg_color)
        draw = ImageDraw.Draw(image)
        for i in range(diameter):
            for j in range(diameter):
                distance_to_center = ((i - diameter/2)**2 + (j - diameter/2)**2)**0.5
                if distance_to_center < diameter/2:
                    alpha = 255
                    if distance_to_center > diameter/2 - 1:
                        alpha = int(255 * (1 - (distance_to_center - (diameter/2 - 1))))
                    image.putpixel((i, j), color + (alpha,))
        return image

    # Função para criar um botão de configurações
    def create_settings_button(self):
        try:
            settings_image = Image.open("view/icons/settings_icon.png")
            settings_image = settings_image.resize((30, 30), Image.LANCZOS)
            settings_photo = ImageTk.PhotoImage(settings_image)
            settings_image_zoomed = settings_image.resize((36, 36), Image.LANCZOS)
            settings_photo_zoomed = ImageTk.PhotoImage(settings_image_zoomed)
        except Exception as e:
            print(f"Error loading settings image: {e}")
            settings_photo = None

        if settings_photo:
            settings_button = tk.Button(self.root, image=settings_photo, command=self.on_settings_click, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            settings_button.place(relx=0.97, rely=0.95, anchor='center')
            settings_button.bind("<Enter>", lambda e: settings_button.config(image=settings_photo_zoomed))
            settings_button.bind("<Leave>", lambda e: settings_button.config(image=settings_photo))

            self.image_refs['settings'] = settings_photo
            self.image_refs['settings_zoomed'] = settings_photo_zoomed

    # Função para sair da aplicação
    def exit(self):
        exit(1)

    # Função para criar um botão de fechar
    def create_close_button(self):
        try:
            close_image = Image.open("view/icons/close.png")
            close_image = close_image.resize((20, 20), Image.LANCZOS)
            close_photo = ImageTk.PhotoImage(close_image)
            close_image_zoomed = close_image.resize((24, 24), Image.LANCZOS)
            close_photo_zoomed = ImageTk.PhotoImage(close_image_zoomed)
        except Exception as e:
            print(f"Error loading close image: {e}")
            close_photo = None

        if close_photo:
            close_button = tk.Button(self.root, image=close_photo, command=self.exit, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            close_button.place(relx=0.98, rely=0.02, anchor='ne')
            close_button.bind("<Enter>", lambda e: close_button.config(image=close_photo_zoomed))
            close_button.bind("<Leave>", lambda e: close_button.config(image=close_photo))
            self.image_refs['close'] = close_photo
            self.image_refs['close_zoomed'] = close_photo_zoomed

    # Função para lidar com o clique no botão do Jira
    def on_jira_click(self): 
        self.root.withdraw()  
        jira_app = JiraDataMinerApp(self.root)
        jira_app.run()

    # Função para lidar com o clique no botão do GitHub
    def on_github_click(self): 
        self.root.withdraw()  
        gh_app = GitHubRepoInfoApp(self.root)
        gh_app.run()  

    # Função para lidar com o clique no botão de configurações
    def on_settings_click(self):
        settings_app = SettingsApp()
        settings_app.mainloop()

    # Função para aumentar o zoom de uma imagem ao passar o mouse
    def zoom_in(self, event, widget, image, label_text=None):
        if isinstance(widget, tk.Canvas):
            zoomed_image = image.resize((int(image.width * 1.1), int(image.height * 1.1)), Image.LANCZOS)
            zoomed_photo = ImageTk.PhotoImage(zoomed_image)
            widget.delete("all")
            widget.create_image(125, 125, image=widget.circle_photo)
            widget.create_image(125, 125, image=zoomed_photo)
            widget.image = zoomed_photo

            if label_text:
                label = tk.Label(self.root, text=label_text, font=self.bree_serif_small, fg="#606060", bg='#1e1e1e')
                widget_x = widget.winfo_rootx() - self.root.winfo_rootx()
                widget_y = widget.winfo_rooty() - self.root.winfo_rooty()
                label_width = label.winfo_reqwidth()
                label.place(x=widget_x + (widget.winfo_width() - label_width) // 2, y=widget_y + 250)
                widget.label = label
        elif isinstance(widget, tk.Button):
            zoomed_image = image.resize((int(image.width * 1.2), int(image.height * 1.2)), Image.LANCZOS)
            zoomed_photo = ImageTk.PhotoImage(zoomed_image)
            widget.config(image=zoomed_photo)
            widget.image = zoomed_photo

    # Função para diminuir o zoom de uma imagem ao retirar o mouse
    def zoom_out(self, event, widget, image):
        if isinstance(widget, tk.Canvas):
            widget.delete("all")
            widget.create_image(125, 125, image=widget.circle_photo)
            widget.create_image(125, 125, image=image)
            if hasattr(widget, 'label'):
                widget.label.destroy()
            widget.image = image
        elif isinstance(widget, tk.Button):
            widget.config(image=image)
            widget.image = image
