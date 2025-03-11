from abc import ABC, abstractmethod
from typing import List
from DataObjects.Department import Department

class UniSpider(ABC):
    departments : List[Department] = []

    def __init__(self, _name : str = "", _url : str = ""):
        self.name = _name
        self.url  = _url

    """ Step 1 - Execute the Spider """
    @abstractmethod
    def run_spider(self, driver):
        pass

    """ Step 2 - Gather the University Departments """
    @abstractmethod
    def scrape_departments(self, driver):
        pass

    """ Step 3 - Gather the course URLs for each Department """
    @abstractmethod
    def scrape_department_courses(self, driver):
        pass

    """ Step 4 - Gather all content from the Courses """
    @abstractmethod
    def scrape_department_course_content(self, driver):
        pass

    """ Step 5 - Gather content from a Course """
    @abstractmethod
    def scrape_single_course(self, driver, course_url):
        pass

    # TODO: Consider adding this function:
    # @abstractmethod
    # def harvest_book():
    #     pass