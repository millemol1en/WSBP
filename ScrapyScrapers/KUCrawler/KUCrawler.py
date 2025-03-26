import scrapy
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

class KUCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

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
        course_name = ' '.join(response.xpath('//h1/text()').get().strip().split()[1:])

        #Fetch coursre meta data.
        dl_element = response.xpath('//dl[@class="dl-horizontal"]')
        dt_elements = dl_element.xpath('./dt/text()').getall()
        dd_elements = dl_element.xpath('./dd/text()').getall()

        for dt, dd in zip(dt_elements, dd_elements):
            if dt == "Credit" or "Point":
                course_points = dd.split()[0]
                break
        

        
        print(f"--> Course Code: {course_code}")
        print(f"--> Course name: {course_name}")
        print(f"--> Points: {course_points}")