import scrapy
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

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

        course_urls = [] # TODO: Remove!

        rows = response.xpath('//table//tr') # Get the table... 

        print(f"     *= {department_name} - {len(rows)}")

        if len(rows) == 0: return                # Skip the departments with only 1 course as it will always be "Study Planner"
        for row in rows:
            course_link  = row.xpath('./td[2]/a')
            course_name  = course_link.xpath('normalize-space(text())').get()
            course_url   = course_link.xpath('@href').get()
            course_level = row.xpath('./td[3]/text()').get()
 
            if course_name and course_url and course_level:
                full_course_url = (f"https://kurser.dtu.dk{course_url}")
                
                if course_name and any(keyword in course_url for keyword in ["course"]) and course_name != "Study Planner": # TODO: Clean this up!
                    course_urls.append(full_course_url) # TODO: Remove!

                    print(f"        -> {course_name} - {course_level.strip()}")

                    yield scrapy.Request(
                        url=full_course_url,
                        callback=self.scrape_single_course,
                        meta={ 'department_name': department_name }
                    )

                else: continue

    
    """ Step 4 """
    def scrape_single_course(self, response):
        pass
