from selenium.webdriver.chrome.service import Service
from SeleniumScrapers.ScraperCore import scraper_core
from ScrapyScrapers.ScrapyScrapersExe import scrapy_scraper_executor

def main():
    # service = Service(executable_path="./chromedriver")
    # scraper_core(service)
    scrapy_scraper_executor()

if __name__=="__main__":
    main() 