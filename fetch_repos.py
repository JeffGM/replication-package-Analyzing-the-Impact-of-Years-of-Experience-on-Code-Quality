import csv
import os
import requests
from github import Github
import pandas as pd
from datetime import datetime, timedelta

# Constants
CSV_FILE = 'workana_profiles.csv'
REPO_FOLDER = 'repos_v2'
GITHUB_TOKEN = 'GITHUB_TOKEN'  # Replace with your GitHub token
ALLOWED_LANGUAGES = ['javascript', 'python', 'php']
REPO_PER_USER = 5
EXCEL_REPORT = 'collected_repos_report.xlsx'

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)
log_file = open("fetch_repos.txt", "a")

# Add this new list at the top level to store report data
report_data = []

# function that prints message and write it to a file
def log_m(message):
    print(message)
    log_file.write(message + '\n')


def read_csv(file_path):
    freelancers = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            freelancers.append(row)
    return freelancers

def get_github_username(url):
    return url.rstrip('/').split('/')[-1]

def get_repo_languages(repo):
    languages = repo.get_languages()
    return [lang.lower() for lang in languages.keys()]

def download_repository(repo_url, repo_name, user):
    os.system(f'git clone {repo_url} {REPO_FOLDER}/{user}/{repo_name}')

def has_single_author(repo):
    contributors = repo.get_contributors()
    return contributors.totalCount == 1

def has_allowed_languages(repo_languages):
    return any(language.lower() in repo_languages for language in ALLOWED_LANGUAGES)

def main():
    if not os.path.exists(REPO_FOLDER):
        os.makedirs(REPO_FOLDER)

    freelancers = read_csv(CSV_FILE)

    for freelancer in freelancers:
        github_username = get_github_username(freelancer['github'])
        skills = [skill.split('(')[0].strip().lower() for skill in freelancer['skills'].split(',')]
        
        try:
            user = g.get_user(github_username)
            repos = user.get_repos()
            # Sort by largest size first
            repos = sorted(repos, key=lambda x: (x.size * -1))
            collected_repos = 0

            log_m(f"User: {user}")
            log_m(f"Skills: {skills}")

            # Check if user has any of the skills
            if not any(allowed_language in skills for allowed_language in ALLOWED_LANGUAGES):
                log_m(f"User {user} does not have any of the allowed languages. Skipping. It have the languages: {skills}")
                log_m("\n")
                log_m("\n")
                continue

            for repo in repos:
                if collected_repos >= REPO_PER_USER:
                    break
                
                log_m(f"Repo: {repo.name}. Size: {repo.size}")

                # Check if repo had activity in the past 5 years
                if repo.pushed_at < datetime.now(repo.pushed_at.tzinfo) - timedelta(days=5*365):
                    log_m(f"Skipping repository with no activity in the past 5 years: {repo.name}")
                    log_m("\n")
                    continue

                if repo.fork:
                    log_m(f"Skipping forked repository: {repo.name}")
                    log_m("\n")
                    continue

                repo_languages = get_repo_languages(repo)

                log_m(f"Languages in repo: {repo_languages}")

                has_languages = has_allowed_languages(repo_languages)
                single_author = has_single_author(repo)
                
                if has_languages and single_author:
                    log_m(f'Downloading repository: {repo.name}')
                    if not os.path.exists(f'{REPO_FOLDER}/{github_username}/{repo.name}'):
                        download_repository(repo.clone_url, repo.name, github_username)
                        # Add repository info to report data with binary language flags
                        report_data.append({
                            'username': github_username,
                            'repository': repo.name,
                            'javascript': 1 if 'javascript' in repo_languages else 0,
                            'python': 1 if 'python' in repo_languages else 0,
                            'php': 1 if 'php' in repo_languages else 0
                        })
                    else:
                        log_m(f'Repository already downloaded: {repo.name}')
                    collected_repos += 1
                elif not has_languages:
                    log_m(f'Repository skipped. No relevant languages found: {repo_languages}')
                elif not single_author:
                    log_m(f'Repository skipped. There is no single author: {single_author}')
                
                log_m("\n")

            log_m(f"Collected {collected_repos} repositories from user {user}")
            log_m("\n")
            log_m("\n")

        except Exception as e:
            log_m(f"Error processing user {freelancer['name']}: {e}")

    # Create and save the report at the end of main()
    if report_data:
        df = pd.DataFrame(report_data)
        df.to_excel(EXCEL_REPORT, index=False)
        log_m(f"Report saved to {EXCEL_REPORT}")

if __name__ == '__main__':
    main()
    log_file.close()
