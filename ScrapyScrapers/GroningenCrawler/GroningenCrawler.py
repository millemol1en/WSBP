import scrapy
import json
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

from Defs.Defs import EXCLUDE_KEY_WORDS

class GroningenCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

    """ Step 1 (Init Execution) """
    def parse(self, response):
        yield from self.scrape_departments(response)

    """ Step 2 """
    def scrape_departments(self, response):
        data = json.loads(response.text)

        for faculty in data:
            faculty_name = faculty.get("titleEn", "Unknown")
            faculty_programs = faculty.get("programs")

            faculty_program_urls = []

            # Testing purposes: Isolates "Law"
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
        
    """ Step 3 """
    def scrape_department_courses(self, response):
        faculty_name = response.meta['faculty_name']
        data = json.loads(response.text)

        blocks  = data.get("blocks", [])

        course_urls = []    # TODO: Remove! This is temporary

        for block in blocks:                        
            courseEntries = block.get("entries", [])

            for entry in courseEntries:
                course_offering = entry.get("courseOffering", {})
                course_block    = course_offering.get("course", {})
                course_code     = course_block.get("code")
                course_name     = course_block.get("titleEn")
                if any(keyword in course_name.lower() for keyword in EXCLUDE_KEY_WORDS): continue
                course_data_url = (f"https://ocasys.rug.nl/api/2024-2025/course/page/{course_code}")
                course_urls.append(course_data_url)
                
                yield scrapy.Request(
                    url=course_data_url,
                    callback=self.scrape_single_course,
                    meta={ 'faculty_name': faculty_name }
                )
    
    """ Step 4 """
    def scrape_single_course(self, response):
        faculty_name = response.meta['faculty_name']
        data = json.loads(response.text)

        course_code  = data.get("code")
        course_title = data.get("titleEn")
        course_level = data.get("levels")
        course_literature = []

        # Locate the books object:
        for offering in data.get("courseOfferings", []):
            books = offering.get("books", [])

            if len(books) == 0: continue
            for book in books:
                book_title  = book.get("title")
                book_isbn   = book.get("isbn")
                book_author = book.get("author")

                if book_title and book_isbn and book_author:
                    book_title = book_title.replace("[i]", "").replace("[/i]", "") # TODO: Replace with general cleaning function
                    course_literature.append({book_title, book_isbn, book_author})

        course_dto = CourseDTO(
            name = course_title,
            code = course_code,
            literature = course_literature,
            department = faculty_name,
            level      = course_level
        )

        yield course_dto


    def spider_closed(self, spider):
        print("Spider closed: %s", spider.name)