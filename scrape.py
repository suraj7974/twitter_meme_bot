from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


def get_trending_topics():
    url = "https://trends24.in/india/"
    print(f"Fetching data from {url}...")

    # Set up Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run in headless mode

    # Set up the driver
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        driver.get(url)
        print("Waiting for page to load...")

        # Wait for the trend container to be present
        trend_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "trend-card__list"))
        )

        print("Parsing content...")
        trending_topics = []
        trends = trend_container.find_elements(By.TAG_NAME, "li")

        for trend in trends:
            trend_name = trend.find_element(
                By.CLASS_NAME, "trend-name").text.strip()
            tweet_count = trend.find_element(
                By.CLASS_NAME, "tweet-count").text.strip()
            trending_topics.append(f"{trend_name} ({tweet_count})")

        print(f"Found {len(trending_topics)} trending topics.")
        return trending_topics[:10]  # Return top 10 trends

    finally:
        driver.quit()


if __name__ == "__main__":
    trending = get_trending_topics()
    print("Top 10 Trending Topics:")
    for i, topic in enumerate(trending, 1):
        print(f"{i}. {topic}")
