# Scrapying APIs
import scrapy

# LLM APIs:
from openai import OpenAI
from google import genai
from google.genai import types

# Native Python Packages:
import os
import inspect
import json
from pydantic import BaseModel

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from DataObjects.Book import Book
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO, ScrapyErrorDTO
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType
from LLMScrapers.LLMScrapyScrapers.LLMGronigenCrawler.GeminiFTDataset import gemini_dataset

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

# ResponseSchema for OpenAI
class ResponseSchema(BaseModel):
    course_name   : str
    course_code   : str
    course_level  : str
    course_points : str
    course_lit    : list[Book]

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

    # [] Scrape all the departments using entirely LLM prompting techniques:
    #    Compared to the raw scraper only 5 lines of code were removed.
    def scrape_departments(self, response):
        data = json.loads(response.text)

        # [] Both models were unsuccessful at getting the necessary information with a single prompt so for each faculty.
        #    we must call the LLM - it was either this or truncating the data and getting even worse results.
        for faculty in data:
            faculty_name = faculty.get("titleEn", "Unknown")
            if faculty_name in ['Honours College', 'Campus Fryslân', 'Teaching Centre']: continue
            faculty_programs = faculty.get("programs")

            core_message = f"""
            You are a web scraping assistant.

            You are given the following JSON data:
            {faculty_programs}

            Your task is to extract specific information according to these rules:
            - Scrape only the Bachelor's and Master's courses.
            - Determine whether a course is Bachelor's or Master's by checking the 'levels' property.
            - Inside each 'faculty', there is an array of 'programs'. Each 'program' contains a 'code' attribute (e.g., '60365-5503') that you must extract.

            Exclusion criteria:
            - Do not include any programs related to 'thesis', 'project', or 'exchange' in their titles.

            Format the output as a Python list of strings.

            Do not include any additional commentary. Only output the list.
            """

            if faculty_name != 'Law': continue  # TODO: Remove! Only for testing
            llm_response = self.call_llm(core_message)
            print(llm_response)


            for program_code in llm_response:
                try:

                    program_url = (f"https://ocasys.rug.nl/api/2024-2025/scheme/program/{program_code}")
            
                    yield scrapy.Request(
                        url=program_url,
                        callback=self.scrape_department_courses,
                        meta={ 'faculty_name': faculty_name }
                    )

                except Exception as e:
                    frame = inspect.currentframe().f_back

                    yield ScrapyErrorDTO(
                        error=str(e),
                        url=response.url,
                        file=frame.f_code.co_filename,
                        line=frame.f_code.co_filename,
                        func=frame.f_code.co_name
                    )

    # [] Performance is terrible without truncation. This need for first hand truncation essentially renders the LLM useless here. 
    #    Reduced the number lines of code down a bit more this time - specifically by 8. 
    def scrape_department_courses(self, response):
        faculty_name = response.meta['faculty_name']
        data = json.loads(response.text)

        core_message = f"""
        You are a web scraping assistant.

        You are given the following JSON data:
        {data}

        Your task is to extract specific information according to these rules:
        - From each 'courseOffering' object, extract the value of the 'code' property.
        - Exclude any course where the course title contains any of the following words: 'Project', 'Thesis', 'Internship', 'Academic', 'Bachelor', 'Research', or 'Ceremony'.

        Example input:
        [
        {
            "faculty": "Engineering",
            "programs": [
                {"title": "Bachelor of Mechanical Engineering", "levels": ["Bachelor"], "code": "60365-5503"},
                {"title": "Research Project in Mechanical Engineering", "levels": ["Bachelor"], "code": "60365-5504"}
            ]
        }
        ]

        Format the output as a Python list of strings.

        Do not include any additional commentary. Only output the list.
        """

        llm_response = self.call_llm(core_message)

        for course_code in llm_response:
            try:
                course_data_url = (f"https://ocasys.rug.nl/api/2024-2025/course/page/{course_code}")
        
                yield scrapy.Request(
                    url=course_data_url,
                    callback=self.scrape_department_courses,
                    meta={ 'faculty_name': faculty_name }
                )

            except Exception as e:
                frame = inspect.currentframe().f_back

                yield ScrapyErrorDTO(
                    error=str(e),
                    url=response.url,
                    file=frame.f_code.co_filename,
                    line=frame.f_code.co_filename,
                    func=frame.f_code.co_name
                )
    
    def scrape_single_course(self, response):
        faculty_name = response.meta['faculty_name']
        data = json.loads(response.text)

        core_message = f"""
        You are a web scraping assistant. 

        You are given the following JSON data: {data}

        Your task is to extract the following pieces of information:
        - Course title: from the key 'titleEn'
        - Course code: from the key 'code'
        - Course literature (books): from the 'books' key, extract 'author', 'title', and 'isbn'

        Additionally:
        - From each book's 'title', also extract the title, ISBN, and publishing firm if available.

        You must return the extracted information following this response schema:

        class ResponseSchema(BaseModel):
            course_name: str
            course_code: str
            course_level: str
            course_points: str
            course_books: list[Book]

        Do not include any extra commentary. Only output data in the exact structure above.
        """

        try:
            llm_response = self.call_llm(core_message)

            for course in llm_response:
                
                yield CourseDTO(
                    name       = course.course_name,
                    code       = course.course_code,
                    literature = course.course_lit,
                    department = faculty_name,
                    level      = course.course_level,
                    points     = course.course_points
                )
            
        except Exception as e:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )
    
    def call_llm(self, core_message, response_schema : ResponseSchema):   
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
                            "schema": response_schema
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

                try:
                    response = gemini_client.models.generate_content(
                        model=tuning_job.tuned_model.model,
                        contents=core_message,
                        config={
                            'response_mime_type': 'application/json',
                            'response_schema': response_schema, 
                        }
                    )
                except Exception as e:
                    print(f"ERROR!: {e}")

                return response.text
            
            case _: pass