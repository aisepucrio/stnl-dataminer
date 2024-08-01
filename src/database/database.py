import os
import json
import customtkinter as ctk
from psycopg2 import sql, connect
from dotenv import load_dotenv
from tkinter import messagebox

class Database:
    def __init__(self):
        # Carrega variáveis de ambiente do arquivo .env localizado duas pastas acima
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        self.dotenv_path = dotenv_path
        self.load_env_variables()

        self.host = self.clean_string(os.getenv('PG_HOST'))
        self.database = self.clean_string(os.getenv('PG_DATABASE'))
        self.user = self.clean_string(os.getenv('PG_USER'))
        self.password = self.clean_string(os.getenv('PG_PASSWORD'))
        self.port = self.clean_string(os.getenv('PG_PORT'))

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
        except Exception as e:
            self.conn = None
            self.cursor = None
            messagebox.showwarning("Warning", "Database connection could not be established. Skipping database operations.")

    def clean_string(self, input_str):
        if (input_str is not None):
            try:
                return input_str.encode('latin1').decode('utf-8')
            except UnicodeDecodeError:
                return input_str  # Retorna a string original se a decodificação falhar
        return input_str

    def load_env_variables(self):
        if os.path.exists(self.dotenv_path):
            load_dotenv(self.dotenv_path, override=True)

        for key, value in os.environ.items():
            os.environ[key] = self.clean_string(value)

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
