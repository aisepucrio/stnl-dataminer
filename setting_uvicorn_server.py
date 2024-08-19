from api.apis import github_api

github_api = github_api.GitHubAPI()

github_api.start_uvicorn_server()