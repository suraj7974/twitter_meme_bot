from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

linkedin_gmail = os.getenv('LINKEDIN_EMAIL')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')

if not linkedin_gmail or not linkedin_password:
    raise ValueError("LinkedIn credentials not found in environment variables")

def setup_driver():
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        # Add arguments for running in GitHub Actions
        if 'GITHUB_ACTIONS' in os.environ:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
        
        # Additional options for better stability
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if 'GITHUB_ACTIONS' in os.environ:
            service = Service('/usr/local/bin/chromedriver')
            print("chrome initialized")
        else:
            service = Service()  # Let it auto-detect locally
            print("chrome initialized")
            
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set window size
        driver.set_window_size(1920, 1080)
        
        return driver

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

def extract_job_data(job_card):
    """Extract job details from a job card element"""
    try:
        # Initialize dictionary for job data
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
            except:
                pass

        # # Extract company name
        # try:
        #     company_elem = job_card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle")
        #     job_data['company'] = company_elem.text.strip()
        # except:
        #     try:
        #         company_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__company-name")
        #         job_data['company'] = company_elem.text.strip()
        #     except:
        #         pass

        # # Extract location
        # try:
        #     location_elem = job_card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item")
        #     job_data['location'] = location_elem.text.strip()
        # except:
        #     try:
        #         location_elem = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
        #         job_data['location'] = location_elem.text.strip()
        #     except:
        #         pass

        # Extract job link
        try:
            link_elem = job_card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
            job_data['link'] = link_elem.get_attribute('href')
        except:
            try:
                link_elem = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                job_data['link'] = link_elem.get_attribute('href')
            except:
                pass

        return job_data

    except Exception as e:
        print(f"Error extracting job data: {str(e)}")
        return None

def save_to_json(jobs_data, filename='linkedin_jobs.json'):
    """Save jobs data to a JSON file"""
    try:
        # Create the data structure with metadata
        data_to_save = {
            "metadata": {
                "total_jobs": len(jobs_data),
                "search_criteria": {
                    "keywords": "remote",
                    "work_type": "Remote"
                }
            },
            "jobs": jobs_data
        }
        
        # Save to JSON file with nice formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(jobs_data)} jobs to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")
        return False

def scroll_page(driver):
    """Scroll through the current page to load all jobs"""
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # Scroll up to 3 times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    except Exception as e:
        print(f"Error while scrolling: {str(e)}")

def get_current_page_jobs(driver):
    """Get all job listings from current page and extract their data"""
    try:
        # Find all job cards on the page
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        
        # Extract data from each job card
        jobs_data = []
        for job_card in job_cards:
            job_data = extract_job_data(job_card)
            if job_data:
                jobs_data.append(job_data)
        
        return jobs_data
    except Exception as e:
        print(f"Error getting current page jobs: {str(e)}")
        return []

def scrape_jobs_with_pagination(driver):
    try:
        current_page = 1
        has_next_page = True
        all_jobs_data = []

        while has_next_page:
            print(f"Scraping page {current_page}")

            # Wait for job listings to load
            time.sleep(3)

            # Scroll through current page
            scroll_page(driver)

            # Get jobs data from current page
            current_page_jobs = get_current_page_jobs(driver)
            all_jobs_data.extend(current_page_jobs)
            print(f"Scraped {len(current_page_jobs)} jobs from page {current_page}")

            try:
                # Wait for pagination controls
                pagination_locators = [
                    (By.CLASS_NAME, "artdeco-pagination__pages"),
                    (By.CLASS_NAME, "artdeco-pagination"),
                    (By.CSS_SELECTOR, "[data-test-pagination-page-btn]"),
                    (By.XPATH, "//ul[contains(@class, 'artdeco-pagination__pages')]"),
                    (By.XPATH, "//button[contains(@aria-label, 'Page')]/..")
                ]

                pagination = None
                for locator in pagination_locators:
                    try:
                        pagination = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(locator)
                        )
                        if pagination:
                            break
                    except:
                        continue

                if not pagination:
                    print("Could not find pagination controls")
                    break

                # Find the next page button
                next_button = None

                try:
                    next_button = driver.find_element(
                        By.XPATH,
                        f"//button[@aria-label='Page {current_page + 1}' or @data-test-pagination-page-btn='{current_page + 1}']"
                    )
                except:
                    buttons = pagination.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        try:
                            if button.get_attribute("aria-label") == f"Page {current_page + 1}":
                                next_button = button
                                break
                        except:
                            continue

                if next_button and next_button.is_enabled() and current_page < 2:
                    print(f"Moving to page {current_page + 1}")
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    time.sleep(1)

                    try:
                        next_button.click()
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", next_button)
                        except:
                            ActionChains(driver).move_to_element(next_button).click().perform()

                    current_page += 1
                    time.sleep(3)

                    current_url = driver.current_url
                    if "page=" not in current_url:
                        driver.get(f"{current_url}&page={current_page}")
                        time.sleep(3)
                else:
                    print("Reached last page or couldn't find next button")
                    has_next_page = False

            except Exception as e:
                print(f"Error navigating to next page: {str(e)}")
                print("Current URL:", driver.current_url)
                has_next_page = False

        # Save the scraped data to JSON
        if all_jobs_data:
            save_to_json(all_jobs_data)
        
        return all_jobs_data

    except Exception as e:
        print(f"Error in pagination: {str(e)}")
        driver.save_screenshot("linkedin_error.png")
        return []

def main():
    driver = None
    try:
        driver = setup_driver()

        if not login_to_linkedin(driver):
            raise Exception("Failed to login to LinkedIn")

        print("Successfully logged in to LinkedIn")

        # Navigate to jobs page
        job_search_url = "https://www.linkedin.com/jobs/search/?keywords=remote&location=&f_WT=2&position=1&pageNum=0"
        driver.get(job_search_url)

        # Wait for initial page load
        time.sleep(5)

        # Start scraping with pagination
        jobs_data = scrape_jobs_with_pagination(driver)
        print(f"Total jobs scraped: {len(jobs_data)}")

        input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()