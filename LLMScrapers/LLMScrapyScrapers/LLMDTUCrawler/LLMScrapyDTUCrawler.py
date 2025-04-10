# Scraping API:
import scrapy

# Local Imports:
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Defs.Defs import EXCLUDE_KEY_WORDS

# Native Python Imports:
import re

class LLMDTUCrawler(LLMScrapyAbstractCrawler):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI,**kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        # [] Header with 'User-Agent' and 'Referer' was required to simulate an authenticate "human" request
        #    from reputable source (Google)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://google.com/',  
        }

        yield scrapy.Request(
            url=self.start_urls[0],
            headers=headers,
            callback=self.scrape_departments,
            dont_filter=True
        )

    """ Step 1 - """
    def scrape_departments(self, response):
        department_options = response.xpath('//select[@id="Department"]/option')

        for dep_option in department_options:
            option_text = dep_option.xpath('normalize-space(text())').get()
            option_value = dep_option.xpath('@value').get()
            # print(f"Department: {option_text}, Value: {option_value}")

            if option_text and option_value:
                # TODO: Remove the "CourseType=DTU_BSC&" - ONLY FOR TESTING
                department_url = (f"https://kurser.dtu.dk/search?Department={option_value}")

                if option_value == "38":
                    yield scrapy.Request(
                        url=department_url,
                        callback=self.scrape_department_courses,
                        meta={'department_name': option_text}
                    )

    """ Step 4 """
    def scrape_department_courses(self, response):
        department_name = response.meta['department_name']

        rows = response.xpath('//table//tr')

        if len(rows) > 1 and department_name != "88 Other courses":    
            for row in rows:
                course_link  = row.xpath('./td[2]/a')
                course_data  = course_link.xpath('normalize-space(text())').get()
                course_url   = course_link.xpath('@href').get()
                course_level = row.xpath('./td[3]/text()').get()

                if course_data and course_url and course_level:
                    full_course_url = (f"https://kurser.dtu.dk{course_url}")
                    
                    if course_data and any(keyword in course_url for keyword in ["course"]) and course_data != "Study Planner": # TODO: Clean this up!

                        course_title = str(course_data).split(" - ", 1)[1] 
                        course_code  = str(course_data).split(" - ", 1)[0]
                        course_level = 0
                        course_level = str(row.xpath('./td[3]/text()').get()).strip()

                        print(f"**== Course: {course_code} * {course_title} * {course_level}")
                        
                        yield scrapy.Request(
                            url=full_course_url,
                            callback=self.scrape_single_course,
                            meta={ 'department_name': department_name, 'course_name': course_title, 'course_code': course_code, 'course_level': course_level }
                        )

                    else: continue

    
    """ Step 5 """
    def scrape_single_course(self, response):
        # [] Retrieve the meta data:
        department_name = response.meta['department_name']
        course_name     = response.meta['course_name'] 
        course_level    = response.meta['course_level'] 
        course_code     = response.meta['course_code'] 
        points_raw = response.xpath("//label[contains(text(), 'Point( ECTS )')]/parent::td/following-sibling::td/text()").get()
        points = f"{points_raw.strip()} ECTS"

        raw_literature = response.xpath(
            "//div[@class='bar' and contains(text(), 'Course literature')]/following-sibling::text()[1]"
        ).get()

        course_literature = self.clean_literature(raw_literature)
        
        if course_name != None or course_code != None: 
            course_dto = CourseDTO(
                name       = course_name,
                code       = course_code,
                literature = course_literature,
                department = department_name,
                level      = course_level,
                points     = points,
            )

            yield course_dto

    """ LOCAL METHODS """
    # []
    #TODO: Ask Æmill if we can delete this, as we shall follow structure of KUScraper to harmonize code.
    def extract_course_code_and_name(self, course_string) -> (str | str):
        match = re.match(r'(\b[A-Z]{2,3}(\d+)|(\d+))\s*-\s*(.+)', course_string)
        if match:
            course_code = match.group(1)
            course_name = match.group(2).strip()
            return course_code, course_name
        return None, None
    
    def call_llm(self):
        return super().call_llm()