from selenium.webdriver.chrome.service import Service
from RawScrapers.RawScrapyScrapers.RawScrapyScrapersExe import raw_scrapy_scraper_executor
from RawScrapers.RawSeleniumScrapers.RawSeleniumScraperExe import raw_selenium_scraper_executor
from LLMScrapers.LLMScrapyScrapers.LLMScrapyScraperExe import llm_scrapy_scraper_executor

def main():
    # service = Service(executable_path="./chromedriver")
    # scraper_core(service)
    # llm_scrapy_scraper_executor()
    raw_scrapy_scraper_executor()

if __name__=="__main__":
    main() 