import scrapy

class CourseDTO(scrapy.Item):
    name        = scrapy.Field()
    code        = scrapy.Field()
    literature  = scrapy.Field()
    department  = scrapy.Field()
    level       = scrapy.Field()
    points      = scrapy.Field()

class ScrapyErrorDTO(scrapy.Item):
    error   = scrapy.Field()
    url     = scrapy.Field()
    file    = scrapy.Field()
    line    = scrapy.Field()
    func    = scrapy.Field()