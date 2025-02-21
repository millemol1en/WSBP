from selenium import webdriver
from Scrapers.KUWebScraper.KUWS import KUSpider
from Scrapers.DTUWebScraper.DTUWS import dtuws

# []
def scraper_core(service):
    print("!===============================================================================================================================!")

    # [] 
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('--headless')                           # No GUI
    driver_options.add_argument('--disable-gpu')                        # No GUI - [for Windows]
    driver_options.add_argument('--blink-settings=imagesEnabled=false') # Blocks images

    # [] 
    driver = webdriver.Chrome(options=driver_options, service=service)

    # [] We start off by first using Chrome DevTools Protocol to block CSS and images - we won't be needing that
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*.css", "*.jpg", "*.png", "*.gif", "*.svg", "*.woff", "*.woff2"]})
    driver.execute_cdp_cmd("Network.enable", {})

    # [] 
    # kuws(driver)
    # dtuws(driver)
    # puws(driver)

    ku_spider = KUSpider("København Universitet", "https://kurser.ku.dk/")
    ku_spider.run_spider(driver)



    driver.quit()
    print("!===============================================================================================================================!")
