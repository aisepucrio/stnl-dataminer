from fastapi import APIRouter, HTTPException, Depends
from src.services.service_test import test
from src.services.gh_services import GitHubAPI

router = APIRouter()

class GitHubController:
    def __init__(self, github_api: GitHubAPI):
        self.github_api = github_api

    async def test_endpoint(self, message: str):
        test_service = test(message)
        return {"test_service": test_service}

    async def check_internet_conection(self):
        connection = self.github_api.check_internet_connection()
        return {"message": connection}
    
    async def set_usage_of_database(self, database_usage: bool):
        return {"message": self.github_api.usage_of_database(database_usage)}
    
    async def get_max_workers(self):
        return {"max_workers": self.github_api.get_max_workers()}
    
    async def get_tokens(self):
        return {"tokens": self.github_api.get_tokens()}
    
    async def get_github_credentials(self):
        return {"credentials": self.github_api.get_github_credentials()}

    async def get_commits_pydriller(self, repo_url: str):
        commits_request = self.github_api.get_commits_pydriller(repo_url)
        return {"commits": commits_request}
    
    async def set_max_workers(self, max_workers: int):
        max_workers = str(max_workers)
        self.github_api.set_max_workers(max_workers)
        return {"message": f"Max workers set to {max_workers}"}
    
    async def set_save_path(self, save_path: str):
        self.github_api.set_save_path(save_path)
        return {"message": f"Save path set to {save_path}"}
    
    async def add_github_credentials(self, username: str, token: str):
        self.github_api.add_github_credentials(username, token)
        return {"message": f"Token {token} added to {username}"}
    
api = GitHubController(github_api=GitHubAPI())

@router.get("/test_endpoint/{message}")
async def test_endpoint(message: str):
    return await api.test_endpoint(message)

@router.get("/check-internet-conection")
async def check_internet_conection():
    return await api.check_internet_conection()

@router.post("/set-usage-of-database/{database_usage}")
async def set_usage_of_database(database_usage: bool):
    return await api.set_usage_of_database(database_usage)

@router.get("/get-max-workers")
async def get_max_workers():
    return await api.get_max_workers()

@router.get("/get-github-credentials")
async def get_github_credentials():
    return await api.get_github_credentials()

@router.get("/get-commits/{repo_name}")
async def get_commits_pydriller(repo_name: str):
    repo_name = repo_name.replace("_", "/")
    return await api.get_commits_pydriller(repo_name)

@router.get("/set-max-workers-to/{max_workers}")
async def set_max_workers(max_workers: int):
    return await api.set_max_workers(max_workers)

@router.post("/set-save-path/{save_path}")
async def set_save_path(save_path: str):
    return await api.set_save_path(save_path)

@router.post("/add_github_credentials/{username}/{token}")
async def add_github_credentials(username: str, token: str):
    return await api.add_github_credentials(username, token)
