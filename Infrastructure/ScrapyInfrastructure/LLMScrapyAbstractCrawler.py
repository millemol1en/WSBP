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

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
gpt_client = OpenAI(api_key=gpt_key)
gemini_client = genai.Client(api_key=gemini_key)

#TODO: Delete? 
class BooksResponse(BaseModel):
    books: list[Book]

class LLMType(Enum):
    CHAT_GPT = "chatgpt"
    GEMINI   = "gemini"
    DEEPSEEKER = "deepseeker"
    NULL_AI = "null_ai"

class LLMScrapyAbstractCrawler(scrapy.Spider, ABC):
    departments : list[Department] = []

    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        self.name = _name
        self.start_urls = [_url] 
        self.llm_type = _llm_type
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

    @abstractmethod
    def call_llm(self):
        pass

    def clean_literature(self, raw_literature):
        match self.llm_type:
            case LLMType.CHAT_GPT:
                print("Chat GPT API")

                """"""
                gpt_prompt_orig = """You are a literature fetcher bot. You get a string, and are supposed to return all relevant books (NOT articles, etc.). 
                        You must follow these rules:
                        1) always ensure the only separator between names are commas.
                        2) always return a json object representing a course, where literature is an array of books.
                        2a) each book object must consist of 'title', 'year', 'author', 'edition', 'isbn', 'pubFirm' (NOTE: pubFirm is publishing firm.)
                        2b) if a field is not present, it should be an empty string
                        3) NOTE: There should be no duplicates, so if a book is mentioned multiple times, it should only be returned once.   
                        3a) NOTE: If there is more than one edition of the same book, choose the newest edition and don't add the older one.
                        3b) NOTE: if there are no books or 'NA', return nothing, '', not even an empty array. 
                        3c) NOTE: 'literature': [] holds a single array and a single array ONLY.
                        Example: Below is an example of the structure you must follow:
                        { "name": "38102 - Technology Entrepreneurship", "code": "", "literature": [ { "title": "Crossing the Chasm", "year": 2014, "author": "G. Moore", "edition": 0, "isbn": 0, "pubFirm": "" }], "department": "38 DTU Entrepreneurship", "level": 0, "points": "NA" }"""
                
                gpt_prompt = f"Fetch books from text {raw_literature}"
                messages = [
                    {
                        "role": "system",
                        "content": gpt_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Text: {raw_literature}"
                    }
                ]

                response = gpt_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",    # NEW FT Model: ft:gpt-4o-2024-08-06:personal::BONn8Qbr # OR gpt-4o-2024-08-06
                messages=messages,
                response_format=BooksResponse,
                max_tokens=1000,
                temperature=0)
                # Extract and return the keywords
                data_dict = response.choices[0].message.parsed.model_dump() #.content.strip()
                books_list : dict = data_dict['books']
                return books_list
            
            case LLMType.GEMINI:
                print("Gemini API")
                gemini_prompt_orig =f"""
                    You are a literature fetcher bot. You get a string, and are supposed to return all relevant books (NOT articles, etc.).
                    You must follow these rules:
                    1) always ensure the only separator between names are commas.
                    2) always return an array of json objects (one object per book)
                    2a) each object must consist of 'title', 'year', 'author', 'edition', 'isbn', 'pubPirm' (NOTE: pubFirm is publishing firm.)
                    "2b) if a field is not present, it should be an empty string
                    3) NOTE: There should be no duplicates, so if a book is mentioned multiple times, it should only be returned once.
                    Text: {raw_literature}""",
                
                gemini_prompt = f"Fetch books from text{raw_literature}"
                
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents= gemini_prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': list[Book], 
                    }
                )
                return json.loads(response.text)

            case LLMType.DEEPSEEKER:
                pass
            case LLMType.NULL_AI:
                pass