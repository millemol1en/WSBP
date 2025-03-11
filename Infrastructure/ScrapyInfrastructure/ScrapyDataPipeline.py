from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import DepartmentDTO

class DataPipeline:
    def __init__(self):
        self.departments = []

    def process_item(self, item, spider):
        if isinstance(item, DepartmentDTO):  # Check if the item is an instance of DepartmentItem
            self.departments.append(item)
        return item
    
    def close_spider(self, spider):
        print(f"Scraped {len(self.departments)} courses")
        for department in self.departments:
            print(f"Department: {department['department']}")
            print(f"Courses: {department['dep_course_urls']}")