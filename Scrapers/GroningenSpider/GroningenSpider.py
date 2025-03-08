import requests
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Defs.Defs import EXCLUDE_KEY_WORDS
from Infrastructure.UniSpider import UniSpider
from DataObjects.Book import Book
from DataObjects.Course import Course
from DataObjects.Department import Department


class GroningenSpider(UniSpider):
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)
        driver.implicitly_wait(1.0)

        # [] 
        self.scrap_departments(driver)

        # [] 
        self.scrap_department_courses(driver)

        # []
        self.scrap_department_course_content(driver)

        # TODO: Remove!
        print("    !----------------------------------------------------------------------------------------------!")

    def scrap_departments(self, driver):
        # []
        url = "https://ocasys.rug.nl/api/faculty/catalog/2024-2025"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()  # Convert response to JSON

            # Extract all department names
            for faculty in data:
                faculty_name     = faculty.get("titleEn", "Unknown")
                faculty_programs = faculty.get("programs")
                program_url_list = []
                # print(f"    *= {faculty_name}: {len(faculty_programs)}")  # Print department name

                # TODO: REMOVE! ONLY FOR TESTING
                if faculty_name != "Law": continue
                num_programs : int = 0

                for program in faculty_programs:
                    if num_programs > 3: break
                    program_level = program.get("levels")
                    program_name  = program.get("titleEn")
                    program_code  = program.get("code")

                    if any(level in { "BACHELOR", "MASTER" } for level in program_level) and program_code:
                        program_url = (f"https://ocasys.rug.nl/2024-2025/catalog/programme/{program_code}")
                        # TODO: REMOVE!
                        # print(f"        _.- {program_name}")
                        # print(f"            -> {program_code}")
                        # print(f"            -> {program_level}")
                        # print(f"            -> {program_url}")

                        program_url_list.append(program_url)
                    
                    num_programs += 1

                # [] We store the program URLs in the variable 'depCourseURLs' (which holds that departments course URLs)
                #    as it offers a temporary resting spot without having to assign a new variable to the class Department
                new_department = Department(_depName=faculty_name, _depCourseURLs=program_url_list)
                self.departments.append(new_department)

        else:
            print(f"Failed to fetch JSON: {response.status_code}")
    
    def scrap_department_courses(self, driver):
        # [] 
        for department in self.departments:
            # [] Temporary storage for the department URLs.
            #    At this stage, the 'departments.courseURLs' has all the departments program lists.
            #    The program lists contain as a sub-set all the departments courses. 
            dep_course_urls = []

            print(f"  => {department.name}")

            # []
            for program_url in department.courseURLs:
                # [] Try-catch is present as some programs are empty
                try:
                    # print(f"     *= {program_url}")
                    driver.get(program_url)

                    # [] Locate the container for the courses - inside of the <div class="css-chbhq">
                    #    Then retrieve all <a> tags within this div container
                    course_table = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-chbhq"))
                    )
                    courses = course_table.find_elements(By.TAG_NAME, "a")

                    # [] For each course we collect its course code and append it to the static URL portion.
                    #    This will take us to the URL destination for each departments JSON file.
                    for course in courses:
                        
                        if any(keyword in course.text.strip() for keyword in EXCLUDE_KEY_WORDS): continue
                        if course.text.strip().lower():
                            course_url  = course.get_attribute("href")

                            course_code = ""
                            match = re.search(r'/([^/]+)#', course_url)
                            if match: course_code = match.group(1)
                            course_json_data = (f"https://ocasys.rug.nl/api/2024-2025/course/page/{course_code}")

                            dep_course_urls.append(course_json_data)

                except Exception as e:
                    continue

            department.courseURLs = dep_course_urls
    
    # []
    def scrap_department_course_content(self, driver):
        
        for department in self.departments:

            print(f"Course Lit Size: {len(department.courseURLs)}")
        
            for course_url in department.courseURLs:

                course = self.scrape_single_course(driver, course_url)


    # []
    def scrape_single_course(self, driver, course_url) -> Course:
        # [] Redirect driver:
        response = requests.get(course_url)

        if response.status_code == 200:
            data = response.json()  # Convert response to JSON
        
            # []
            

            # []
            for offering in data.get("courseOfferings", []):
                books = offering.get("books", [])

            for book in books:
                print(book)

        else:
            print(f"Failed to fetch JSON: {response.status_code}")
        

    ### LOCAL METHODS ###
    def extract_courses_from_program_list():
        pass
