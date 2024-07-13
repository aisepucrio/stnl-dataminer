import customtkinter as ctk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from controller.controller_jira import JiraController

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



