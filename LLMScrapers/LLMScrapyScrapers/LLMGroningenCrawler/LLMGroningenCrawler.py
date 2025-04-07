# Scrapying APIs
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Native Python Packages:
from urllib.parse import urlparse, urljoin
import os
import re
import time
import json

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler, LLMType

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
            "programmes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                        },
                        "url": {
                            "type": "string",
                        }
                    }
                }
            }
        }
    }
}

class LLMGroningenCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    # "Please return a Python string list of the information which you were able to retrieve.\n"

    def scrape_departments(self, response):
        core_message = f"""
        "You are a web scraping bot tasked at scraping the linked URL: https://ocasys.rug.nl/current/catalog.\n"
        "What you are to scrap is all of the faculty names as well as the names and URLs of the bachelors programmes they provide.\n"
        "You will find all the necessary data in the file '2024-2025' located in the XHR Requests.\n"
        "There should be a total of 13 entries, with each faculty being on the outter-most layer in the JSON file.\n"
        "Please write back the information you located in provided JSON 'response_schema', wherein the top level is the faculty name, followed by all the programmes they provide.\n"
        """

        scraped_departments = self.call_llm(core_message)
        
        print(f"DEPARTMENTS: \n{scraped_departments}")

    def scrape_department_courses(self, response):
        return super().scrape_department_courses(response)
    
    def scrape_single_course(self, response):
        return super().scrape_single_course(response)
    
    # TODO: Place this into a generalized LLM specific file:
    def call_llm(self, core_message):   
        print("Calling LLM")     
        match self.llm_type:
            case LLMType.CHAT_GPT:
                response = gpt_client.chat.completions.create(
                    model="gpt-4o-2024-08-06",                      
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                core_message
                            )
                        }
                    ],
                    temperature=0,                                  
                )

                content = response.choices[0].message.content.strip()
            
                return content
            
            case LLMType.GEMINI:
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=core_message,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': response_schema, 
                    }
                    
                )

                return response.text
            
            case _: pass