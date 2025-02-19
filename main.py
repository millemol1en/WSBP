from selenium.webdriver.chrome.service import Service
from Scrapers.KUWebScraper.KUWS import kuws
from Scrapers.DTUWebScraper.DTUWS import dtuws

def main():
    service = Service(executable_path="./chromedriver")
    kuws(service)
    # dtuws(service)

if __name__=="__main__":
    main() 