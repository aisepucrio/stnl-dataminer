import os
import json
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            port=os.getenv('PG_PORT')
        )
        self.cursor = self.conn.cursor()

    def create_schema_and_tables(self, repo_name):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        
        self.cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))

        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.commits (
            sha VARCHAR(255) PRIMARY KEY,
            message TEXT,
            date TIMESTAMP,
            author VARCHAR(255)
        )""").format(sql.Identifier(schema_name)))
        
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.issues (
            number INTEGER PRIMARY KEY,
            title TEXT,
            state VARCHAR(50),
            creator VARCHAR(255),
            comments JSONB
        )""").format(sql.Identifier(schema_name)))
        
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.pull_requests (
            number INTEGER PRIMARY KEY,
            title TEXT,
            state VARCHAR(50),
            creator VARCHAR(255),
            comments JSONB
        )""").format(sql.Identifier(schema_name)))
        
        self.cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {}.branches (
            name VARCHAR(255) PRIMARY KEY,
            sha VARCHAR(255)
        )""").format(sql.Identifier(schema_name)))

        self.conn.commit()

    def insert_commits(self, repo_name, commits):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for commit in commits:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.commits (sha, message, date, author) 
            VALUES (%s, %s, %s, %s) ON CONFLICT (sha) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (commit['sha'], commit['message'], commit['date'], commit['author']))
        self.conn.commit()

    def insert_issues(self, repo_name, issues):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for issue in issues:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.issues (number, title, state, creator, comments) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (number) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (issue['number'], issue['title'], issue['state'], issue['creator'], json.dumps(issue['comments'])))
        self.conn.commit()

    def insert_pull_requests(self, repo_name, pull_requests):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for pr in pull_requests:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.pull_requests (number, title, state, creator, comments) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (number) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (pr['number'], pr['title'], pr['state'], pr['creator'], json.dumps(pr['comments'])))
        self.conn.commit()

    def insert_branches(self, repo_name, branches):
        schema_name = repo_name.replace('/', '_').replace('-', '_')
        for branch in branches:
            self.cursor.execute(sql.SQL("""
            INSERT INTO {}.branches (name, sha) 
            VALUES (%s, %s) ON CONFLICT (name) DO NOTHING
            """).format(sql.Identifier(schema_name)),
            (branch['name'], branch['sha']))
        self.conn.commit()
