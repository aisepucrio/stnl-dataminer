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

class JiraDataMinerApp(ctk.CTk):
    def __init__(self, menu_app):
        super().__init__()

        self.menu_app = menu_app
        self.controller = JiraController(self)

        self.title("Jira Data Miner")
        self.geometry("550x700")
        self.configure(bg="black")

        # Adicionar botão de voltar
        self.back_button = ctk.CTkButton(
            self, text="← Back", command=self.back_to_menu,
            corner_radius=8, fg_color="#2e2e2e", hover_color="#4a4a4a",
            text_color="#ffffff", width=80, height=32, font=("Segoe UI", 12, "bold")
        )
        self.back_button.pack(pady=12, padx=10, anchor='nw')

        self.url_label = ctk.CTkLabel(self, text="Project or Repository URL:")
        self.url_label.pack(pady=10)
        self.url_entry = ctk.CTkEntry(self, width=300)
        self.url_entry.pack(pady=10)

        self.start_date_label = ctk.CTkLabel(self, text="Start Date:")
        self.start_date_label.pack(pady=10)
        self.start_date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date_entry.pack(pady=10)

        self.end_date_label = ctk.CTkLabel(self, text="End Date:")
        self.end_date_label.pack(pady=10)
        self.end_date_entry = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date_entry.pack(pady=10)

        self.load_fields_button = ctk.CTkButton(self, text="Confirm", command=self.controller.confirm_selection)
        self.load_fields_button.pack(pady=20)

        self.mining_options_frame = None

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

    def back_to_menu(self):
        self.menu_app.deiconify()
        self.destroy()

    def show_jira_options(self, jira_domain, project_key):
        if self.mining_options_frame:
            self.mining_options_frame.destroy()

        self.mining_options_frame = ctk.CTkFrame(self)
        self.mining_options_frame.pack(pady=20)

        self.epics_switch = ctk.CTkSwitch(self.mining_options_frame, text="Epics")
        self.epics_switch.pack(pady=5)
        self.user_stories_switch = ctk.CTkSwitch(self.mining_options_frame, text="User Stories")
        self.user_stories_switch.pack(pady=5)
        self.tasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Tasks")
        self.tasks_switch.pack(pady=5)
        self.subtasks_switch = ctk.CTkSwitch(self.mining_options_frame, text="Sub-tasks")
        self.subtasks_switch.pack(pady=5)
        self.bugs_switch = ctk.CTkSwitch(self.mining_options_frame, text="Bugs")
        self.bugs_switch.pack(pady=5)
        self.enablers_switch = ctk.CTkSwitch(self.mining_options_frame, text="Enablers")
        self.enablers_switch.pack(pady=5)

        self.mine_button = ctk.CTkButton(self.mining_options_frame, text="Mine Data", command=lambda: self.controller.mine_data_jira(jira_domain, project_key))
        self.mine_button.pack(pady=20)

        self.stop_button = ctk.CTkButton(self.mining_options_frame, text="Stop", fg_color="red", command=self.controller.stop_mining)
        self.stop_button.pack(pady=10)

    def show_github_options(self, repo_url):
        if self.mining_options_frame:
            self.mining_options_frame.destroy()

        self.mining_options_frame = ctk.CTkFrame(self)
        self.mining_options_frame.pack(pady=20)

        self.commits_switch = ctk.CTkSwitch(self.mining_options_frame, text="Commits")
        self.commits_switch.pack(pady=5)
        self.issues_switch = ctk.CTkSwitch(self.mining_options_frame, text="Issues")
        self.issues_switch.pack(pady=5)
        self.pull_requests_switch = ctk.CTkSwitch(self.mining_options_frame, text="Pull Requests")
        self.pull_requests_switch.pack(pady=5)
        self.branches_switch = ctk.CTkSwitch(self.mining_options_frame, text="Branches")
        self.branches_switch.pack(pady=5)

        self.mine_button = ctk.CTkButton(self.mining_options_frame, text="Mine Data", command=lambda: self.controller.mine_data_github(repo_url))
        self.mine_button.pack(pady=20)

        self.stop_button = ctk.CTkButton(self.mining_options_frame, text="Stop", fg_color="red", command=self.controller.stop_mining)
        self.stop_button.pack(pady=10)
    
    def run(self):
        self.mainloop()

