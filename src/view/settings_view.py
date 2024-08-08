import customtkinter as ctk
import os
from dotenv import set_key, dotenv_values
from tkinter import font as tkfont, messagebox, Toplevel, Listbox, filedialog

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
    def __init__(self, menu_app, tokens, usernames, emails, api_tokens, save_path, max_workers, use_database):
        super().__init__()
        self.menu_app = menu_app
        self.tokens = tokens
        self.usernames = usernames
        self.emails = emails
        self.api_tokens = api_tokens
        self.save_path = save_path
        self.max_workers = max_workers
        self.use_database = use_database
        self.title("Settings")
        self.geometry("800x750")  # Definindo dimensões específicas da janela
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.button_color = "#1e1e1e"

        # Adicionar o atributo para rastrear o estado do menu
        self.menu_window = None  # Adicionado para rastrear o estado do menu

        # Carrega variáveis de ambiente
        self.env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')

        self.create_widgets()

        self.center_window()  # Centraliza a janela após criação dos widgets

        self.bind('<Unmap>', self.check_window_state)
        self.bind('<Map>', self.check_window_state)
        self.bind("<Configure>", self.on_window_move)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        print("Save changes before closing the window.")

    def center_window(self):
        self.update_idletasks()
        width = 700  # Largura desejada
        height = 400  # Altura desejada
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def database_checkbox_command(self):
        self.database_checkbox_value = self.database_checkbox.get()
        
        set_key(self.env_file, 'USE_DATABASE', '1' if self.database_checkbox_value else '0')

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

        self.database_checkbox = ctk.CTkCheckBox(self, text="Use Database", command=self.database_checkbox_command)
        self.database_checkbox.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Define o estado inicial da checkbox
        self.database_checkbox.select() if self.use_database else self.database_checkbox.deselect()

        # Botão "Save Changes"
        self.save_changes_button = ctk.CTkButton(self, text="Save Changes", command=self.save_changes_and_close, fg_color='#3e3e3e')
        self.save_changes_button.grid(row=7, column=0, columnspan=4, pady=20)

    # Função para salvar as alterações e fechar a janela
    def save_changes_and_close(self):
        self.menu_app.deiconify()
        self.destroy()

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
        current_directory = os.getcwd() 
        path = filedialog.askdirectory(initialdir=current_directory)  
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

