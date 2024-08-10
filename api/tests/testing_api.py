import requests

class TestAPIEndpoints:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:8000/github" 

    def test_endpoint(self, message="hello"):
        response = requests.get(f"{self.BASE_URL}/test/{message}")
        print(response.json())

    def test_check_internet_conection(self):
        response = requests.get(f"{self.BASE_URL}/check-internet-conection")
        print(response.json())

    def test_get_tokens(self):
        response = requests.get(f"{self.BASE_URL}/get-tokens")
        print(response.json())

    def test_get_commits_pydriller(self, repo_name="aisepucrio_stnl-dataminer"):
        response = requests.get(f"{self.BASE_URL}/get-commits-pydriller/{repo_name}")
        print(response.json())

    def test_set_max_workers(self, max_workers):
        response = requests.get(f"{self.BASE_URL}/set-max-workers-to/{max_workers}")
        print(response.json())

    def test_add_github_credentials(self, username, token):
        response = requests.post(f"{self.BASE_URL}/add_github_credentials/{username}/{token}")
        print(response.json())

# Rodar os testes com pytest

tests = TestAPIEndpoints()
