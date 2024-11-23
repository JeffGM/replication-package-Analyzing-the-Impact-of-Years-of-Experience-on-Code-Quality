import requests
import csv
import os
import sys
from collections import defaultdict
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# SonarQube server details
SONARQUBE_URL = 'http://localhost:9001'
SONARQUBE_TOKEN = 'SONARQUBE_TOKEN'  # Replace with your SonarQube token

# Metrics to fetch
METRICS = 'ncloc'

def get_project_issues(project_key):
    url = f"{SONARQUBE_URL}/api/issues/search?componentKeys={project_key}&ps=500"
    response = requests.get(url, auth=(SONARQUBE_TOKEN, ''))
    return response.json()

def get_file_metrics(project_key):
    url = f"{SONARQUBE_URL}/api/measures/component_tree?component={project_key}&metricKeys={METRICS}"
    response = requests.get(url, auth=(SONARQUBE_TOKEN, ''))

    return response.json()

def generate_reports(project_key, dir, recursions=0):
    issues_data = get_project_issues(project_key)
    file_metrics_data = get_file_metrics(project_key)

    if len(file_metrics_data['components']) == 0:
        if recursions >= 3:
            print(f"Repository {project_key} couldn't be analyzed")
            return
        
        time.sleep(20)
        return generate_reports(project_key, dir, recursions+1)

    # Detailed issues report
    issues_file = f'{dir}/{project_key}_issues.csv'
    with open(issues_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Key', 'Component', 'File Extension', 'Rule', 'Type', 'Impact', 'Severity', 'Status', 'Message'])
        for issue in issues_data['issues']:
            component = issue['component']
            file_extension = component.split('.')[-1] if '.' in component else 'unknown'
            writer.writerow([
                issue['key'], component, file_extension, issue['rule'], issue['type'], issue['impacts'],
                issue['severity'], issue['status'], issue['message']
            ])

    # Consolidated report by file extension
    consolidated_data = defaultdict(lambda: {'minor': 0, 'major': 0, 'critical': 0, 'loc': 0})

    # Populate the consolidated data with issues
    for issue in issues_data['issues']:
        component = issue['component']
        file_extension = component.split('.')[-1] if '.' in component else 'unknown'
        severity = issue['severity'].lower()
        if severity in consolidated_data[file_extension]:
            consolidated_data[file_extension][severity] += 1

    # Populate the consolidated data with LOC
    for component in file_metrics_data['components']:
        if component['qualifier'] == "FIL":
            file_extension = component['path'].split('.')[-1] if '.' in component['path'] else 'unknown'

            if file_extension == 'unknown':
                continue

            if len(component['measures']) == 0:
                continue

            loc = int(component['measures'][0]['value'])
            consolidated_data[file_extension]['loc'] += loc

    # Save consolidated data to CSV
    consolidated_file = f'{dir}/{project_key}_consolidated.csv'
    with open(consolidated_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['File Extension', 'Minor Issues', 'Major Issues', 'Critical Issues', 'Total LOC'])
        for file_extension, data in consolidated_data.items():
            writer.writerow([file_extension, data['minor'], data['major'], data['critical'], data['loc']])

    print(f"Reports generated: {issues_file}, {consolidated_file}")

def check_project_exists(project_key):
    url = f"{SONARQUBE_URL}/api/projects/search?projects={project_key}"
    response = requests.get(url, auth=(SONARQUBE_TOKEN, ''))
    if response.status_code == 200:
        data = response.json()
        return len(data.get('components', [])) > 0
    return False

def create_project_in_sonarqube(project_key, project_name):
    # Check if project already exists
    if check_project_exists(project_key):
        print(f"Project {project_name} already exists in SonarQube with key {project_key}")
        return True
        
    url = f"{SONARQUBE_URL}/api/projects/create"
    data = {
        'name': project_name,
        'project': project_key
    }
    response = requests.post(url, data=data, auth=(SONARQUBE_TOKEN, ''))
    if response.status_code == 200:
        print(f"Project {project_name} created in SonarQube with key {project_key}")
        return True
    else:
        print(f"Failed to create project {project_name} in SonarQube: {response.text}")
        return False

def scan_repository(repo_path, project_key):
    # Create a unique scanner work directory for this scan
    scanner_work_dir = os.path.join(repo_path, ".scannerwork_" + project_key + "_" + str(time.time()))
    
    # Ensure the directory exists
    os.makedirs(scanner_work_dir, exist_ok=True)
    
    scan_command = (
        f"sonar-scanner "
        f"-Dsonar.projectKey={project_key} "
        f"-Dsonar.sources={repo_path} "
        f"-Dsonar.host.url={SONARQUBE_URL} "
        f"-Dsonar.token={SONARQUBE_TOKEN} "
        f"-Dsonar.scm.exclusions.disabled=true "
        f"-Dsonar.inclusions=**/*.js,**/*.jsx,**/*.php,**/*.py "
        f"-Dsonar.exclusions=**/node_modules/**,**/vendor/**,**/dist/**,**/.git/** "
        f"-Dsonar.working.directory={scanner_work_dir} "  # Set unique working directory
    )
    os.system(scan_command)

def process_repository(repo_info):
    repo_path, project_key, project_name = repo_info
    
    # Ensure project key is unique and valid
    # Replace any invalid characters and ensure uniqueness
    safe_project_key = project_key.lower().replace(' ', '_').replace('-', '_')
    
    # Create the project in SonarQube if it doesn't exist
    if check_project_exists(safe_project_key):
        print(f"Skipping {project_name} as it already exists in SonarQube")
        return
        
    if not create_project_in_sonarqube(safe_project_key, project_name):
        return
    
    # Scan the repository
    print(f"Start scanning repository {safe_project_key}")
    print("\n")
    scan_repository(repo_path, safe_project_key)

    # Give SonarQube some time to process before generating reports
    time.sleep(10)

    # Generate reports
    print(f"Start generating reports for repository {safe_project_key}")
    print("\n")
    generate_reports(safe_project_key, repo_path)

def main():
    repos_base_path = 'repos_v2'
    repository_info = []
    
    # Collect all repository information
    for user_folder in os.listdir(repos_base_path):
        user_path = os.path.join(repos_base_path, user_folder)
        if os.path.isdir(user_path):
            for repo_folder in os.listdir(user_path):
                repo_path = os.path.join(user_path, repo_folder)
                if os.path.isdir(repo_path):
                    # Create a unique project key using both user and repo name
                    project_key = f"{user_folder}_{repo_folder}"
                    project_name = f"{user_folder}/{repo_folder}"
                    repository_info.append((repo_path, project_key, project_name))

    # Process repositories in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_repository, repo_info) for repo_info in repository_info]
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
