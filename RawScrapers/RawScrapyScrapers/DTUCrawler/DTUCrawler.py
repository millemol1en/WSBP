import re
import scrapy
from Infrastructure.ScrapyInfrastructure.RawScrapyAbstractCrawler import RawScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

from Defs.Defs import EXCLUDE_KEY_WORDS

class DTUCrawler(RawScrapyAbstractCrawler):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

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

    """ Step 2 - """
    def scrape_departments(self, response):
        department_options = response.xpath('//select[@id="Department"]/option')

        for dep_option in department_options:
            option_text = dep_option.xpath('normalize-space(text())').get()
            option_value = dep_option.xpath('@value').get()
            # print(f"Department: {option_text}, Value: {option_value}")

            if option_text and option_value:
                # TODO: Remove the "CourseType=DTU_BSC&" - ONLY FOR TESTING
                department_url = (f"https://kurser.dtu.dk/search?Department={option_value}")

                yield scrapy.Request(
                    url=department_url,
                    callback=self.scrape_department_courses,
                    meta={'department_name': option_text}
                )

    """ Step 4 """
    def scrape_department_courses(self, response):
        department_name = response.meta['department_name']

        rows = response.xpath('//table//tr') # Get the table... 

        #print(f"   *= {department_name}")

        # [] ...
        if len(rows) > 1 and department_name != "88 Other courses":    
            # []             
            for row in rows:
                course_link                 = row.xpath('./td[2]/a')
                course_title                = course_link.xpath('normalize-space(text())').get()
                course_url                  = course_link.xpath('@href').get()
                course_level                = row.xpath('./td[3]/text()').get()
    
                if course_title and course_url and course_level:
                    full_course_url = (f"https://kurser.dtu.dk{course_url}")
                    
                    # []
                    if course_title and any(keyword in course_url for keyword in ["course"]) and course_title != "Study Planner": # TODO: Clean this up!

                        # []                        
                        # (course_code, course_name)  = self.extract_course_code_and_name(course_title)
                        
                        yield scrapy.Request(
                            url=full_course_url,
                            callback=self.scrape_single_course,
                            # TODO: Fix the "course_name" and "course_code" variables - so repair the 'extract_course_code_and_name()' function
                            meta={ 'department_name': department_name, 'course_name': course_title, 'course_code': "", 'course_level': course_level }
                        )

                    else: continue

    
    """ Step 4 """
    def scrape_single_course(self, response):
        # [] Retrieve the meta data:
        department_name = response.meta['department_name']
        course_name     = response.meta['course_name']
        course_level    = response.meta['course_level']
        course_code     = response.meta['course_code']

        # [] Retrieve the raw literature text block:
        course_literature = response.xpath(
            "//div[@class='bar' and contains(text(), 'Course literature')]/following-sibling::text()[1]"
        ).get()

        if course_name != None or course_code != None: 
            course_dto = CourseDTO(
                name       = course_name,
                code       = course_code,
                literature = [course_literature],
                department = department_name,
                level      = course_level.split(',')
            )

            yield course_dto

    """ LOCAL METHODS """
    # []
    def extract_course_code_and_name(self, course_string) -> (str | str):
        match = re.match(r'(\b[A-Z]{2,3}(\d+)|(\d+))\s*-\s*(.+)', course_string)
        if match:
            course_code = match.group(1)
            course_name = match.group(2).strip()
            return course_code, course_name
        return None, None