from scrapy.crawler import CrawlerProcess
from ScrapyScrapers.KUCrawler.KUCrawler import KUCrawler
from ScrapyScrapers.GroningenCrawler.GroningenCrawler import GroningenCrawler
from ScrapyScrapers.DTUCrawler.DTUCrawler import DTUCrawler
from ScrapyScrapers.PolyUCrawler.PolyUCrawler import PolyUCrawler
from time import time

# TODO: Add Multithreading
def scrapy_scraper_executor():
    process = CrawlerProcess({
        # 
        'LOG_LEVEL': 'ERROR', # INFO, ERROR, CRITICAL
        # 'FEEDS': {
        #     'university.json': {'format': 'json', 'overwrite': True}
        # },

        # Pipeline Configuration:
        'ITEM_PIPELINES': {
            'Infrastructure.ScrapyInfrastructure.ScrapyDataPipeline.DataPipeline': 1
        },

        # Performance Optimization
        'CONCURRENT_REQUESTS': 64,                  # Increase concurrency
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,       # Balance load per domain
        'DOWNLOAD_DELAY': 0.25,                     # Prevent overload (0.25 sec delay)
        
        # AutoThrottle (Adaptive Speed Control)
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 10,

        # Middleware Optimizations
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 300,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
        },

        # Cache (Optional for even faster scraping if data is static)
        # 'HTTPCACHE_ENABLED': True,
        # 'HTTPCACHE_EXPIRATION_SECS': 86400,  # Cache for 1 day
        # 'HTTPCACHE_DIR': 'httpcache',
    })

    """ KU Crawler """
    # process.crawl(KUCrawler, _name="København Universitet", _url="https://kurser.ku.dk/")
    # process.start()

    """ Groningen Crawler """
    # process.crawl(GroningenCrawler, _name="Groningen University", _url="https://ocasys.rug.nl/api/faculty/catalog/2024-2025")
    # process.start()

    """ DTU Crawler """
    process.crawl(DTUCrawler, _name="DTU", _url="https://kurser.dtu.dk/")
    process.start()

    """ PolyU Crawler """
    # process.crawl(PolyUCrawler, _name="PolyU", _url="https://www.polyu.edu.hk/en/education/faculties-schools-departments/")
    # process.start()


"""
    For spiders, the scraping cycle goes through something like this:
        1. You give the spider a set of "start_urls" and specify a specific "call_back" function
        2. The 
        3. 

"""