from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

EXCLUDE_KEY_WORDS = {"Project", "Thesis", "Internship", "Academic", "Bachelor", "Search"}

# []
def extract_info_from_table(driver, link):
    # []
    driver.get(link)

    # []
    course_urls = []

    # [] 
    # table = driver.find_element(By.CLASS_NAME, "table")
    courses = driver.find_elements(By.TAG_NAME, "a")

    for course in courses:
        course_name = course.text.strip()           # TODO: Remove this...
        course_link = course.get_attribute("href")

        # [] DTU is littered with <a> tags unnecessarily so we need to filter all this
        if course_name and not any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS) and any(keyword in course_link for keyword in "course"):
            course_urls.append(course_urls)
            print(f"          := {course_name}: {course_link}")
            
        else:
            continue
        # !
    
    return course_urls

def extract_courses_by_departments(driver):
    driver.implicitly_wait(1)
    department_links : List[(str, str)] = []

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

    for (depName, depLink) in department_links:
        print(f"      !~~~~~~~~~~~~~~~~~~~~{depName}~~~~~~~~~~~~~~~~~~!")

        extracted_courses = extract_info_from_table(driver, depLink)
        print(f"          := Number of courses extracted: {len(extracted_courses)}")

        print("      !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")

    # driver.get_element(By.CLASS_NAME, "table")


def dtuws(service):
    print("!===========================================DTUWS=======================================================!")

    # []
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('--headless')

    # []
    driver = webdriver.Chrome(options=driver_options, service=service)

    # [] Get the DTU courses website:
    driver.get("https://kurser.dtu.dk/")

    # [] Extract all courses via the various departments:
    extract_courses_by_departments(driver)

    print("!===================================================================================================!")