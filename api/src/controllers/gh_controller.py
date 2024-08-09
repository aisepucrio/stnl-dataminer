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
    
    async def get_tokens(self):
        return {"tokens": self.github_api.get_tokens()}
    
    async def get_commits_pydriller(self, repo_url: str):
        commits_request = self.github_api.get_commits_pydriller(repo_url)
        return {"commits": commits_request}

api = GitHubController(github_api=GitHubAPI())

@router.get("/test/{message}")
async def test_endpoint(message: str):
    return await api.test_endpoint(message)

@router.get("/check-internet-conection")
async def check_internet_conection():
    return await api.check_internet_conection()

@router.get("/get-tokens")
async def get_tokens():
    return await api.get_tokens()

@router.get("/get-commits-pydriller/{repo_name}")
async def get_commits_pydriller(repo_name: str):
    repo_name = repo_name.replace("_", "/")
    return await api.get_commits_pydriller(repo_name)



