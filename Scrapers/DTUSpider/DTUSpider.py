from typing import List
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.UniSpider import UniSpider
from DataObjects.Department import Department
from Defs.Defs import EXCLUDE_KEY_WORDS

class DTUSpider(UniSpider):
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)

        # []
        departments = self.get_departments(driver)
        
        # []
        department_courses = self.get_department_courses(driver, departments)

        # TODO: Remove!
        print(f"LENGTH: {len(department_courses)}")
        print("    !----------------------------------------------------------------------------------------------!")

    def get_departments(self, driver):
        print(f"        !~~~~~~~~~~~~~~~~~~~~~~~~~~Getting Courses from URL: {self.url}~~~~~~~~~~~~~~~~~~~~~~~~~~!")
        driver.implicitly_wait(1)

        # []
        department_links : List[(str, str)] = []

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
                department_link = "https://kurser.dtu.dk/search?CourseType=DTU_BSC&Department=" + option_value
                department_links.append((option_text, department_link))

        # TODO: Remove!
        print("        !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")
        
        return department_links

    def get_department_courses(self, driver, departments):
        # []
        department_list : List[Department] = []

        # [] 
        for (depName, depLink) in departments:
            # TODO: Remove!
            print(f"             |==============================={depName}===============================|")

            # []
            new_department = Department(depName, depLink)
            
            # []
            driver.get(depLink)

            # []
            course_urls = []

            # [] 
            courses = driver.find_elements(By.TAG_NAME, "a")

            # []
            for course in courses:
                course_name = course.text.strip()
                course_link = course.get_attribute("href")

                if course_name and not any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS) and any(keyword in course_link for keyword in "course"):
                    course_urls.append(course_link)
                    print(f"            := {course_name}: {course_link}")
                
                else:
                    continue

            # []
            new_department.courses = course_urls
            department_list.append(new_department)

            # TODO: Remove!
            print("             |======================================================================|")

        return department_list