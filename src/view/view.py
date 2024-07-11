from PIL import Image
import customtkinter as ctk

class DataMinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Data Miner")
        self.geometry("450x600")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="Choose Platform", font=("Segoe UI", 20))
        self.label.pack(pady=20)

        # Carregando as imagens dos ícones
        jira_icon = ctk.CTkImage(light_image=Image.open("view/icons/jira_icon.png"), size=(20, 20))
        github_icon = ctk.CTkImage(light_image=Image.open("view/icons/gh_icon.png"), size=(20, 20))

        self.jira_button = ctk.CTkButton(self.frame, text="Jira", image=jira_icon, compound="left", command=self.open_jira)
        self.jira_button.pack(pady=10)

        self.github_button = ctk.CTkButton(self.frame, text="GitHub", image=github_icon, compound="left", command=self.open_github)
        self.github_button.pack(pady=10)

        self.mining_frame = None
        self.controller = None

    def open_jira(self):
        # Implementar a lógica para abrir as opções do Jira
        print("Jira selected")

    def open_github(self):
        # Implementar a lógica para abrir as opções do GitHub
        print("GitHub selected")

if __name__ == "__main__":
    app = DataMinerApp()
    app.mainloop()
