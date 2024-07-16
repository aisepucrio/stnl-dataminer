import customtkinter
import threading
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from controller.controller import GitHubController  
from dotenv import load_dotenv

load_dotenv()

class GitHubRepoInfoApp(customtkinter.CTk):
    def __init__(self, menu_app):
        super().__init__()

        self.menu_app = menu_app
        self.controller = GitHubController()

        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme("dark-blue")

        self.root = customtkinter.CTk()
        self.root.geometry("450x750")
        self.root.title("GitHub Repo Info")

        # Adicionar botão de voltar
        self.back_button = customtkinter.CTkButton(
            self.root, text="← Back", command=self.back_to_menu, 
            corner_radius=8, fg_color="#2e2e2e", hover_color="#4a4a4a",
            text_color="#ffffff", width=80, height=32, font=("Segoe UI", 12, "bold")
        )
        self.back_button.pack(pady=12, padx=10, anchor='nw', side='top')

        default_font = customtkinter.CTkFont(family="Segoe UI", size=12)

        self.frame = customtkinter.CTkFrame(master=self.root)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.label_url = customtkinter.CTkLabel(master=self.frame, text="Repository URL", font=default_font)
        self.label_url.pack(pady=12, padx=10)

        self.entry_url = customtkinter.CTkEntry(master=self.frame, placeholder_text='Enter GitHub repo URL', width=400, font=default_font)
        self.entry_url.pack(pady=12, padx=10)

        self.label_start_date = customtkinter.CTkLabel(master=self.frame, text="Start Date (DD/MM/YYYY)", font=default_font)
        self.label_start_date.pack(pady=12, padx=10)

        self.entry_start_date = DateEntry(master=self.frame, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_start_date.pack(pady=12, padx=10)

        self.label_end_date = customtkinter.CTkLabel(master=self.frame, text="End Date (DD/MM/YYYY)", font=default_font)
        self.label_end_date.pack(pady=12, padx=10)

        self.entry_end_date = DateEntry(master=self.frame, date_pattern='dd/MM/yyyy', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_end_date.pack(pady=12, padx=10)

        self.switch_frame = customtkinter.CTkFrame(master=self.frame)
        self.switch_frame.pack(pady=12, padx=10, anchor='center', expand=True)

        self.switch_commits = customtkinter.CTkSwitch(master=self.switch_frame, text="Commits", font=default_font)
        self.switch_commits.pack(pady=5, padx=20, anchor='w')
        self.switch_issues = customtkinter.CTkSwitch(master=self.switch_frame, text="Issues", font=default_font)
        self.switch_issues.pack(pady=5, padx=20, anchor='w')
        self.switch_pull_requests = customtkinter.CTkSwitch(master=self.switch_frame, text="Pull Requests", font=default_font)
        self.switch_pull_requests.pack(pady=5, padx=20, anchor='w')
        self.switch_branches = customtkinter.CTkSwitch(master=self.switch_frame, text="Branches", font=default_font)
        self.switch_branches.pack(pady=5, padx=20, anchor='w')

        self.button = customtkinter.CTkButton(master=self.frame, text="Get Information", command=self.get_information, font=default_font, corner_radius=8)
        self.button.pack(pady=12, padx=10)

        self.stop_button = customtkinter.CTkButton(master=self.frame, text="Stop", command=self.stop_process, font=default_font, corner_radius=8, fg_color="red")
        self.stop_button.pack(pady=12, padx=10)

        self.progress_bar = customtkinter.CTkProgressBar(master=self.frame)
        self.progress_bar.pack(pady=12, padx=10)
        self.progress_bar.set(0)

        self.result_label = customtkinter.CTkLabel(master=self.frame, text="", font=default_font)
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
        max_workers = self.controller.max_workers_default  # Always use the default from .env

        print(f"Number of workers being used: {max_workers}")

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
