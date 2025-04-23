# Scraping APIs:
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Native Python Imports:
from dotenv import load_dotenv
import os
import time

# Local Imports:
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMType

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)


class LLMCrawling(scrapy.Spider):
    def __init__(self, _name="", _llm_type=LLMType.NULL_AI, **kwargs):
        self.name=_name
        self.llm_type=_llm_type
        super().__init__(**kwargs)

    def start_requests(self):
        # Departments:
        dep_urls = [
            "https://www.polyu.edu.hk/bre/", 
            
        ]

        # Applied Physics (AP) URLs:
        
        for dep_url in dep_urls:
            time.sleep(1.5)
            yield scrapy.Request(
                url=dep_url,
                callback=self.retrieve_courses,
            )

    # []
    def retrieve_courses(self, response):
        # [] HTML Parsing:
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")
        clean_html  = self.strip_html_sl(parsed_html)

        core_message = f"""
        "You are a helpful assistant skilled in HTML parsing.\n"
        "You will be given raw HTML from a university department page.\n"
        "Your task is to locate a hyperlink pointing to the department's subject list or syllabus.\n"
        "The link text might include terms like 'All Subjects', 'Subject List', 'Subject Syllabus', 'Subject Syllabi', etc.\n"
        "Additionally, the target link may be further embedded inside an <li> tag also be further embedded inside an additional tag like an <li>. If so, choose the'Bachelor Programme'.\n"
        "Finally, if unable to locate any subject list it would always be better to return a link re-directing to 'Programmes'.\n"
        "Return only the URL (href) to the best match and nothing else.\n"
        "HTML:\n{clean_html}"
        """



        self.call_llm()



    def call_llm(self, core_message):        
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
                    temperature=0,                                  # Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. 
                )

                content = response.choices[0].message.content.strip()
            
                return content
            
            case LLMType.GEMINI:
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=core_message,
                    config={
                        'response_mime_type': 'application/json',
                    }
                )

                return response.text
            
            case _: pass