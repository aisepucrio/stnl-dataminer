import os
import json
import customtkinter as ctk
from psycopg2 import sql, OperationalError, connect
from dotenv import load_dotenv, dotenv_values
from tkinter import Tk, Label, Button, messagebox

class Database:
    def __init__(self):
        # Carrega variáveis de ambiente do arquivo .env localizado duas pastas acima
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        self.dotenv_path = dotenv_path
        self.load_env_variables()

        self.host = os.getenv('PG_HOST')
        self.database = os.getenv('PG_DATABASE')
        self.user = os.getenv('PG_USER')
        self.password = os.getenv('PG_PASSWORD')
        self.port = os.getenv('PG_PORT')

        try:
            # Conecta ao banco de dados PostgreSQL usando variáveis de ambiente
            self.conn = connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            # Cria um cursor para executar comandos SQL
            self.cursor = self.conn.cursor()
            print(f"Connected to database {self.database} at {self.host}")
        except OperationalError as e:
            self.conn = None
            self.cursor = None
            print(f"Could not connect to the database: {e}")
            print(f"Host: {self.host}, Database: {self.database}, User: {self.user}, Port: {self.port}")
            self.handle_connection_error()

    def load_env_variables(self):
        if os.path.exists(self.dotenv_path):
            load_dotenv(self.dotenv_path, override=True)

    def handle_connection_error(self):
        def on_continue():
            root.destroy()

        def on_save():
            # Lê o conteúdo atual do arquivo .env
            existing_env_vars = dotenv_values(self.dotenv_path)
            
            # Atualiza as variáveis de ambiente do banco de dados com os novos valores
            existing_env_vars.update({
                'PG_HOST': host_entry.get(),
                'PG_DATABASE': database_entry.get(),
                'PG_USER': user_entry.get(),
                'PG_PASSWORD': password_entry.get(),
                'PG_PORT': port_entry.get(),
            })
            
            # Escreve as variáveis de volta no arquivo .env, mantendo os tipos de dados
            with open(self.dotenv_path, 'w') as f:
                for key, value in existing_env_vars.items():
                    if value.isdigit():
                        f.write(f"{key}={value}\n")
                    elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
                        f.write(f"{key}={value}\n")
                    else:
                        f.write(f"{key}='{value}'\n")  # Mantém strings entre aspas simples
            
            self.load_env_variables()
            root.destroy()
            # Tenta conectar novamente após salvar o .env
            self.__init__()

        ctk.set_appearance_mode("dark")

        root = ctk.CTk()
        root.title("Database Connection Error")
        root.configure(bg="#1e1e1e")

        entry_bg_color = "#2e2e2e"  # Cor um pouco mais escura para o frame das variáveis problemáticas
        entry_text_color = "white"
        button_bg_color = "#3e3e3e"
        button_fg_color = "white"

        ctk.CTkLabel(root, text="Could not connect to the database.", font=("Arial", 14), text_color="white").pack(pady=10)

        entry_frame = ctk.CTkFrame(root, fg_color=entry_bg_color, bg_color="#1e1e1e")
        entry_frame.pack(pady=10, padx=10)

        ctk.CTkLabel(entry_frame, text="PG_HOST:", font=("Arial", 12), text_color="white", bg_color=entry_bg_color).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        host_entry = ctk.CTkEntry(entry_frame, width=300, fg_color=entry_bg_color, text_color=entry_text_color, bg_color=entry_bg_color)
        host_entry.grid(row=0, column=1, pady=5, padx=5)
        host_entry.insert(0, self.host)

        ctk.CTkLabel(entry_frame, text="PG_DATABASE:", font=("Arial", 12), text_color="white", bg_color=entry_bg_color).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        database_entry = ctk.CTkEntry(entry_frame, width=300, fg_color=entry_bg_color, text_color=entry_text_color, bg_color=entry_bg_color)
        database_entry.grid(row=1, column=1, pady=5, padx=5)
        database_entry.insert(0, self.database)

        ctk.CTkLabel(entry_frame, text="PG_USER:", font=("Arial", 12), text_color="white", bg_color=entry_bg_color).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        user_entry = ctk.CTkEntry(entry_frame, width=300, fg_color=entry_bg_color, text_color=entry_text_color, bg_color=entry_bg_color)
        user_entry.grid(row=2, column=1, pady=5, padx=5)
        user_entry.insert(0, self.user)

        ctk.CTkLabel(entry_frame, text="PG_PASSWORD:", font=("Arial", 12), text_color="white", bg_color=entry_bg_color).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        password_entry = ctk.CTkEntry(entry_frame, width=300, show="*", fg_color=entry_bg_color, text_color=entry_text_color, bg_color=entry_bg_color)
        password_entry.grid(row=3, column=1, pady=5, padx=5)
        password_entry.insert(0, self.password)

        ctk.CTkLabel(entry_frame, text="PG_PORT:", font=("Arial", 12), text_color="white", bg_color=entry_bg_color).grid(row=4, column=0, sticky="e", pady=5, padx=5)
        port_entry = ctk.CTkEntry(entry_frame, width=300, fg_color=entry_bg_color, text_color=entry_text_color, bg_color=entry_bg_color)
        port_entry.grid(row=4, column=1, pady=5, padx=5)
        port_entry.insert(0, self.port)

        ctk.CTkButton(root, text="Skip", command=on_continue, fg_color=button_bg_color, hover_color="darkgray", bg_color="#1e1e1e", text_color=button_fg_color).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(root, text="Save and Retry", command=on_save, fg_color=button_bg_color, hover_color="darkgray", bg_color="#1e1e1e", text_color=button_fg_color).pack(side="right", padx=20, pady=20)

        root.mainloop()

    # Método para criar esquema e tabelas no banco de dados
    def create_schema_and_tables(self, repo_name):
        # Formata o nome do esquema substituindo caracteres especiais
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        
        # Cria esquema se não existir
        self.cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))

        # Cria tabela de commits se não existir
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.commits (
            sha VARCHAR(255) PRIMARY KEY,
            message TEXT,
            date TIMESTAMP,
            author VARCHAR(255)
        )""").format(sql.Identifier(schema_name)))
        
        # Cria tabela de issues se não existir
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.issues (
            number INTEGER PRIMARY KEY,
            title TEXT,
            state VARCHAR(50),
            creator VARCHAR(255),
            comments JSONB
        )""").format(sql.Identifier(schema_name)))
        
        # Cria tabela de pull requests se não existir
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.pull_requests (
            number INTEGER PRIMARY KEY,
            title TEXT,
            state VARCHAR(50),
            creator VARCHAR(255),
            comments JSONB
        )""").format(sql.Identifier(schema_name)))
        
        # Cria tabela de branches se não existir
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.branches (
            name VARCHAR(255) PRIMARY KEY,
            sha VARCHAR(255)
        )""").format(sql.Identifier(schema_name)))

        # Comita as alterações no banco de dados
        self.conn.commit()

    # Método para inserir commits na tabela
    def insert_commits(self, repo_name, commits):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for commit in commits:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.commits (sha, message, date, author) 
            VALUES (%s, %s, %s, %s) ON CONFLICT (sha) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (commit['sha'], commit['message'], commit['date'], commit['author']))
        # Comita as inserções no banco de dados
        self.conn.commit()

    # Método para inserir issues na tabela
    def insert_issues(self, repo_name, issues):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for issue in issues:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.issues (number, title, state, creator, comments) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (number) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (issue['number'], issue['title'], issue['state'], issue['creator'], json.dumps(issue['comments'])))
        # Comita as inserções no banco de dados
        self.conn.commit()

    # Método para inserir pull requests na tabela
    def insert_pull_requests(self, repo_name, pull_requests):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for pr in pull_requests:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.pull_requests (number, title, state, creator, comments) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (number) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (pr['number'], pr['title'], pr['state'], pr['creator'], json.dumps(pr['comments'])))
        # Comita as inserções no banco de dados
        self.conn.commit()

    # Método para inserir branches na tabela
    def insert_branches(self, repo_name, branches):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for branch in branches:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.branches (name, sha) 
            VALUES (%s, %s) ON CONFLICT (name) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (branch['name'], branch['sha']))
        # Comita as inserções no banco de dados
        self.conn.commit()
