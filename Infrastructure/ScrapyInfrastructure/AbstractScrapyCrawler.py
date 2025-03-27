from abc import ABC, abstractmethod
import scrapy
from DataObjects.Department import Department

class ScrapyAbstractCrawler(scrapy.Spider, ABC):
    departments : list[Department] = []

    def __init__(self, _name="", _url="", **kwargs):
        self.name = _name
        self.start_urls = [_url]
        super().__init__(**kwargs)

    """ Step 1 - Required Method in for Scrapy to execute """
    @abstractmethod
    def parse(self, response):
        pass

    """ Step 2 - """
    @abstractmethod
    def scrape_departments(self, response):
       pass
    
    """ Step 3 """
    @abstractmethod
    def scrape_department_courses(self, response):
        pass
    
    """ Step 4 """
    @abstractmethod
    def scrape_single_course(self, response):
        pass
