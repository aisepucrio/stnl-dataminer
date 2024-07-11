from model.api_gh import GitHubAPI
from database.database_gh import Database

class GitHubController:
    def __init__(self):
        self.api = GitHubAPI()
        self.db = Database()
        self.stop_process_flag = False

    def collect_data(self, repo_url, start_date, end_date, options, max_workers, update_progress_callback, progress_step):
        repo_name = self.api.get_repo_name(repo_url)
        self.db.create_schema_and_tables(repo_name)
        
        start_date_iso = start_date.strftime('%Y-%m-%d') + 'T00:00:01Z'
        end_date_iso = end_date.strftime('%Y-%m-%d') + 'T23:59:59Z'

        data = {}

        if options.get('commits'):
            data['commits'] = self.api.get_commits(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_commits(repo_name, data['commits'])
            update_progress_callback(progress_step)

        if options.get('issues'):
            data['issues'] = self.api.get_issues(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_issues(repo_name, data['issues'])
            update_progress_callback(progress_step)

        if options.get('pull_requests'):
            data['pull_requests'] = self.api.get_pull_requests(repo_name, start_date_iso, end_date_iso, max_workers)
            self.db.insert_pull_requests(repo_name, data['pull_requests'])
            update_progress_callback(progress_step)

        if options.get('branches'):
            data['branches'] = self.api.get_branches(repo_name, max_workers)
            self.db.insert_branches(repo_name, data['branches'])
            update_progress_callback(progress_step)

        self.api.save_to_json(data, f"{repo_name.replace('/', '_').replace('-', '_')}.json")
        
        return data

    def stop_process(self):
        self.stop_process_flag = True
