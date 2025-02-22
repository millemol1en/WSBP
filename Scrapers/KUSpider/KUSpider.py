from typing import List
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from DataObjects.Department import Department
from Infrastructure.UniSpider import UniSpider
from Defs.Defs import EXCLUDE_KEY_WORDS

class KUSpider(UniSpider):
    # []
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)

        # []
        departments = self.get_departments(driver)
        
        # []
        department_courses = self.get_department_courses(driver, departments)

        print(f"LENGTH: {len(department_courses)}")

        print("    !----------------------------------------------------------------------------------------------!")


    # []
    def get_departments(self, driver):
        print(f"        !~~~~~~~~~~~~~~~~~~~~~~~~~~Department URL: {self.url}~~~~~~~~~~~~~~~~~~~~~~~~~~!")

        # [] 
        department_links : List[(str, str)] = []

        # [] 
        dep_sec_tag = driver.find_element(By.ID, "departments")
        dep_sec_obj = Select(dep_sec_tag)

        # [] Retrieve URLs for all the departments:
        for option in dep_sec_obj.options:
            # [] The website sets the text for the <option> tags to be hidden, so we have to use JS to
            #    harvest the information
            option_text  = driver.execute_script("return arguments[0].textContent;", option).strip()
            option_value = option.get_attribute("value")

            if option_value and option_text:
                if option_value == "DEPARTMENT_0013": # TODO: REMOVE THIS - ONLY FOR TESTING!
                    department_link = "https://kurser.ku.dk/search?programme=BA&departments=" + option_value
                    department_links.append((option_text, department_link))

        # TODO: Remove!
        print("        !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")
        
        return department_links

    # []
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

                if not any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS):
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

    def scrape_single_course(self, driver):
        # TODO....

        print(f"Scraping single course")