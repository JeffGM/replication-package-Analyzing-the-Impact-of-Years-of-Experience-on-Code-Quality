# Replication Package for the Study: "Aged to Perfection? Analyzing the Impact of Years of Experience on Code Quality"

## Replication Package Structure

### Programs for Data Extraction and Summarization
These programs extract and summarize information from sources such as GitHub, Workana, and SonarQube.

- **`scraper.py`**: Collects public Workana profiles relevant to the research scope. The results are saved in `workana_profiles.csv`.
- **`fetch_repos.py`**: Downloads up to five Git repositories for each developer listed in `workana_profiles.csv`.
- **`fetch_sonar_qube.py`**: Uses SonarQube to analyze repositories and generate reports for each repository folder.
- **`aggregator.py`**: Consolidates all SonarQube reports for a given developer into a unified report, which is stored in each developer’s folder.

### Helper Programs
These programs assist with miscellaneous tasks.

- **`other_tools_and_helpers/anonimize_workana_profile_names`**: Replaces names in the profiles with anonymous identifiers.
- **`other_tools_and_helpers/get_github_repo_links`**: Generates a list of all downloaded repositories for each developer. The results are saved in `github_repo_links.csv`.

### Analysis Programs
- **`analysis.py`**: Conducts statistical tests and descriptive analyses of the collected data. This program populates the `metrics-dataset` folder with summarized reports and creates the consolidated file `all_developer_metrics_workana_sonarqube.csv`.

### Data Files
- **`workana_profiles.csv`**: Contains the collected Workana profiles. To protect privacy, sensitive information has been redacted and replaced with `[REDACTED]`.
- **`github_repo_links.csv`**: Lists the GitHub repository links analyzed during the study.
- **`collected_repos_report.xlsx`**: Provides a summary of all collected repositories, including the programming languages used.
- **`metrics-dataset` folder**: Contains the summarized metrics extracted by SonarQube for each developer.
- **`all_developer_metrics_workana_sonarqube.csv`**: Aggregates the years of experience and SonarQube metrics for each developer. This file serves as the final dataset for statistical analysis.

## Execution
To replicate the study, follow these steps:

1. **Extract Workana profiles**: Run `scraper.py`.
2. **Collect GitHub repositories**: Execute `fetch_repos.py`, ensuring that a GitHub API key is configured.
3. **Analyze repositories with SonarQube**: Use the latest version of SonarQube Community Edition (as of November 2024). Ensure that the server is running locally on port 9001.
4. **Summarize metrics**: Run `aggregator.py` to consolidate the SonarQube analysis results.
5. **Analyze the data**: Execute the cells in `analysis.ipynb` to perform the final statistical analysis.
