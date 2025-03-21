from typing import List
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.SeleniumInfrastructure.SeleniumAbstractCrawler import UniSpider
from DataObjects.Department import Department
from Defs.Defs import EXCLUDE_KEY_WORDS

class DTUSpider(UniSpider):
    # [Step .0]
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)

        # []
        self.scrape_departments(driver)
        
        # []
        self.scrape_department_courses(driver)

        # TODO: Remove!
        print(f"    ?= Number of Departments: {len(self.departments)}")

        for department in self.departments:
            print(f"    ?= {department.name}: Num Courses: {len(department.courseURLs)}")

        print("    !----------------------------------------------------------------------------------------------!")

    # [Step .1]
    def scrape_departments(self, driver):
        print(f"        !~~~~~~~~~~~~~~~~~~~~~~~~~~Getting Courses from URL: {self.url}~~~~~~~~~~~~~~~~~~~~~~~~~~!")
        driver.implicitly_wait(1)

        # []
        dep_sec_tag = driver.find_element(By.ID, "Department")
        dep_sec_obj = Select(dep_sec_tag)
        # &CourseType=DTU_BSC

        for option in dep_sec_obj.options:
            option_text  = option.text.strip()
            option_value = option.get_attribute("value")

            if option_value and option_text:
                # [] We are currently forcefully attaching the level (bachelors niveau) to the URL
                #    and in the future we might change this.
                department_url = "https://kurser.dtu.dk/search?CourseType=DTU_BSC&Department=" + option_value

                # [] We create a new Department object and append it to the universities list:
                new_department_obj = Department(_depName = option_text, _depURL = department_url)
                self.departments.append(new_department_obj)

        # TODO: Remove!
        print("        !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")
        
    # [Step .2]
    def scrape_department_courses(self, driver):
        # [] 
        for department in self.departments:
            # TODO: Remove!
            print(f"             |==============================={department.name}===============================|")
            
            # []
            driver.get(department.url)

            # []
            course_urls : List[str] = []

            # [] 
            courses = driver.find_elements(By.TAG_NAME, "a")

            # []
            for course in courses:
                course_name = course.text.strip()
                course_url  = course.get_attribute("href")

                if course_name and not any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS) and any(keyword in course_url for keyword in "course"):
                    course_urls.append(course_url)
                    print(f"            := {course_name}: {course_url}")
                
                else:
                    continue

            # []
            department.courseURLs = course_urls

            # TODO: Remove!
            print("             |======================================================================|")

    # [Step .3]
    def scrape_department_course_content(self, driver):
        return super().scrape_department_course_content(driver)

    # [Step .4]
    def scrape_single_course(self, driver, course_url):
        return super().scrape_single_course(driver)