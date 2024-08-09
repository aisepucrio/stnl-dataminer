import customtkinter as ctk
from tkcalendar import DateEntry

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

        # Frame para os tipos de issue adicionais
        self.additional_issues_frame = ctk.CTkFrame(self)
        self.additional_issues_frame.pack(pady=7, padx=10, anchor='center')

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

    # Função para executar a aplicação
    def run(self):
        self.mainloop()