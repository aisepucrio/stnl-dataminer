import requests

GITHUB_TOKEN = ''
REPO = 'pandas-dev/pandas'

def get_pull_request_tags(repo, token):
    url = f'https://api.github.com/repos/{repo}/pulls?state=all'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        pulls = response.json()
        pull_request_tags = []

        for pr in pulls:
            pr_number = pr['number']
            pr_url = pr['url']

            pr_response = requests.get(pr_url, headers=headers)
            if pr_response.status_code == 200:
                pr_data = pr_response.json()
                tags = [label['name'] for label in pr_data.get('labels', [])]
                pull_request_tags.append({
                    'number': pr_number,
                    'title': pr_data['title'],
                    'tags': tags
                })
            else:
                print(f"Falha ao obter detalhes do PR #{pr_number}")

        return pull_request_tags
    else:
        print(f"Falha ao obter pull requests: {response.status_code}")
        return []

if __name__ == "__main__":
    tags = get_pull_request_tags(REPO, GITHUB_TOKEN)
    for tag in tags:
        print(f"PR #{tag['number']}: {tag['title']} - Tags: {', '.join(tag['tags'])}")
