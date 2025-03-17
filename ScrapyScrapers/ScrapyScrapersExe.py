from scrapy.crawler import CrawlerProcess
from ScrapyScrapers.KUCrawler.KUCrawler import KUCrawler
from ScrapyScrapers.GroningenCrawler.GroningenCrawler import GroningenCrawler
from ScrapyScrapers.DTUCrawler.DTUCrawler import DTUCrawler
from ScrapyScrapers.PolyUCrawler.PolyUCrawler import PolyUCrawler
from time import time

# TODO: Add Multithreading
def scrapy_scraper_executor():
    process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR', # INFO, ERROR, CRITICAL
        # 'FEEDS': {
        #     'university.json': {'format': 'json', 'overwrite': True}
        # },
        # 'ITEM_PIPELINES': {
        #     'Infrastructure.ScrapyInfrastructure.ScrapyDataPipeline.DataPipeline': 1
        # }
    })

    """ KU Crawler """
    # process.crawl(KUCrawler, _name="København Universitet", _url="https://kurser.ku.dk/")
    # process.start()

    """ Groningen Crawler """
    # process.crawl(GroningenCrawler, _name="Groningen University", _url="https://ocasys.rug.nl/api/faculty/catalog/2024-2025")
    # process.start()

    """ DTU Crawler """
    # process.crawl(DTUCrawler, _name="DTU", _url="https://kurser.dtu.dk/")
    # process.start()

    """ PolyU Crawler """
    process.crawl(PolyUCrawler, _name="PolyU", _url="https://www.polyu.edu.hk/en/education/faculties-schools-departments/")
    process.start()


"""
    For spiders, the scraping cycle goes through something like this:
        1. You give the spider a set of "start_urls" and specify a specific "call_back" function
        2. The 
        3. 

"""