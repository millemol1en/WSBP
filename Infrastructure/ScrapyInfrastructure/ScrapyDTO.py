import scrapy

class DepartmentDTO(scrapy.Item):
    department = scrapy.Field()
    dep_course_urls = scrapy.Field()