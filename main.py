import os
import requests
import git
from git import Repo

# Configuration
GITHUB_USERNAME = 'AlexDev404'
# The below token is invalid, so don't even think of trying it
GITHUB_TOKEN = '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'  # Create a personal access token from GitHub settings with scope "repo"
BASE_DIR = '.'  # Directory with all your local Git repos
GITHUB_API_URL = 'https://api.github.com'


# Helper function to delete a repository on GitHub
def delete_github_repo(repo_name):
    url = f'{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f'Successfully deleted GitHub repo: {repo_name}')
    elif response.status_code == 404:
        print(f'Repo {repo_name} not found on GitHub. Skipping deletion.')
    else:
        print(f'Error deleting repo {repo_name}: {response.text}')


# Helper function to create a repository on GitHub
def create_github_repo(repo_name, is_private=True):
    url = f'{GITHUB_API_URL}/user/repos'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }
    data = {
        'name': repo_name,
        'private': is_private,
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print(f'Successfully created GitHub repo: {repo_name}')
    elif response.status_code == 422 and 'already exists' in response.text:
        print(f'Repo {repo_name} already exists on GitHub.')
    else:
        print(f'Error creating repo {repo_name}: {response.text}')

# Function to push the repo to GitHub
def push_to_github(repo_path, repo_name):
    try:
        repo = Repo(repo_path)
        remote_url = f'https://github.com/{GITHUB_USERNAME}/{repo_name}.git'

        # Check if remote is already set
        if 'origin' in repo.remotes:
            origin = repo.remotes.origin
            print(f'Pushing updates to existing remote: {remote_url}')
        else:
            origin = repo.create_remote('origin', remote_url)
            print(f'Created remote at {remote_url}')

        # Add the files
        repo.git.add(all=True)

        # Commit the files
        repo.index.commit("Initial commit")

        # Push to GitHub
        origin.push(refspec='refs/heads/*:refs/heads/*')
        print(f'Successfully pushed {repo_name} to GitHub.')
        # delete_github_repo(repo_name)
        # # Remove all remotes before adding the new one
        # for remote in repo.remotes:
        #     repo.delete_remote(remote)
        #     print(f'Remote {remote.name} removed.')
    except git.exc.GitCommandError as e:
        print(f'Error pushing {repo_name}: {e}')

# Main function
def push_all_repos():
    for folder_name in os.listdir(BASE_DIR):
        repo_path = os.path.join(BASE_DIR, folder_name)

        if os.path.isdir(repo_path):
            try:
                repo = Repo(repo_path)
                if repo.bare:
                    print(f'{folder_name} is not a valid Git repository. Skipping.')
                    continue

                # Create GitHub repo if not already created
                create_github_repo(folder_name, False)

                # Push to GitHub
                push_to_github(repo_path, folder_name)
            except git.exc.InvalidGitRepositoryError:
                print(f'{folder_name} is not a Git repository. Skipping.')

if __name__ == '__main__':
    push_all_repos()
