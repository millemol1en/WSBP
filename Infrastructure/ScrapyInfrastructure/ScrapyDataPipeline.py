import time

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from DataObjects.Department import Department, Course
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

class DataPipeline:
    # [0] Initalize our static Department dictionary:
    def __init__(self):
        self.departments : dict[str, Department] = {}
        self.delta_time  : float                 = time.time()

    # [1] Once an item has been located it will be automatically processed by the following function:
    def process_item(self, item, spider):
        if isinstance(item, CourseDTO):  
            department_name = item['department']

            # [1.1] If department isn't already there, make a new one:
            if department_name not in self.departments:
                self.departments[department_name] = Department(
                    _depName=department_name,
                    _depCourses=[],
                    _depCourseURLs=[]
                )

            # [1.2] Extract course details:
            new_course = Course(
                _name       = item['name'],
                _code       = item['code'],
                _semester   = "",
                _points     = "",
                _literature = item.get('literature', []),
                _level      = item.get('level', [])
            )

            # [1.3] 
            department = self.departments[department_name]

            if not any(course.code == new_course.code for course in department.courses):
                department.courses.append(new_course)

        return item
    
    # [] 
    def close_spider(self, spider):
        print(f"Finished executing for {spider.name} - {len(self.departments)}")

        for _, department in self.departments.items():
            print(f"  *= Department: {department.name}")
            for course in department.courses:
                print(f"      -> {course.name}")

        self.delta_time = time.time() - self.delta_time
        print(f"RUN-TIME DURATION: {self.delta_time} seconds")