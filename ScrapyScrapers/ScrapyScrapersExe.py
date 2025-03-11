from scrapy.crawler import CrawlerProcess
from ScrapyScrapers.KUSpider.KUSpider import KUSpider

def scrapy_scraper_executor():
    process = CrawlerProcess({
        'LOG_LEVEL': 'ERROR', # INFO, ERROR, CRITICAL
        # 'FEEDS': {
        #     'departments.json': {'format': 'json', 'overwrite': True}
        # },
        'ITEM_PIPELINES': {
            'Infrastructure.ScrapyDataPipeline.DataPipeline': 1
        }
    })

    process.crawl(KUSpider, _name="København Universitet", _url="https://kurser.ku.dk/")
    process.start()