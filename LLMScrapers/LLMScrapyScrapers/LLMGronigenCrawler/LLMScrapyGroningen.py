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

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType
from LLMScrapers.LLMScrapyScrapers.LLMGronigenCrawler.GeminiFTDataset import gemini_dataset

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

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

    # []
    def scrape_departments_subset(self, response):
        data = json.loads(response.text)

        # TODO: Reformat this code...
        for faculty in data:
            faculty_name = faculty.get("titleEn", "Unknown")
            faculty_programs = faculty.get("programs")

            faculty_program_urls = []

            # Subset to test will be "Law":
            if faculty_name != "Law": continue
            
            for program in faculty_programs:
                program_level = program.get("levels")
                program_name = program.get("titleEn")
                program_code = program.get("code")

                if program_code and any(level in {"BACHELOR", "MASTER"} for level in program_level):
                    program_url = (f"https://ocasys.rug.nl/api/2024-2025/scheme/program/{program_code}")
                    faculty_program_urls.append(program_url)
            
                yield scrapy.Request(
                    url=program_url,
                    callback=self.scrape_department_courses,
                    meta={ 'faculty_name': faculty_name }
                )

    # [] Scrape all the departments using entirely LLM prompting techniques:
    def scrape_departments(self, response):
        print("CALLING DEPARTMENTS")
        core_message = f"""
        "You are a web scraping bot tasked at scraping the provided URL: https://ocasys.rug.nl/api/faculty/catalog/2024-2025 \n"
        "You are to scrape the JSON data located in the XHR Requests.\n"
        "Specifically, you are to scrape all the faculties and their bachelors level subjects.\n"
        "Crucially, there are 13 faculties in total, all of them at the top level, but not all them are of interest to us.\n"
        "Within each faculty there will be an array of programs. Each program contains 3 key attributes which we interested in, 'levels', 'titleEn' and 'code'. Crucially, the code is a number, like '60365-5503'\n"
        "Do not include thesis, projects or exchange.\n"
        "Please write back the information you located in provided JSON 'response_schema', wherein the top level is the faculty name, followed by all the programmes they provide.\n"
        """

        scraped_departments = self.call_llm(core_message)
        
        print(f"DEPARTMENTS: \n{scraped_departments}")

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

        match self.llm_type:
            case LLMType.CHAT_GPT:
                response = gpt_client.chat.completions.create(
                    model="gpt-4o-2024-08-06",                      
                    messages=[
                        {
                            "role": "system",
                            "content": core_message,
                        }
                    ],
                    temperature=0,
                    tool_choice="auto",
                    tool_schema={
                        "format": {
                            "type": "json_schema",
                            "name": "groningen_university_departments_and_courses",
                            "schema": rs_j
                        }
                    }                                  
                )

                content = response.choices[0].message.content.strip()
            
                return content
            
            case LLMType.GEMINI:
                training_dataset = types.TuningDataset(
                    examples=[
                        types.TuningExample(
                            text_input=i,
                            output=o
                        )
                        for i, o in gemini_dataset
                    ]
                )

                tuning_job = gemini_client.tunings.tune(
                    base_model='models/gemini-1.5-flash-001-tuning',
                    training_dataset=training_dataset,
                    config=types.CreateTuningJobConfig(
                        epoch_count=5,                                  # How many full passes over your dataset the model makes.
                        batch_size=4,                                   # How many examples are used at once to calculate a gradient update.
                        learning_rate=0.001,                            # Determines how strongly the model parameters are adjusted on each iteration
                        tuned_model_display_name="test tuned model"     #
                    )
                )

                job_id    = tuning_job.name
                job_state = tuning_job.state
                print(f"Started tuning job: {job_id}")
                print(f"Job state name: {job_state.name}")
                    
                while job_state.name != "JOB_STATE_SUCCEEDED":
                    print(f"Running! Current job state is: {job_state.name}")

                print(f"Job state name: {job_state.name}")

                try:
                    response = gemini_client.models.generate_content(
                        model=tuning_job.tuned_model.model,
                        contents=core_message,
                        config={
                            'response_mime_type': 'application/json',
                            'response_schema': rs_j, 
                        }
                    )
                except Exception as e:
                    print(f"ERROR!: {e}")

                return response.text
            
            case _: pass