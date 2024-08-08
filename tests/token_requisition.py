import requests

def get_github_rate_limit(tokens):
    tokens = tokens.split(',')
    for token in tokens:
        print(f'Analisando o token: {token}')
        url = "https://api.github.com/rate_limit"
        headers = {
            "Authorization": f"token {token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            core_limit = data['rate']['remaining']
            print(f'Requisições restantes: {core_limit}')
        else:
            raise Exception(f"Error fetching rate limit: {response.status_code}, {response.text}")

# Exemplo de uso:
tokens = ''
try:
    remaining_requests = get_github_rate_limit(tokens)
except Exception as e:
    print(str(e))
