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

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO, ScrapyErrorDTO
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
            "You are a web scraping bot tasked at scraping the provided JSON data: {faculty_programs} \n"
            "Specifically, you are to scrape the bachelors and masters courses from the provided data.\n"
            "Whether or not a course is is bachelors or masters can be inferred from looking at the 'levels' property.\n"
            "Within each faculty there will be an array of programs. Each program contains a single attributes which we interested, 'code', which could for example look like so: '60365-5503'\n"
            "Do not include thesis, projects or exchange.\n"
            "Please write back the information you located in a Python list.\n"
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
        "You are a web scraping bot tasked with scraping the following JSON data: {data} \n"
        "Your are tasked with scraping the provided JSON data - specifically the 'code' property which can be found in each of the many 'courseOffering' properties.\n"
        "However, you are to exclude the programs which have the following words in their title: 'Project', 'Thesis', 'Internship', 'Academic', 'Bachelor', 'Research' and 'Ceramony'"
        "Please write back the information in a Python list.\n"
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
        "You are a web scraping bot tasked with scraping the following JSON data: {data} \n"
        "Your task is to harvest the following key pieces of information. Firstly, you need to get the course title which is stored in the key 'titleEn' and the course code which is stored in the key 'code'.\n"
        "Secondly, you need to harvest the information within "
        """

    
        try:
            llm_response = self.call_llm(core_message)

            yield CourseDTO(
                name = course_title,
                code = course_code,
                literature = course_literature,
                department = faculty_name,
                level      = course_level,
                points     = course_points
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