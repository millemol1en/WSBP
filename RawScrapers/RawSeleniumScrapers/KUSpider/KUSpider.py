from typing import List
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from DataObjects.Department import Department
from Infrastructure.SeleniumInfrastructure.SeleniumAbstractCrawler import UniSpider
from Defs.Defs import EXCLUDE_KEY_WORDS

class RawKUSpider(UniSpider):
    def run_spider(self, driver):
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # [] 
        driver.get(self.url)

        # [] 
        self.scrape_departments(driver)
        
        # [] 
        self.scrape_department_courses(driver)

        print(f"    ?= Number of Departments: {len(self.departments)}")

        for department in self.departments:
            print(f"    ?= {department.name}: Num Courses: {len(department.courses)}")

        print("    !----------------------------------------------------------------------------------------------!")

    # TODO: Update the names - more universal naming conventions and structure:
    # []
    def scrape_departments(self, driver):
        # [] Get the department - stored as a <section> tag in HTML
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
                    department_url = "https://kurser.ku.dk/search?programme=BA&departments=" + option_value

                    # [] Create a new department object
                    new_department_obj = Department(_depName = option_text, _depURL = department_url)
                    self.departments.append(new_department_obj)

    # [] Here we use visit the department URL and collect the associated courses
    def scrape_department_courses(self, driver):
        for department in self.departments:
            # TODO: Remove!
            print(f"           |==============================={department.name}===============================|")
         
            driver.get(department.url)

            # TODO: Needs to be updated to List[Course] when ready...
            course_urls : List[str] = []

            # [] We gather all the <a> tags and thereaftr loop over them, retrieving the "href" to the course
            #    as well as filtering out those we don't want:
            courses = driver.find_elements(By.TAG_NAME, "a")
            for course in courses:
                course_name = course.text.strip()
                course_url  = course.get_attribute("href")

                if not any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS):
                    # TODO: Change this to create a new Course object and store it
                    course_urls.append(course_url)
                    print(f"             := {course_name}: {course_url}")
                
                else:
                    continue

            # [] Update our "courses" objects with their new Courses list
            department.courseURLs = course_urls

            # TODO: Remove!
            print("           |======================================================================|")

    def scrape_department_course_content(self, driver):
        return super().scrape_department_course_content(driver)
    
    def scrape_single_course(self, driver):
        return super().scrape_single_course(driver)