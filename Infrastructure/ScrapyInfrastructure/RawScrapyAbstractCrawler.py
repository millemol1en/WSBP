# Scraping APIs:
import scrapy

# Loca Imports:
from DataObjects.Department import Department
from DataObjects.Book import Book
from DataObjects.Course import Course
from Infrastructure.LiteratureCleaner.LiteratureCleaner import sanitize_course_literature, extract_books, new_fixer

# LLM APIs:
from openai import OpenAI
from google import genai
from pydantic import BaseModel

# Native Python Imports:
import os 
import json
from enum import Enum
from dotenv import load_dotenv
from abc import ABC, abstractmethod

class RawScrapyAbstractCrawler(scrapy.Spider, ABC):
    departments : list[Department] = []

    def __init__(self, _name="", _url="", **kwargs):
        self.name = _name
        self.start_urls = [_url] 
        super().__init__(**kwargs)

    """ Step 1 - Init """
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