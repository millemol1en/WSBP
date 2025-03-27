from abc import ABC, abstractmethod
import scrapy
from DataObjects.Department import Department

"""
    The following class is 

"""

class AbstractLLMScrapyCrawler(scrapy.Spider, ABC):
    poly_departments : list[str] = []

    def __init__(self, _name="", _url=[], **kwargs):
        self.name = _name
        self.start_urls = _url
        super().__init__(**kwargs)

    @abstractmethod
    def scrape_departments(self, response):
        pass