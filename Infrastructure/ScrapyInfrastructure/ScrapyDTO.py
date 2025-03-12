import scrapy

class CourseDTO(scrapy.Item):
    literature = scrapy.Field()

class DepartmentDTO(scrapy.Item):
    department = scrapy.Field()
    dep_course_urls = scrapy.Field()