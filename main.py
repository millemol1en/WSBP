from selenium.webdriver.chrome.service import Service
from Scrapers.ScraperCore import scraper_core

def main():
    service = Service(executable_path="./chromedriver")
    scraper_core(service)

if __name__=="__main__":
    main() 