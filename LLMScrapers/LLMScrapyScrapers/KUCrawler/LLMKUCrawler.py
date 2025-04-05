import scrapy
import os
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler, LLMType
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO


class LLMKUCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    """ Step 2 - """
    # TODO: Replace ".css" with XPath
    def scrape_departments(self, response):
        departments_select = response.css('select#departments')
        departments_option = departments_select.css('option')

        for dep_option in departments_option:
            option_text = dep_option.css("::text").get().strip()
            option_value = dep_option.css("::attr(value)").get()
            # print(f"Department: {option_text}, Value: {option_value}")

            if option_text and option_value:
                department_url = (f"https://kurser.ku.dk/search?programme=BA&departments={option_value}") # TODO: Consider Masters Courses???
                
                
                if option_value == "DEPARTMENT_0013":
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
                full_course_url = (f"https://kurser.ku.dk/{course_url}")
                course_urls.append(full_course_url)

                yield scrapy.Request(
                    url=full_course_url,
                    callback=self.scrape_single_course,
                    meta={ 'department_name': department_name }
                )
    
    """ Step 4 """
    def scrape_single_course(self, response):
        course_code = response.xpath('//h1/text()').get().strip().split()[0]
        course_title = ' '.join(response.xpath('//h1/text()').get().strip().split()[1:])
        #course_department = response.xpath('(//h5[@class="panel-title"])[3]/following-sibling::ul[@class="list-unstyled"][1]/li/text()').get()
        course_department = response.meta['department_name']
        course_points = "NA"
        course_level = "NA"
        #Fetch coursre meta data.
        dl_element = response.xpath('//dl[@class="dl-horizontal"]')
    

        dt_elements = dl_element.xpath('./dt')
        dd_elements = dl_element.xpath('./dd')

        for dt, dd in zip(dt_elements, dd_elements):
            dt_text = dt.xpath('normalize-space(.)').get() 
            dd_text = dd.xpath('.//text()').getall()
            
            if dt_text.strip() in ["Credit", "Point"]:
                course_points = dd_text[0]
            elif dt_text.strip() in ["Level", "Niveau"]:
                course_level = dd_text[0]
        
        raw_literature = ' '.join(response.xpath('normalize-space(//div[@id="course-materials"])').getall())
        
        #sanitized_lines = sanitize_course_literature(raw_literature)
        
        course_literature = self.clean_literature(raw_literature)
        
        courseDTO = CourseDTO(
            name = course_title,
            code = course_code,
            literature = course_literature,
            department = course_department,
            level      = course_level,
            points     = course_points
        )

        yield courseDTO
