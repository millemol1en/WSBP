# Scraping API:
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Local Imports:
from DataObjects.Department import Department
from DataObjects.Course import Course
from DataObjects.Exception import ExceptionObj
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO

# Native Python Imports:
import time

class DataPipeline:
    # [0] Initalize our static Department dictionary:
    def __init__(self):
        self.departments : dict[str, Department] = {}
        self.exceptions  : list[ExceptionObj]    = []
        self.delta_time  : float                 = time.time()
        self.excep_ID    : int                   = 0
        self.excep_flag  : bool                  = False

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
                _points     = item['points'],
                _literature = item.get('literature', []),
                _level      = item.get('level', [])
            )

            # [1.3] Retrieve the current department of interest and if the course is unique we add it.
            #       This is necessary to prevent courses which are listed in other departments from being added:
            department = self.departments[department_name]

            if not any(course.code == new_course.code for course in department.courses):
                department.courses.append(new_course)

        if isinstance(item, ExceptionObj): 
            if self.excep_flag == False: self.excep_flag = True

            new_exception = ExceptionObj(
                _ID     = self.excep_ID,
                _name   = item['name'],
                _url    = item['file'],
                _file   = item['file'],
                _line   = item['line'],
                _func   = item['func']
            )
            self.exceptions.append(new_exception)
            self.excep_ID += 1

        return item
    
    # [] 
    def close_spider(self, spider):
        print(f"Finished executing for {spider.name} - {len(self.departments)}")

        for _, department in self.departments.items():
            print(f"  *= Department: {department.name}")
            for course in department.courses:
                # TODO: Change to using the __print__ in course when done testing:
                print(f"      -> {course.name}")

        self.delta_time = time.time() - self.delta_time
        print(f"RUN-TIME DURATION: {self.delta_time} seconds")


        if self.excep_flag:
            for exception in self.exceptions:
                exception.__print__()

