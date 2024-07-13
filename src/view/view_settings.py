import customtkinter as ctk
from tkinter import messagebox, Toplevel, Listbox
from dotenv import load_dotenv, set_key, dotenv_values
import os

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
        self.geometry("705x245")
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
                f.write('TOKENS=\nUSERNAMES=\nEMAIL=\nAPI_TOKEN=\n')
        
        load_dotenv(self.env_file)
        
        env_values = dotenv_values(self.env_file)
        self.tokens = env_values.get('TOKENS', '').split(',')
        self.usernames = env_values.get('USERNAMES', '').split(',')
        self.emails = env_values.get('EMAIL', '').split(',')
        self.api_tokens = env_values.get('API_TOKEN', '').split(',')

        # Ensure all required keys are present in the .env file
        self.ensure_env_key('TOKENS')
        self.ensure_env_key('USERNAMES')
        self.ensure_env_key('EMAIL')
        self.ensure_env_key('API_TOKEN')

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

        # Max Workers
        self.max_workers_label = ctk.CTkLabel(self, text="Number of Max Workers:")
        self.max_workers_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.max_workers_entry = ctk.CTkEntry(self, width=200)
        self.max_workers_entry.grid(row=4, column=1, padx=10, pady=10)

    def update_env_file(self, key, value):
        set_key(self.env_file, key, value)

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

if __name__ == "__main__":
    app = SettingsApp()
    app.mainloop()
