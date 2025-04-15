# Scrapying APIs
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai
from google.genai import types


# Native Python Packages:
from urllib.parse import urlparse, urljoin
import os
import re
import time
import json
import requests

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(vertexai=True, project='neon-opus-456517-v7', location='us-central1')

class LLMGroningenCrawler(LLMScrapyAbstractCrawler):
    def __init__(self, 
                 _name="", 
                 _url="", 
                 _llm_type=LLMType.NULL_AI, 
                 **kwargs
    ):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    # [Fine-Tune Test #1] 
    # Can LLMs handle large sums of information (38k > tokens) and send back a proper response?
    def scrape_all_departments_and_programs(self, response):
        # [] Get the websites JSON data:
        json_data = json.loads(response.text)

        # [] Remove titles which aren't actual faculties:
        titles_to_remove = {"Honours College", "Teaching Centre", "Campus Fryslân", "University College"}
        filtered_data    = [faculty for faculty in json_data if faculty.get("titleEn") not in titles_to_remove]

        core_message = f"""
        You are a JSON processing assistant.

        Your task is to extract data from the JSON provided below.

        ### GOAL
        Return a list of faculties and, under each faculty, include ONLY the programs that contain 'BACHELOR' in their 'levels' array.

        ### INSTRUCTIONS
        1. Iterate over each faculty in the JSON.
        2. For each faculty, look at the 'programs' array.
        3. For each program:
            - If the 'levels' array contains the string 'BACHELOR', include this program.
            - From the program, extract only the following fields:
                - 'titleEn' (or 'titleNl' if 'titleEn' is not available)
                - 'code'
                - 'levels'
        4. If a faculty has no BACHELOR-level programs, you may omit it.
        5. Return only the final structured data in valid JSON format. Do not include any explanation, commentary, or formatting outside the JSON.

        ### JSON INPUT
        {filtered_data}
        """

        scraped_departments = self.call_llm(core_message)
        parsed_data         = json.loads(scraped_departments)

        with open("./LLMScrapers/LLMScrapyScrapers/LLMGronigenCrawler/test.json", "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            

    # [] Scrape all the departments using almost exclusively LLM prompting techniques:
    def scrape_departments(self, response):
        json_data = json.loads(response.text)

        filtered_data = [faculty for faculty in json_data if faculty.get("titleEn") == "Medical Sciences / UMCG"]

        core_message = f"""
        You are a web crawler, specialized in JSON parsing.

        ### GOAL
        Return a list of faculties and, under each faculty, include ONLY the programs that contain 'BACHELOR' in their 'levels' array.

        ### INSTRUCTIONS
        1. Read the JSON file and retrieve the code for each program.
        2. Take the code which you just retrieved and attach it to the following URL: 'https://ocasys.rug.nl/current/catalog/programme/'
        3. Visit this new URL and looking at the XHR Requests locate the 
        https://ocasys.rug.nl/api/2024-2025/course/page/
        ### JSON INPUT
        {filtered_data}
        """


    def scrape_department_courses(self, response):
        core_message = f"""
        "You are a JSON parser"
        """

        return super().scrape_department_courses(response)
    
    def scrape_single_course(self, response):
        return super().scrape_single_course(response)
    
    def call_llm(self, core_message):   
        print("CALLING LLM")
        rs_f  = open("./LLMScrapers/LLMScrapyScrapers/LLMGronigenCrawler/ResponseSchema.json", "r")
        rs_j = json.load(rs_f)

        print("Loaded schema:", rs_j)

        match self.llm_type:
            case LLMType.CHAT_GPT:
                response = gpt_client.chat.completions.create(
                    model="gpt-4-turbo",                      
                    messages=[
                        {
                            "role": "system",
                            "content": core_message
                        }
                    ],
                    temperature=0,     
                    stream=True                      
                )

                # content = response.choices[0].message.content.strip()
            
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content

                return full_response
            
            case LLMType.GEMINI:
                

                # try:
                #     response = gemini_client.models.generate_content(
                #         model=tuning_job.tuned_model.model,
                #         contents=core_message,
                #         config={
                #             'response_mime_type': 'application/json',
                #             'response_schema': rs_j, 
                #         }
                #     )
                # except Exception as e:
                #     print(f"ERROR!: {e}")

                # return response.text
                pass
            
            case _: pass