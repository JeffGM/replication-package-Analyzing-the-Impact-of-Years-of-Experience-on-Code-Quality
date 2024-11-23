import os
import csv
from git import Repo

# Define the path to the repos_v2 folder
repos_folder = '../repos_v2'

# Define the output CSV file
output_csv = '../github_repo_links.csv'

# Open the CSV file for writing
with open(output_csv, mode='w', newline='') as csv_file:
    fieldnames = ['Username', 'Repo Name', 'Remote URL']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Iterate over each user directory in the repos_v2 folder
    for username in os.listdir(repos_folder):
        user_path = os.path.join(repos_folder, username)

        # Check if the path is a directory
        if os.path.isdir(user_path):
            # Iterate over each repo directory within the user directory
            for repo_name in os.listdir(user_path):
                repo_path = os.path.join(user_path, repo_name)

                # Check if the path is a directory and contains a .git folder
                if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, '.git')):
                    try:
                        # Open the repository
                        repo = Repo(repo_path)

                        # Get the remote URL
                        remote_url = next(repo.remote().urls)

                        # Write the data to the CSV file
                        writer.writerow({'Username': username, 'Repo Name': repo_name, 'Remote URL': remote_url})

                    except Exception as e:
                        print(f"Error processing repository {repo_name} for user {username}: {e}")

print(f"CSV file '{output_csv}' has been created.")