import scrapy
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import DepartmentDTO

from Defs.Defs import EXCLUDE_KEY_WORDS

class DTUCrawler(ScrapyAbstractCrawler):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://google.com/',  # Mimics arriving via search
        }

        yield scrapy.Request(
            url=self.start_urls[0],
            headers=headers,
            callback=self.scrape_departments,
            dont_filter=True
        )

    """ Step 2 - """
    def scrape_departments(self, response):
        # print(response.text)
        #departments_select = response.css('select[id="Department"]')
        departments_select = response.css('select#Department')
        departments_option = departments_select.css('option')

        for dep_option in departments_option:
            option_text = dep_option.css("::text").get().strip()
            option_value = dep_option.css("::attr(value)").get()
            # print(f"Department: {option_text}, Value: {option_value}")

            if option_text and option_value:
                department_url = (f"https://kurser.dtu.dk/search?CourseType=DTU_BSC&Department={option_value}")

                yield scrapy.Request(
                    url=department_url,
                    callback=self.scrape_department_courses,
                    meta={'department_name': option_text}
                )

    """ Step 4 """
    def scrape_department_courses(self, response):
        department_name = response.meta['department_name']

        course_urls = []

        course_links = response.css('a')

        for course in course_links:
            course_name = course.css("::text").get().strip()
            course_url = course.css("::attr(href)").get()

            if course_url:
                full_course_url = (f"https://kurser.dtu.dk{course_url}")
                
                if course_name and any(keyword in course_url for keyword in ["course"]):
                    course_urls.append(full_course_url)
                else: continue

        department_item = DepartmentDTO(
            department=department_name,
            dep_course_urls=course_urls
        )

        yield department_item
    
    """ Step 4 """
    def scrape_single_course(self, response, course_url):
        pass