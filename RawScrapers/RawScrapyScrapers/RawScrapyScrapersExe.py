from scrapy.crawler import CrawlerProcess
from RawScrapers.RawScrapyScrapers.KUCrawler.KUCrawler import KUCrawler
from RawScrapers.RawScrapyScrapers.GroningenCrawler.GroningenCrawler import GroningenCrawler
from RawScrapers.RawScrapyScrapers.DTUCrawler.DTUCrawler import DTUCrawler
from RawScrapers.RawScrapyScrapers.PolyUCrawler.PolyUCrawler import PolyUCrawler
from time import time

# TODO: Add Multithreading
def raw_scrapy_scraper_executor():
    process = CrawlerProcess({
        # [] Logging:
        'LOG_LEVEL': 'INFO', # INFO, ERROR, CRITICAL, DEBUG

        # [] ...:
        'FEEDS': {
             './Testing/PolyU/polyu_raw.json': {'format': 'json', 'overwrite': True, 'encoding': 'utf-8'},
        },

        # Pipeline Configuration:
        'ITEM_PIPELINES': {
            'Infrastructure.ScrapyInfrastructure.ScrapyDataPipeline.DataPipeline': 1
        },

        # Performance Optimization
        'CONCURRENT_ITEMS': 256,
        'CONCURRENT_REQUESTS': 64,                  # Increase concurrency
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,       # Balance load per domain
        'DOWNLOAD_DELAY': 0.0,                      # At "0.0" this may cause an overloader so 0.25 would be safer
        
        # AutoThrottle (Adaptive Speed Control)
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 1,
        # 'AUTOTHROTTLE_MAX_DELAY': 5,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 10,

        # Middleware Optimizations
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
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
    # process.crawl(DTUCrawler, _name="DTU", _url="https://kurser.dtu.dk/")
    # process.start()

    """ PolyU Crawler """
    process.crawl(PolyUCrawler, _name="PolyU", _url="https://www.polyu.edu.hk/en/education/faculties-schools-departments/")
    process.start()

