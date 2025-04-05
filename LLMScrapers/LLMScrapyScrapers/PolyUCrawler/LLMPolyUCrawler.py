# Scrapying APIs
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Additionals:
from dotenv import load_dotenv
import os

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler

class LLMPolyUCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    def scrape_departments(self, response):
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")
        clean_html  = self.strip_html_dep(parsed_html)


    
    def scrape_department_courses(self, response):
        return super().scrape_department_courses(response)
    
    def scrape_single_course(self, response):
        return super().scrape_single_course(response)
    

    """ LOCAL METHODS """
    # [LM #1] ...
    def sanitize_department_url(self, dep_url) -> str:
        parsed_url = urlparse(dep_url)

        if not parsed_url.netloc or "polyu.edu.hk" not in parsed_url.netloc:
            return urljoin("https://www.polyu.edu.hk/", dep_url.lstrip("/"))

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_url
