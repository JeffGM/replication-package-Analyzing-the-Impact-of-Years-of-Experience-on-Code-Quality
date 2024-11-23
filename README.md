# Replication package of the study 'Aged to Perfection? Analyzing the Impact of Years of Experience on Code Quality'

## Replication Package Structure

### Extraction and sumarization programs: Used to extract information from sources, i.e. GitHub, Workana, SonarQube. 
- scraper.py: Collects public Workana profiles that match the research interest. The results are saved in the file workana_profiles.csv;
- fech_repos.py: Downloads up to 5 Git repositories for each developer listed on workana_profiles.csv;
- fetch_sonar_qube.py: Uses SonarQube to run analysis on the repositories and create reports on each repository folder;
- agregator.py: Joins all SonarQube reports from a given developer and creates a unified report, available in each developer folder;

### Helper programs: Used to perform other miscelaneous tasks
- other_tools_and_helpers/anonimize_workana_profile_names: Replaces the column name for anonymous identifiers;
- other_tools_and_helpers/get_github_repo_links: Creates a list of all repositories downloaded, per developer. The results are saved in the file github_repo_links.csv

### Analysis programs
- analysis.py: Performs statistical tests and descriptive analysis of the collected data. The program will fill the folder metrics-dataset with the reports and join every file in the all_developer_metrics_workana_sonarqube.csv file;

### Data files
- workana_profiles.csv: Contains all the public Workana profiles collected during the extraction. Due to privacy concerns, the available version contains the mark [REDACTED] on given words or phrases to protect sensive information.
- github_repo_links.csv: Contains all links to the analyzed GitHub repositories;
- collected_repos_report.xlsx: Contains a list of all repositories collected and which languages the repository contains;
- metrics-dataset folder: Contains all summarized metrics extracted by SonarQube for each developer;
- all_developer_metrics_workana_sonarqube.csv: Each line corresponds to a developer, containing the years of experience and SonarQube metrics. This file is the final result of the collection process, before statistc analysis and calculations are performed;
    
## Execution
To execute the study, the following steps should be taken:
- Extract Workana profiles with scraper.py
- Collect the GitHub repositories with fetch_repos.py. It is necessary to configure a GitHub API key;
- Run SonarQube analysis on the downloaded repositories. This study utilized the latest available version of SonarQube Community Edition on Nov 2024. The script expects that this version is running on a local server on port 9001;
- Execute the program agregator.py, to summarize the SonarQube metrics;
- Finally, run the cells of the program analysis.ipynb to analyze the results.