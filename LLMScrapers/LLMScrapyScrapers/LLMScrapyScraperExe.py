# API Imports:
from scrapy.crawler import CrawlerProcess

# Local Imports:
from LLMScrapers.LLMScrapyScrapers.LLMKUCrawler.LLMScrapyKUCrawler import LLMKUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMGronigenCrawler.LLMScrapyGroningen import LLMGroningenCrawler
from LLMScrapers.LLMScrapyScrapers.LLMDTUCrawler.LLMScrapyDTUCrawler import LLMDTUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMPolyUCrawler.LLMScrapyPolyUCrawler import LLMPolyUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMSelfRepairing.LLMSelfRepairingScraper import LLMSelfRepairingScraper
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMType

def llm_scrapy_scraper_executor():
    process = CrawlerProcess({
        # [] Logging:
        'LOG_LEVEL': 'INFO', # INFO, ERROR, CRITICAL, DEBUG

        #[] ...:
        'FEEDS': {
            'polyu_gpt_zeroshot.json': {'format': 'json', 'overwrite': True, 'encoding': 'utf-8'},
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

    """ Self Repairing """
    # process.crawl(LLMSelfRepairingScraper)
    # process.start()

    """ Data Accuracy - KU """
    #process.crawl(LLMKUCrawler, _name="København Universitet", _url="https://kurser.ku.dk/", _llm_type=LLMType.GEMINI)
    #process.start()

    """ Data Accuracy - DTU """
    #process.crawl(LLMDTUCrawler, _name="Danmarks Tekniske Universitet", _url="https://kurser.dtu.dk/", _llm_type=LLMType.GEMINI)
    #process.start()

    """ Crawling Accuracy - Groningen """
    # process.crawl(LLMGroningenCrawler, _name="University of Groningen", _url="https://ocasys.rug.nl/current/catalog", _llm_type=LLMType.GEMINI)
    # process.start()

    """ PolyU """
    process.crawl(LLMPolyUCrawler, _name="PolyU", _url="https://www.polyu.edu.hk/en/education/faculties-schools-departments/", _llm_type=LLMType.CHAT_GPT)
    process.start()