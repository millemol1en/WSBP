import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Defs.Defs import EXCLUDE_KEY_WORDS, NON_BOOK_MARKERS
from Infrastructure.SeleniumInfrastructure.SeleniumAbstractCrawler import UniSpider
from DataObjects.Book import Book
from DataObjects.Course import Course
from DataObjects.Department import Department

class GroningenSpider(UniSpider):
    """ STEP 1 """
    # [] 
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")
        time_start = time.time()

        # []
        driver.get(self.url)
        driver.implicitly_wait(1.0)

        # [] 
        self.scrape_departments(driver)

        # [] 
        self.scrape_department_courses_threaded(driver)

        # []
        # self.scrape_department_course_threaded(driver)

        time_end = time.time()
        run_time = round(time_end - time_start, 2)

        print(f"     != GRONINGEN TIME: {run_time}")
        # TODO: Remove!
        print("    !----------------------------------------------------------------------------------------------!")

    """ Step 2 """
    # [] 
    def scrape_departments(self, driver):
        # [] The URL is a JSON file and if successful we can bypass the traditional JavaScript to instead 
        #    gather the necessary information via requests
        url = "https://ocasys.rug.nl/api/faculty/catalog/2024-2025"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json() 

            # [] Extract all department name, associated programs (containing the courses) and have a temporary
            #    storage location for the programs, the variable 'program_url_list'
            for faculty in data:
                faculty_name     = faculty.get("titleEn", "Unknown")
                faculty_programs = faculty.get("programs")
                program_url_list = []

                #if faculty_name in { "Honours College", "Teaching Center" }: continue # TODO: REASON FOR SKIPPING?
                if faculty_name != "Law": continue #TODO: Testing!

                # [] Iterate over the faculties and get the programs:
                for program in faculty_programs:
                    program_level = program.get("levels")
                    program_name  = program.get("titleEn")
                    program_code  = program.get("code")

                    # [] We only wish to have the programs which are for Bachelors and Masters:
                    if program_code and any(level in { "BACHELOR", "MASTER" } for level in program_level):
                        program_url = (f"https://ocasys.rug.nl/api/2024-2025/scheme/program/{program_code}")
                        # (OLD VERSION) -> program_url = (f"https://ocasys.rug.nl/2024-2025/catalog/programme/{program_code}")
                        program_url_list.append(program_url)


                # [] We store the program URLs in the variable 'depCourseURLs' (which holds that departments course URLs)
                #    as it offers a temporary resting spot without having to assign a new variable to the class Department
                new_department = Department(_depName=faculty_name, _depCourseURLs=program_url_list)
                self.departments.append(new_department)

        else:
            print(f"Failed to fetch JSON: {response.status_code}")
    

    """ Step 3 """
    # [3.1] 
    def scrape_department_courses_raw(self, _):
        for department in self.departments:
            self.scrape_department_courses_threaded(department)

    # [3.2]
    def scrape_department_courses_threaded(self, _):
        with ThreadPoolExecutor() as executor:
            executor.map(lambda department: self.scrape_department_courses(department), self.departments)

    # [3.3]
    def scrape_department_courses(self, department):
        # [] Iterate over every department and create temporary storage
        dep_course_urls = []
        # TODO: Remove!
        print(f"  =* {department.name}")
        for program_url in department.courseURLs:
            response = requests.get(program_url)

            if response.status_code == 200:
                data = response.json()

                blocks  = data.get("blocks", [])

                # [] Iterate over the programs and get the courses
                for block in blocks:                        
                    courseEntries = block.get("entries", [])
                    
                    for entry in courseEntries:
                        course_offering = entry.get("courseOffering", {})
                        course_data = course_offering.get("course", {})
                        course_code = course_data.get("code")
                        course_name = course_data.get("titleEn")
                        if any(keyword in course_name.lower() for keyword in EXCLUDE_KEY_WORDS): continue
                        course_json_data = (f"https://ocasys.rug.nl/api/2024-2025/course/page/{course_code}")
                        dep_course_urls.append(course_json_data)
                        print(f"{course_name} - {course_code}") # TODO: Remove!
                
            department.courseURLs = dep_course_urls

    """ Step 4 """
    # [4.1]
    def scrape_department_course_raw(self, _):
        for department in self.departments:
            self.scrape_department_course_content(self, department)

    # [4.2]
    def scrape_department_course_threaded(self, _):
        with ThreadPoolExecutor() as executor:
        # Each department runs in its own thread
            executor.map(lambda department: self.scrape_department_course_content(department), self.departments)

    # [4.3]
    def scrape_department_course_content(self, department):
        print(f"Course Lit Size: {len(department.courseURLs)}")
    
        for course_url in department.courseURLs:
            course = self.scrape_single_course(course_url)

        if course:
            course.__print__()

    """ Step 5 """
    # [5.1]
    def scrape_single_course(self, course_url) -> Course:
        response = requests.get(course_url)

        if response.status_code == 200:
            data = response.json()
        
            # []
            course_code  = data.get("code")
            course_title = data.get("titleEn")
            course_books = []

            # []
            for offering in data.get("courseOfferings", []):
                books = offering.get("books", [])

                for book in books:
                    book_title  = book.get("title").replace("[i]", "").replace("[/i]", "")
                    book_isbn   = book.get("isbn")
                    book_author = book.get("author")
                    
                    # [] Must at least have a title and author:
                    if book_title and book_author and book_title.lower() not in NON_BOOK_MARKERS:
                        new_book = Book(_title=book_title, _author=book_author, _isbn=book_isbn)
                        course_books.append(new_book)
            
            if len(course_books) == 0: return None
            else: return Course(_name=course_title, _code=course_code, _literature=course_books)

        else:
            print(f"Failed to fetch JSON: {response.status_code}")
    

    # OLD FUNCTIONS:

    # def scrape_department_courses(self, driver):
    #     # [] 
    #     for department in self.departments:
    #         # [] Temporary storage for the department URLs.
    #         #    At this stage, the 'departments.courseURLs' has all the departments program lists.
    #         #    The program lists contain as a sub-set all the departments courses. 
    #         dep_course_urls = []

    #         print(f"  => {department.name}")

    #         # []
    #         for program_url in department.courseURLs:
    #             # [] Try-catch is present as some programs are empty
    #             try:
    #                 # print(f"     *= {program_url}")
    #                 driver.get(program_url)

    #                 # [] Locate the container for the courses - inside of the <div class="css-chbhq">
    #                 #    Then retrieve all <a> tags within this div container
    #                 course_table = WebDriverWait(driver, 10).until(
    #                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-chbhq"))
    #                 )
    #                 courses = course_table.find_elements(By.TAG_NAME, "a")

    #                 # [] For each course we collect its course code and append it to the static URL portion.
    #                 #    This will take us to the URL destination for each departments JSON file.
    #                 for course in courses:
                        
    #                     if any(keyword in course.text.strip().lower() for keyword in EXCLUDE_KEY_WORDS): continue
    #                     if course.text.strip().lower():
    #                         course_url  = course.get_attribute("href")

    #                         course_code = ""
    #                         match = re.search(r'/([^/]+)#', course_url)
    #                         if match: course_code = match.group(1)
    #                         course_json_data = (f"https://ocasys.rug.nl/api/2024-2025/course/page/{course_code}")

    #                         dep_course_urls.append(course_json_data)

    #             except Exception as e:
    #                 continue

    #         department.courseURLs = dep_course_urls