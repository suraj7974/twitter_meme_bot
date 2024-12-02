from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

linkedin_gmail = os.getenv('LINKEDIN_EMAIL')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')

COMPANY_IDS_FILE = 'company_ids.json'
JOBS_OUTPUT_FILE = 'linkedin_jobs.json'

def load_or_create_company_ids():
    """Load company IDs from JSON or create a new file if it doesn't exist"""
    try:
        if not os.path.exists(COMPANY_IDS_FILE):

            default_companies = {
                "microsoft": "1035",
                "amazon": "1586",
            }
            
            with open(COMPANY_IDS_FILE, 'w') as f:
                json.dump(default_companies, f, indent=2)
            
            return default_companies
        
        # Load existing company IDs
        with open(COMPANY_IDS_FILE, 'r') as f:
            return json.load(f)
    
    except Exception as e:
        print(f"Error loading/creating company IDs: {e}")
        return {}

def update_company_ids(new_company_ids):
    """Update the company IDs file"""
    try:
        with open(COMPANY_IDS_FILE, 'r') as f:
            existing_ids = json.load(f)
        
        # Update existing IDs with new ones
        existing_ids.update(new_company_ids)
        
        with open(COMPANY_IDS_FILE, 'w') as f:
            json.dump(existing_ids, f, indent=2)
        
        print("Company IDs updated successfully.")
    except Exception as e:
        print(f"Error updating company IDs: {e}")

def setup_driver():
    options = Options()
    options.headless = False
    options.add_experimental_option("detach", True)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

def login_to_linkedin(driver):
    try:
        driver.get("https://www.linkedin.com/login")

        username_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_elem.send_keys(linkedin_gmail)

        password_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_elem.send_keys(linkedin_password)

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        submit_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav-search"))
        )
        return True

    except TimeoutException:
        print("Timeout while trying to log in")
        return False
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

from urllib.parse import urlparse

def extract_job_data(job_card):
    """Extract job details including title, link, location, and skills from a job card element."""
    try:
        job_data = {
            'title': '',
            'link': ''
        }

        # Extract job title
        try:
            title_elem = job_card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
            job_data['title'] = title_elem.text.strip().split('\n')[0]
        except:
            try:
                title_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                job_data['title'] = title_elem.text.strip().split('\n')[0]
            except Exception as e:
                print(f"Title not found: {e}")

        # Extract job link and clean it
        try:
            link_elem = job_card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            raw_link = link_elem.get_attribute('href')
            parsed_url = urlparse(raw_link)  # Parse the URL
            cleaned_link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"  # Reconstruct the base URL
            job_data['link'] = cleaned_link
        except:
            try:
                link_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                raw_link = link_elem.get_attribute('href')
                parsed_url = urlparse(raw_link)
                cleaned_link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                job_data['link'] = cleaned_link
            except Exception as e:
                print(f"Link not found: {e}")

        return job_data

    except Exception as e:
        print(f"Error extracting job data: {e}")
        return None




def save_to_json(jobs_data):
    """Save jobs data to a JSON file, overwriting previous content"""
    try:
        # Create the data structure with metadata
        data_to_save = {
            "metadata": {
                "total_jobs": len(jobs_data),
                "search_criteria": {
                    "work_type": "Company Jobs"
                },
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "jobs": jobs_data
        }
        
        # Save to JSON file with nice formatting, overwriting previous content
        with open(JOBS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(jobs_data)} jobs to {JOBS_OUTPUT_FILE}")
        return True
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")
        return False

def scrape_jobs_for_company(driver, company_name, company_ids):
    """Scrape jobs for a specific company using company ID"""
    try:
        # Get company ID, default to None if not found
        company_id = company_ids.get(company_name.lower())
        if not company_id:
            print(f"No company ID found for {company_name}")
            return []

        # Construct job search URL using company ID
        job_search_url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?currentJobId=&f_C={company_id}"
            "&geoId=102713980"
            "&origin=JOB_SEARCH_PAGE_JOB_FILTER"
            "&refresh=true"
        )
        
        # Navigate to the job search URL
        driver.get(job_search_url)

        # Wait for initial page load
        time.sleep(5)

        # Scroll through the page to load jobs
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # Scroll up to 3 times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        # Extract data from each job card
        jobs_data = []
        for job_card in job_cards:
            job_data = extract_job_data(job_card)
            if job_data:
                job_data['company'] = company_name.capitalize()
                jobs_data.append(job_data)
        
        print(f"Scraped {len(jobs_data)} jobs for {company_name}")
        return jobs_data

    except Exception as e:
        print(f"Error scraping jobs for {company_name}: {str(e)}")
        return []

def main():
    driver = None
    try:
        # Load company IDs
        company_ids = load_or_create_company_ids()
        
        # List of companies to scrape (use keys from company_ids)
        companies = list(company_ids.keys())
        
        # All jobs will be collected here
        all_companies_jobs = []

        # Setup driver and login
        driver = setup_driver()

        if not login_to_linkedin(driver):
            raise Exception("Failed to login to LinkedIn")

        print("Successfully logged in to LinkedIn")

        # Scrape jobs for each company
        for company in companies:
            print(f"Scraping jobs for {company}")
            
            # Scrape jobs for current company
            company_jobs = scrape_jobs_for_company(driver, company, company_ids)
            
            # Extend the all jobs list
            all_companies_jobs.extend(company_jobs)
            
            # Add a small delay between company searches
            time.sleep(3)

        # Save all jobs to a JSON file
        if all_companies_jobs:
            save_to_json(all_companies_jobs)
        
        print(f"Total jobs scraped across all companies: {len(all_companies_jobs)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()