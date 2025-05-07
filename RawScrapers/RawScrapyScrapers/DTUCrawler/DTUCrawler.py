# Scraper APIs:
import scrapy

# Local Imports:
from Infrastructure.ScrapyInfrastructure.RawScrapyAbstractCrawler import RawScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO, ScrapyErrorDTO
from Infrastructure.LiteratureCleaner.KU_DTU_LiteratureCleaner import extract_literature
from Defs.Defs import NON_BOOK_MARKERS, CLEANING_PATTERNS

# Native Python Imports:
import re
import inspect

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
        try:
            department_options = response.xpath('//select[@id="Department"]/option')

            for dep_option in department_options:
                option_text = dep_option.xpath('normalize-space(text())').get()
                option_value = dep_option.xpath('@value').get()
                # print(f"Department: {option_text}, Value: {option_value}")

                # [] Testing for Data Accuracy Baseline:
                if option_value != "38": continue

                if option_text and option_value:
                    department_url = (f"https://kurser.dtu.dk/search?Volume=2024%2F2025&Department={option_value}")
                    #department_url = (f"https://kurser.dtu.dk/search?Department={option_value}")

                    yield scrapy.Request(
                        url=department_url,
                        callback=self.scrape_department_courses,
                        meta={'department_name': option_text}
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

    """ Step 4 """
    def scrape_department_courses(self, response):
        department_name = response.meta['department_name']

        rows = response.xpath('//table//tr') # Get the table... 

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

        course_literature = []
        # [] Retrieve the raw literature text block:
        course_lit_elements = response.xpath(
            #"//div[@class='bar' and contains(text(), 'Course literature')]/following-sibling::text()"
            """
                //div[@class='bar' and contains(text(), 'Course literature')]
                /following-sibling::node()
                [not(self::div[@class='bar' and (contains(text(), 'Remarks') or contains(text(), 'Last updated'))])
                and
                not(preceding-sibling::div[@class='bar' and (contains(text(), 'Remarks') or contains(text(), 'Last updated'))])
                ]
            """
        )
        buffer = ""

        valid_course_literature = []
        for el in course_lit_elements:
            raw_texts = el.getall() 
            
            for raw_text in raw_texts:
                raw_strs = raw_text.split("<br>")

                for raw_str in raw_strs:
                    refined_str = raw_str.strip()

                    if refined_str:
                        # for marker in NON_BOOK_MARKERS:
                        #     if marker.lower() in refined_str.lower():
                        #         print(f"SKIPPED DUE TO MARKER: {marker} in line: {refined_str}")
                        #         continue
                        if any(marker.lower() in refined_str.lower() for marker in NON_BOOK_MARKERS):
                            continue

                        for pattern in CLEANING_PATTERNS:
                            refined_str = re.sub(pattern, '', refined_str).strip()

                        course_literature = extract_literature(refined_str)

                        if course_literature and "literature" in course_literature:
                            valid_literature = []
                            for lit in course_literature["literature"]:
                                # Check if both author and title are longer than 4 characters
                                if len(lit.get("author", "")) > 4 and len(lit.get("title", "")) > 4:
                                    valid_literature.append(lit)
                            
                            # Update course_literature with only valid entries
                            valid_course_literature = valid_literature
            
        if course_name != None or course_code != None: 
            yield CourseDTO(
                name       = course_name,
                code       = course_code,
                literature = valid_course_literature,
                department = department_name,
                level      = (f"{course_level.split(',')} ECTS")
            )

    """ LOCAL METHODS """
    # []
    def extract_course_code_and_name(self, course_string) -> (str | str):
        match = re.match(r'(\b[A-Z]{2,3}(\d+)|(\d+))\s*-\s*(.+)', course_string)
        if match:
            course_code = match.group(1)
            course_name = match.group(2).strip()
            return course_code, course_name
        return None, None