class GitHubRepoInfoApp(ctk.CTk):
    def __init__(self, menu_app):
        super().__init__()

        self.menu_app = menu_app
        self.controller = GitHubController()

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.geometry("450x800")
        self.root.title("GitHub Repo Info")

        self.back_button = ctk.CTkButton(
            self.root, text="← Back", command=self.back_to_menu, 
            corner_radius=8, fg_color="#2e2e2e", hover_color="#4a4a4a",
            text_color="#ffffff", width=80, height=32, font=("Segoe UI", 12, "bold")
        )
        self.back_button.pack(pady=12, padx=10, anchor='nw', side='top')

        default_font = ctk.CTkFont(family="Segoe UI", size=12)

        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.label_url = ctk.CTkLabel(master=self.frame, text="Repository URL", font=default_font)
        self.label_url.pack(pady=12, padx=10)

        self.entry_url = ctk.CTkEntry(master=self.frame, placeholder_text='Enter GitHub repo URL', width=400, font=default_font)
        self.entry_url.pack(pady=12, padx=10)

        self.label_start_date = ctk.CTkLabel(master=self.frame, text="Start Date (DD/MM/YYYY)", font=default_font)
        self.label_start_date.pack(pady=12, padx=10)

        self.entry_start_date = DateEntry(master=self.frame, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_start_date.pack(pady=12, padx=10)

        self.label_end_date = ctk.CTkLabel(master=self.frame, text="End Date (DD/MM/YYYY)", font=default_font)
        self.label_end_date.pack(pady=12, padx=10)

        self.entry_end_date = DateEntry(master=self.frame, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_end_date.pack(pady=12, padx=10)

        self.switch_frame = ctk.CTkFrame(master=self.frame)
        self.switch_frame.pack(pady=12, padx=10, anchor='center', expand=True)

        self.switch_commits = ctk.CTkSwitch(master=self.switch_frame, text="Commits", font=default_font)
        self.switch_commits.pack(pady=5, padx=20, anchor='w')
        self.switch_issues = ctk.CTkSwitch(master=self.switch_frame, text="Issues", font=default_font)
        self.switch_issues.pack(pady=5, padx=20, anchor='w')
        self.switch_pull_requests = ctk.CTkSwitch(master=self.switch_frame, text="Pull Requests", font=default_font)
        self.switch_pull_requests.pack(pady=5, padx=20, anchor='w')
        self.switch_branches = ctk.CTkSwitch(master=self.switch_frame, text="Branches", font=default_font)
        self.switch_branches.pack(pady=5, padx=20, anchor='w')

        self.button = ctk.CTkButton(master=self.frame, text="Get Information", command=self.get_information, font=default_font, corner_radius=8)
        self.button.pack(pady=12, padx=10)

        self.stop_button = ctk.CTkButton(master=self.frame, text="Stop", command=self.stop_process, font=default_font, corner_radius=8, fg_color="red")
        self.stop_button.pack(pady=12, padx=10)

        self.progress_bar = ctk.CTkProgressBar(master=self.frame)
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0)

        self.result_label = ctk.CTkLabel(master=self.frame, text="", font=default_font)
        self.result_label.pack(pady=12, padx=10)

    def back_to_menu(self):
        self.menu_app.deiconify()
        self.root.destroy()  # Ensure the current window is destroyed

    def run(self):
        self.root.mainloop()

    def get_information(self):
        repo_url = self.entry_url.get()
        start_date = self.entry_start_date.get_date()
        end_date = self.entry_end_date.get_date()
        max_workers = self.controller.max_workers_default 

        options = {
            'commits': self.switch_commits.get() == 1,
            'issues': self.switch_issues.get() == 1,
            'pull_requests': self.switch_pull_requests.get() == 1,
            'branches': self.switch_branches.get() == 1
        }

        def collect_data():
            try:
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

    def update_progress(self, step):
        current_value = self.progress_bar.get()
        self.progress_bar.set(current_value + step)

    def stop_process(self):
        self.controller.stop_process()
        self.result_label.configure(text="Process stopped by the user.")

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

class SettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Settings")
        self.geometry("705x295")  # Aumenta a altura para o novo campo
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.button_color = "#1e1e1e"

        # Load environment variables
        self.env_file = '.env'
        self.load_env()

        self.create_widgets()

    def load_env(self):
        if not os.path.exists(self.env_file):
            with open(self.env_file, 'w') as f:
                f.write('TOKENS=\nUSERNAMES=\nEMAIL=\nAPI_TOKEN=\nSAVE_PATH=\nMAX_WORKERS=1\n')
        
        load_dotenv(self.env_file)
        
        env_values = dotenv_values(self.env_file)
        self.tokens = env_values.get('TOKENS', '').split(',')
        self.usernames = env_values.get('USERNAMES', '').split(',')
        self.emails = env_values.get('EMAIL', '').split(',')
        self.api_tokens = env_values.get('API_TOKEN', '').split(',')
        self.save_path = env_values.get('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Desktop"))
        max_workers_str = env_values.get('MAX_WORKERS', '1')
        self.max_workers = int(max_workers_str) if max_workers_str else 1

        # Ensure all required keys are present in the .env file
        self.ensure_env_key('TOKENS')
        self.ensure_env_key('USERNAMES')
        self.ensure_env_key('EMAIL')
        self.ensure_env_key('API_TOKEN')
        self.ensure_env_key('SAVE_PATH')
        self.ensure_env_key('MAX_WORKERS')

    def ensure_env_key(self, key):
        if key not in dotenv_values(self.env_file):
            set_key(self.env_file, key, '')

    def create_widgets(self):
        # GitHub Tokens
        self.github_token_label = ctk.CTkLabel(self, text="GitHub Tokens:")
        self.github_token_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.github_token_entry = ctk.CTkEntry(self, width=200)
        self.github_token_entry.grid(row=0, column=1, padx=10, pady=10)

        self.github_token_add_button = ctk.CTkButton(self, text="Add", command=self.add_github_token, fg_color=self.button_color)
        self.github_token_add_button.grid(row=0, column=2, padx=10, pady=10)

        self.github_token_edit_button = ctk.CTkButton(self, text="Edit", command=self.edit_github_token_window, fg_color=self.button_color)
        self.github_token_edit_button.grid(row=0, column=3, padx=10, pady=10)

        # GitHub Users
        self.github_user_label = ctk.CTkLabel(self, text="GitHub Users:")
        self.github_user_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.github_user_entry = ctk.CTkEntry(self, width=200)
        self.github_user_entry.grid(row=1, column=1, padx=10, pady=10)

        self.github_user_add_button = ctk.CTkButton(self, text="Add", command=self.add_github_user, fg_color=self.button_color)
        self.github_user_add_button.grid(row=1, column=2, padx=10, pady=10)

        self.github_user_edit_button = ctk.CTkButton(self, text="Edit", command=self.edit_github_user_window, fg_color=self.button_color)
        self.github_user_edit_button.grid(row=1, column=3, padx=10, pady=10)

        # API Email
        self.api_email_label = ctk.CTkLabel(self, text="API Email:")
        self.api_email_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.api_email_entry = ctk.CTkEntry(self, width=200)
        self.api_email_entry.grid(row=2, column=1, padx=10, pady=10)

        self.api_email_add_button = ctk.CTkButton(self, text="Add", command=self.add_api_email, fg_color=self.button_color)
        self.api_email_add_button.grid(row=2, column=2, padx=10, pady=10)

        self.api_email_edit_button = ctk.CTkButton(self, text="Edit", command=self.edit_api_email_window, fg_color=self.button_color)
        self.api_email_edit_button.grid(row=2, column=3, padx=10, pady=10)

        # API Token
        self.api_token_label = ctk.CTkLabel(self, text="API Token:")
        self.api_token_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.api_token_entry = ctk.CTkEntry(self, width=200)
        self.api_token_entry.grid(row=3, column=1, padx=10, pady=10)

        self.api_token_add_button = ctk.CTkButton(self, text="Add", command=self.add_api_token, fg_color=self.button_color)
        self.api_token_add_button.grid(row=3, column=2, padx=10, pady=10)

        self.api_token_edit_button = ctk.CTkButton(self, text="Edit", command=self.edit_api_token_window, fg_color=self.button_color)
        self.api_token_edit_button.grid(row=3, column=3, padx=10, pady=10)

        # Save Path
        self.save_path_label = ctk.CTkLabel(self, text="Save Path:")
        self.save_path_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.save_path_entry = ctk.CTkEntry(self, width=200)
        self.save_path_entry.insert(0, self.save_path)
        self.save_path_entry.grid(row=4, column=1, padx=10, pady=10)

        self.save_path_button = ctk.CTkButton(self, text="Browse", command=self.browse_save_path, fg_color=self.button_color)
        self.save_path_button.grid(row=4, column=2, padx=10, pady=10)

        # Max Workers
        self.max_workers_label = ctk.CTkLabel(self, text="Number of Max Workers:")
        self.max_workers_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.max_workers_entry = ctk.CTkEntry(self, width=200)
        self.max_workers_entry.insert(0, str(self.max_workers))
        self.max_workers_entry.grid(row=5, column=1, padx=10, pady=10)

        self.max_workers_add_button = ctk.CTkButton(self, text="Add", command=self.add_max_workers, fg_color=self.button_color)
        self.max_workers_add_button.grid(row=5, column=2, padx=10, pady=10)

    def update_env_file(self, key, value):
        set_key(self.env_file, key, value)
        if key == 'SAVE_PATH':
            self.save_path = value 

    def add_github_token(self):
        token = self.github_token_entry.get()
        if token:
            self.tokens.append(token)
            self.update_env_file('TOKENS', ','.join(self.tokens))
            self.github_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub token.")

    def edit_github_token_window(self):
        self.open_listbox_window("Edit GitHub Tokens", self.tokens, self.add_github_token_to_listbox)

    def add_github_user(self):
        user = self.github_user_entry.get()
        if user:
            self.usernames.append(user)
            self.update_env_file('USERNAMES', ','.join(self.usernames))
            self.github_user_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub user.")

    def edit_github_user_window(self):
        self.open_listbox_window("Edit GitHub Users", self.usernames, self.add_github_user_to_listbox)

    def add_api_email(self):
        email = self.api_email_entry.get()
        if email:
            self.emails.append(email)
            self.update_env_file('EMAIL', ','.join(self.emails))
            self.api_email_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API email.")

    def edit_api_email_window(self):
        self.open_listbox_window("Edit API Emails", self.emails, self.add_api_email_to_listbox)

    def add_api_token(self):
        token = self.api_token_entry.get()
        if token:
            self.api_tokens.append(token)
            self.update_env_file('API_TOKEN', ','.join(self.api_tokens))
            self.api_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API token.")

    def edit_api_token_window(self):
        self.open_listbox_window("Edit API Tokens", self.api_tokens, self.add_api_token_to_listbox)

    def browse_save_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_entry.delete(0, "end")
            self.save_path_entry.insert(0, path)
            self.update_env_file('SAVE_PATH', path)

    def add_max_workers(self):
        max_workers_str = self.max_workers_entry.get()
        try:
            max_workers = int(max_workers_str)  # Tenta converter a entrada para int
            self.update_env_file('MAX_WORKERS', str(max_workers))
            self.max_workers_entry.delete(0, "end")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid integer for Max Workers.")

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

    def populate_listbox(self, listbox, items):
        for item in items:
            if item:
                listbox.insert('end', item)

    def edit_item(self, listbox):
        selected = listbox.curselection()
        if selected:
            item = listbox.get(selected)
            listbox.delete(selected)
            listbox.insert(selected, item)
        else:
            messagebox.showwarning("Warning", "Please select an item to edit.")

    def remove_item(self, listbox):
        selected = listbox.curselection()
        if selected:
            item = listbox.get(selected)
            listbox.delete(selected)
            self.remove_from_env(item)
        else:
            messagebox.showwarning("Warning", "Please select an item to remove.")

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

    def add_github_token_to_listbox(self, listbox):
        token = self.github_token_entry.get()
        if token:
            listbox.insert('end', token)
            self.github_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub token.")

    def add_github_user_to_listbox(self, listbox):
        user = self.github_user_entry.get()
        if user:
            listbox.insert('end', user)
            self.github_user_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter a GitHub user.")

    def add_api_email_to_listbox(self, listbox):
        email = self.api_email_entry.get()
        if email:
            listbox.insert('end', email)
            self.api_email_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API email.")

    def add_api_token_to_listbox(self, listbox):
        token = self.api_token_entry.get()
        if token:
            listbox.insert('end', token)
            self.api_token_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Please enter an API token.")

class DataMinerApp:
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

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Selecione a Plataforma", font=self.bree_serif, fg="#606060", bg='#1e1e1e')
        title_label.pack(pady=30)

        frame = tk.Frame(self.root, bg='#1e1e1e')
        frame.pack(pady=20)

        self.create_platform_button(frame, "view/icons/jira_icon_black.png", "JIRA", 0, 0, self.on_jira_click)
        self.create_platform_button(frame, "view/icons/gh_icon_black.png", "GitHub", 0, 1, self.on_github_click)

        self.create_settings_button()
        self.create_close_button()

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
            close_button = tk.Button(self.root, image=close_photo, command=self.root.quit, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            close_button.place(relx=0.98, rely=0.02, anchor='ne')
            close_button.bind("<Enter>", lambda e: close_button.config(image=close_photo_zoomed))
            close_button.bind("<Leave>", lambda e: close_button.config(image=close_photo))
            self.image_refs['close'] = close_photo
            self.image_refs['close_zoomed'] = close_photo_zoomed

    def on_jira_click(self): 
        self.root.withdraw()  
        jira_app = JiraDataMinerApp(self.root)
        jira_app.run()

    def on_github_click(self): 
        self.root.withdraw()  
        gh_app = GitHubRepoInfoApp(self.root)
        gh_app.run()  

    def on_settings_click(self):
        settings_app = SettingsApp()
        settings_app.mainloop()

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
