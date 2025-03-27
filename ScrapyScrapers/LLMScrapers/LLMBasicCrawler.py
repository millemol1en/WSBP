# Test. 01: 
#       -> Old URL: https://web.archive.org/web/20201001192436/https://www.polyu.edu.hk/en/education/faculties-schools-departments/
#       -> New URL: https://web.archive.org/web/20241209031021/https://www.polyu.edu.hk/en/education/faculties-schools-departments/ 

import scrapy 
from langchain import LangChain
from Infrastructure.LLMInfrastructure.AbstractLLMScrapyCrawler import AbstractLLMScrapyCrawler

class LLMBasicCrawler(AbstractLLMScrapyCrawler):
    def __init__(self, _name="", _url=[], **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)
        if len(self.start_urls) != 2:
            raise ValueError("Excepted a 'new' and 'old' URL")

    def start_requests(self):
        print("CALLING REQUEST!")
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, meta={'url_type': 'old'})
        yield scrapy.Request(url=self.start_urls[1], callback=self.parse, meta={'url_type': 'new'})

    def parse(self, response):
        yield self.scrape_departments(response)

    def scrape_departments(self, response):
        print(f"Scraping departments! {response.request.url}")
        # Peform scraping of information
