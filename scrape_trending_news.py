from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import time
from chromedriver_setup import setup_driver

class TechNewsScraper:
    def __init__(self):
        print("[DEBUG] Initializing the TechNewsScraper")
        self.driver = setup_driver() 
        print("[DEBUG] WebDriver setup completed")
    
    def scrape_tech_news(self):
        print("[DEBUG] Starting tech news scraping")
        news_sources = [
            {
                'url': 'https://techcrunch.com/latest',
                'title_selector': 'h3 a', 
            }
        ]

        all_news = []
        for source in news_sources:
            try:
                print(f"[DEBUG] Navigating to {source['url']}")
                self.driver.get(source['url'])
                time.sleep(2) 
                print(f"[DEBUG] Waiting for elements with selector {source['title_selector']}")
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, source['title_selector']))
                )
                print(f"[DEBUG] Elements located on {source['url']}")

                # Locate articles using the updated selector
                articles = self.driver.find_elements(By.CSS_SELECTOR, source['title_selector'])
                print(f"[DEBUG] Found {len(articles)} articles on {source['url']}")

                for article in articles[:10]:
                    title = article.text.strip()
                    link = article.get_attribute('href')
                    if title and link:
                        print(f"[DEBUG] Article found - Title: {title}, Link: {link}")
                        all_news.append({
                            'title': title,
                            'link': link
                        })
            except Exception as e:
                print(f"[ERROR] Error scraping {source['url']}: {e}")

        print(f"[DEBUG] Finished scraping, total articles collected: {len(all_news)}")
        self._save_to_json(all_news)
        return all_news

    def _save_to_json(self, news_data):
        print(f"[DEBUG] Saving scraped data to JSON file")
        output_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_articles': len(news_data)
            },
            'articles': news_data
        }
        with open('trending_tech_news.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print("[DEBUG] Data saved successfully to trending_tech_news.json")

    def close(self):
        if self.driver:
            print("[DEBUG] Closing WebDriver")
            self.driver.quit()

def main():
    print("[DEBUG] Starting the main function")
    scraper = TechNewsScraper()
    try:
        tech_news = scraper.scrape_tech_news()
        print(f"[DEBUG] Scraped {len(tech_news)} tech news articles")
    finally:
        scraper.close()
        print("[DEBUG] WebDriver closed, program terminated")

if __name__ == "__main__":
    main()
