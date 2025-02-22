from abc import ABC, abstractmethod
from typing import List
from DataObjects.Department import Department

class UniSpider(ABC):
    # [] 
    departments : List[Department] = []

    # [] 
    def __init__(self, _name : str = "", _url : str = ""):
        self.name = _name
        self.url  = _url

    # []
    @abstractmethod
    def run_spider(self, driver):
        """This method will initialize the Uni-Spider for the """
        pass

    # [] 
    @abstractmethod
    def get_departments(self, driver):
        pass

    # [] 
    @abstractmethod
    def get_department_courses(self, driver, uni_departments):
        """This method should be implemented by subclasses to scrape department data"""
        pass

    # [] Function to scrap a single course:
    def scrape_single_course(self, driver):
        pass