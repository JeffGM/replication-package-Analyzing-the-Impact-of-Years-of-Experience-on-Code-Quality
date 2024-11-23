import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import sys
import os

class MaxCollected(Exception):  
    pass

# Add new constants at the top
LANGUAGES = ['en', 'es', 'pt', 'fr', 'ru', 'it', 'zc']
TECHNOLOGIES = ['javascript', 'python', 'php']
EXISTING_PROFILES_FILE = 'workana_profiles.csv'

def load_existing_profiles():
    """Load existing profiles to avoid duplicates"""
    existing_profiles = set()
    try:
        with open(EXISTING_PROFILES_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                existing_profiles.add(row['url'])
    except FileNotFoundError:
        pass
    return existing_profiles

def get_profile_links(driver, page, language, technology=None):
    """Modified to handle language and technology filters"""
    base_url = "https://www.workana.com"
    if technology:
        url = f"{base_url}/{language}/freelancers/{technology}?query=github.com&worker_type=0&page={page}"
    else:
        url = f"{base_url}/freelancers?language={language}&query=github.com&worker_type=0&page={page}"
    
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    profile_links = []
    for article in soup.find_all('article', class_='js-worker listing worker-item'):
        link = article.find('a', href=True)['href']
        profile_links.append(link)
    
    return profile_links

def get_profile_data(driver, profile_url):
    driver.get(profile_url)
    time.sleep(3)  # Wait for the page to load

    # Click on "Ver mais detalhes" link
    try:
        more_details_buttons = driver.find_elements(By.CSS_SELECTOR, "a.link.small")
        for button in more_details_buttons:
            if "Ver mais detalhes" in button.text:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)  # Wait for the additional content to load
    except Exception as e:
        print(f"Could not click 'Ver mais detalhes': {e}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    profile_data = {}
    
    profile_data['url'] = profile_url
    profile_data['name'] = soup.find('div', itemprop='name').text.strip() if soup.find('div', itemprop='name') else 'N/A'
    profile_data['title'] = soup.find('section', class_='profile-role').h1.text.strip() if soup.find('section', class_='profile-role') and soup.find('section', class_='profile-role').h1 else 'N/A'
    profile_data['location'] = soup.find('span', class_='country-name').text.strip() if soup.find('span', class_='country-name') else 'N/A'
    profile_data['hourly_rate'] = soup.find('div', class_='h3').text.strip() if soup.find('div', class_='h3') else 'N/A'
    profile_data['description'] = soup.find('div', id='section-description').text.strip().replace('\n', ' ').replace('\r', ' ') if soup.find('div', id='section-description') else 'N/A'
    profile_data['github'] = soup.find('a', href=lambda href: href and "github.com" in href)['href'] if soup.find('a', href=lambda href: href and "github.com" in href) else 'N/A'

    profile_data['skills'] = []
    
    skills_section = soup.find('div', id='section-skills')
    if skills_section:
        for row in skills_section.find_all('tr'):
            skill_name = row.find('td', class_='skills').text.strip() if row.find('td', class_='skills') else 'N/A'
            yoe = row.find_all('td')[3].text.rstrip() if len(row.find_all('td')) > 3 else 'N/A'
            if skill_name != 'N/A' and yoe != 'N/A':
                profile_data['skills'].append({'skill': skill_name, 'years_of_experience': yoe})
    
    return profile_data

def scrape_workana(num_pages, existing_profiles):
    """Modified to handle multiple languages and technologies"""
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    all_profiles = []
    
    try:
        # First pass: scrape by language
        for lang in LANGUAGES:
            print(f"Scraping profiles for language: {lang}")
            for page in range(1, num_pages + 1):
                profile_links = get_profile_links(driver, page, lang)
                for link in profile_links:
                    if link not in existing_profiles:
                        profile_data = get_profile_data(driver, link)
                        all_profiles.append(profile_data)
                        existing_profiles.add(link)

        # Second pass: scrape by technology
        for tech in TECHNOLOGIES:
            for lang in LANGUAGES:
                print(f"Scraping {tech} profiles for language: {lang}")
                for page in range(1, num_pages + 1):
                    profile_links = get_profile_links(driver, page, lang, tech)
                    for link in profile_links:
                        if link not in existing_profiles:
                            profile_data = get_profile_data(driver, link)
                            all_profiles.append(profile_data)
                            existing_profiles.add(link)

    finally:
        driver.quit()
    
    return all_profiles

# Modified main execution
def append_to_csv(profiles):
    """Append new profiles to the CSV file"""
    mode = 'a' if os.path.exists(EXISTING_PROFILES_FILE) else 'w'
    with open(EXISTING_PROFILES_FILE, mode=mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        if mode == 'w':  # Only write header for new file
            writer.writerow(['url', 'github', 'name', 'title', 'location', 'hourly_rate', 'skills', 'description'])
        for profile in profiles:
            skills = ', '.join([f"{skill['skill']} ({skill['years_of_experience']})" for skill in profile['skills']])
            writer.writerow([
                profile['url'],
                profile['github'],
                profile['name'],
                profile['title'],
                profile['location'],
                profile['hourly_rate'],
                skills,
                f'"""{profile["description"]}"""'
            ])

if __name__ == "__main__":
    num_pages_to_scrape = 17
    existing_profiles = load_existing_profiles()
    print(f"Found {len(existing_profiles)} existing profiles")
    
    new_profiles = scrape_workana(num_pages_to_scrape, existing_profiles)
    print(f"Scraped {len(new_profiles)} new profiles")
    
    append_to_csv(new_profiles)
    print(f"Total profiles after scraping: {len(existing_profiles) + len(new_profiles)}")
