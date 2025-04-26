# API Imports:
from scrapy.crawler import CrawlerProcess

# CC Imports:
from radon.complexity import cc_visit
from radon.raw import analyze

# Native Python Packages:
from pathlib import Path
import traceback
import sys

# Local Imports:
from LLMScrapers.LLMScrapyScrapers.LLMKUCrawler.LLMScrapyKUCrawler import LLMKUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMGronigenCrawler.LLMScrapyGroningen import LLMGroningenCrawler
from LLMScrapers.LLMScrapyScrapers.LLMDTUCrawler.LLMScrapyDTUCrawler import LLMDTUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMPolyUCrawler.LLMScrapyPolyUCrawler import LLMPolyUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMSelfRepairing.LLMSelfRepairingScraper import LLMSelfRepairingScraper
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMType
from Infrastructure.LLMFineTuning.LLMFineTuning import LLMFineTuning 
from Testing.WSCyclicalComplexity import WSCyclicalComplexity

def llm_scrapy_scraper_executor():
    process = CrawlerProcess({
        # [] Logging:
        'LOG_LEVEL': 'INFO', # INFO, ERROR, CRITICAL, DEBUG

        # [] ...:
        # 'FEEDS': {
        #       'polyu_gemini.json': {'format': 'json', 'overwrite': True, 'encoding': 'utf-8'},
        # },

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
    # process.crawl(LLMKUCrawler, _name="København Universitet", _url="https://kurser.ku.dk/", _llm_type=LLMType.CHAT_GPT)
    # process.start()

    """ Data Accuracy - DTU """
    # process.crawl(LLMDTUCrawler, _name="Danmarks Tekniske Universitet", _url="https://kurser.dtu.dk/", _llm_type=LLMType.GEMINI)
    # process.start()

    """ Crawling Accuracy - Groningen """
    # process.crawl(LLMGroningenCrawler, _name="University of Groningen", _url="https://ocasys.rug.nl/current/catalog", _llm_type=LLMType.GEMINI)
    # process.start()

    """ PolyU """
    # process.crawl(LLMPolyUCrawler, _name="PolyU", _url="https://www.polyu.edu.hk/en/education/faculties-schools-departments/", _llm_type=LLMType.CHAT_GPT)
    # process.start()
    
    rt = RunTests(['LLMScrapers/LLMScrapyScrapers', 'RawScrapers/RawScrapyScrapers'])
    rt.exec()

    # print("="*50)
    # print("Analyzing RawScrapers/RawScrapyScrapers/KUCrawler/KUCrawler.py...\n" + "-"*50)

    # with open("RawScrapers/RawScrapyScrapers/KUCrawler/KUCrawler.py", 'r', encoding='utf-8') as f:
    #     code = f.read()

    # analyzer = WSCyclicalComplexity()

    # try:
    #     (func_wscc, aggregate_wscc) = analyzer.calc_wscc(code)

    #     for (func, data) in func_wscc.items():
    #         print(f"Function: {func}")
    #         print(f"  =* Keywords: {data['keywords']}")
    #         print(f"  =* Depth: {data['depth']}")
    #         print(f"  =* Func calls: {data['function_calls']}")
    #         print(f"  =* Grade: {data['grade']}")
    #         print(f"  =* Selector Complexity: {data['selector_complexity']}")
        
    #     print(f"Aggregate WSCC for RawScrapers/RawScrapyScrapers/KUCrawler/KUCrawler.py: {aggregate_wscc}")

    # except Exception as e:
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #     tb = traceback.extract_tb(exc_traceback)
    #     print("Exception occurred:")
    #     for entry in tb:
    #         print(f"  File: {entry.filename}, Line: {entry.lineno}, in {entry.name}")
    #         print(f"    Code: {entry.line}")

    # print("="*50)

    

class RunTests():
    def __init__(self, _paths : list[str]):
        self.paths = _paths

    def exec(self):
        for path in self.paths:
            base_dir = Path(path)

            py_files = list(base_dir.rglob('*.py'))

            analyzer = WSCyclicalComplexity()

            for py_file in py_files:
                print("="*50)
                print(f"\nAnalyzing {py_file}...\n" + "-"*50)

                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                try:
                    (func_wscc, aggregate_wscc) = analyzer.calc_wscc(code)

                    for (func, data) in func_wscc.items():
                        print(f"Function: {func}")
                        print(f"  =* Keywords: {data['keywords']}")
                        print(f"  =* Depth: {data['depth']}")
                        print(f"  =* Func calls: {data['function_calls']}")
                        print(f"  =* Grade: {data['grade']}")
                        print(f"  =* Selector Complexity: {data['selector_complexity']}")
                    
                    print(f"Aggregate WSCC for {py_file.name}: {aggregate_wscc}")

                except Exception as e:
                    print(f"Failed to analyze {py_file.name}: {e}")

                print("="*50)