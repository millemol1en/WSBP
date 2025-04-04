from abc import ABC, abstractmethod
from Infrastructure.lit_cleaner import sanitize_course_literature, extract_books, new_fixer
import scrapy
from DataObjects.Department import Department
from DataObjects.Book import Book
import os 
from enum import Enum
from openai import OpenAI
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

gpt_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

gpt_client = OpenAI(api_key=gpt_key)
gemini_client = genai.Client(api_key=gemini_key)

class BooksResponse(BaseModel):
    books: list[Book]

class LLMType(Enum):
    CHAT_GPT = "chatgpt"
    GEMINI   = "gemini"
    DEEPSEEKER = "deepseeker"
    NULL_AI = "null_ai"

class ScrapyAbstractCrawler(scrapy.Spider, ABC):
    departments : list[Department] = []

    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        self.name = _name
        self.start_urls = [_url] 
        self.api_type = _llm_type
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

    def clean_literature(self, raw_literature):
        match self.api_type:
            case LLMType.CHAT_GPT:
                print("Chat GPT API")
                messages = [
                    {
                        "role": "system",
                        "content": "You are a literature fetcher bot. You get a string, and are supposed to return all relevant books (NOT articles, etc.). "
                        "You must follow these rules:"
                        "1) always ensure the only separator between names are commas."
                        "2) always return an array of json objects (one object per book)"
                        "2a) each object must consist of 'title', 'year', 'author', 'edition', 'isbn', 'pubFirm' (NOTE: pubFirm is publishing firm.)"
                        "2b) if a field is not present, it should be an empty string"
                        "3) NOTE: There should be no duplicates, so if a book is mentioned multiple times, it should only be returned once."   
                    },
                    {
                        "role": "user",
                        "content": f"Text: {raw_literature}"
                    }
                ]
                # Call the API
                #client.chat.completions.create
                response = gpt_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=BooksResponse,
                max_tokens=1000,
                temperature=0)
                # Extract and return the keywords
                data_dict = response.choices[0].message.parsed.model_dump() #.content.strip()
                books_list = data_dict['books']
                return books_list
            

                #yield
            case LLMType.GEMINI:
                client = genai.Client(api_key="AIzaSyBkv-Iqab_WvzDrCCSIiloL5J140_BqFq8")
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"""
                    You are a literature fetcher bot. You get a string, and are supposed to return all relevant books (NOT articles, etc.).
                    You must follow these rules:
                    1) always ensure the only separator between names are commas.
                    2) always return an array of json objects (one object per book)
                    2a) each object must consist of 'title', 'year', 'author', 'edition', 'isbn', 'pubPirm' (NOTE: pubFirm is publishing firm.)
                    "2b) if a field is not present, it should be an empty string
                    3) NOTE: There should be no duplicates, so if a book is mentioned multiple times, it should only be returned once.
                    Text: {raw_literature}""",
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': list[Book], 
                    }
                )
                return response.text
                #yield
            case LLMType.DEEPSEEKER:
                pass
            case LLMType.NULL_AI:
                pass