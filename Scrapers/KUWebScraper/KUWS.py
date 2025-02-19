from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from Scrapers.KUWebScraper.KUSSC import scrap_single_course

EXCLUDE_KEY_WORDS = {"Project", "Thesis", "Internship", "Academic", "Bachelor"}

# [0] Function used to reject cookies:
def reject_cookies(driver):
    print("   !------------------------------Rejecting Cookies------------------------------!")

    try:
        cookie_div = driver.find_element(By.ID, "ccc")

        if cookie_div:
            driver.execute_script("arguments[0].innerHTML = arguments[1];", cookie_div, "")
            print("   -> Clicked 'Reject All' button")
        else:
            print("   -> No buttons found in cookie banner.")
    
    except Exception as e:
        print("  Error occurred in function 'reject_cookies' with the following error message")
        print(e)

    print("   !-----------------------------------------------------------------------------!")

# [1] Function used to extract the necessary courses from the 
#    link   ::
#    lst    ::
def extract_info_from_table(driver, link):
    # []
    driver.get(link)

    # []
    course_urls = []

    # [] 
    courses = driver.find_elements(By.TAG_NAME, "a")

    for course in courses:
        course_name = course.text.strip()           # TODO: Remove this...
        course_link = course.get_attribute("href")

        if any(keyword in course_name for keyword in EXCLUDE_KEY_WORDS):
            print(f"          := Skipping course: {course_name}")
            continue

        # !
        course_urls.append(course_urls)
        print(f"          := {course_name}: {course_link}")
    
    return course_urls

# [2]
def extract_courses_by_department(driver):
    print("   !------------------------Getting Courses by Department-------------------------!")

    # []
    department_links : List[(str, str)] = []

    dep_sec_tag = driver.find_element(By.ID, "departments")
    dep_sec_obj = Select(dep_sec_tag)

    # []
    for option in dep_sec_obj.options:
        # [] The website sets the text for the <option> tags to be hidden, so we have to use JS to
        #    harvest the information
        option_text  = driver.execute_script("return arguments[0].textContent;", option).strip()
        option_value = option.get_attribute("value")

        if option_value and option_text:
            department_link = "https://kurser.ku.dk/search?programme=BA&departments=" + option_value
            department_links.append((option_text, department_link))

    # []
    for (depName, depLink) in department_links:
        print(f"      !~~~~~~~~~~~~~~~~~~~~{depName}~~~~~~~~~~~~~~~~~~!")

        extracted_courses = extract_info_from_table(driver, depLink)
        print(f"          := Number of courses extracted: {len(extracted_courses)}")

        print("      !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")

# [3]
def extract_courses_by_faculty(driver):
    print("   !-------------------------Getting Courses by Faculty--------------------------!")

    # []
    faculty_links : List[(str, str)] = []

    # []
    fac_sec_tag = driver.find_element(By.ID, "faculty")
    fac_sec_obj = Select(fac_sec_tag)

    # []
    for option in fac_sec_obj.options:
        option_text  = option.text.strip()                      
        option_value = option.get_attribute("value")

        if option_value:
            # TODO: Remove this - only for testing purposes...
            if option_value == 'FACULTY_0006':
                faculty_link = "https://kurser.ku.dk/search?programme=BA&faculty=" + option_value
                faculty_links.append((option_text, faculty_link))

    # []
    for (facName, facLink) in faculty_links:
        print(f"      !~~~~~~~~~~~~~~~~~~~~{facName}~~~~~~~~~~~~~~~~~~!")

        # !
        extracted_courses = extract_info_from_table(driver, facLink)
        print(f"          := Number of courses extracted: {len(extracted_courses)}")

        print("      !~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!")
    print("   !-----------------------------------------------------------------------------!")

# [4]
def kuws(service):
    print("!============================================KUWS=======================================================!")

    # []
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('--headless') # [] Run in 'no-GUI' mode
    # options.add_argument('--no-sandbox')  # This option runs Chrome with no sandbox (bypass OS security)
    # options.add_argument('--disable-dev-shm-usage')  # This option disables the /dev/shm usage

    # []
    driver = webdriver.Chrome(options=driver_options, service=service)

    # [] Get the KU web course:
    driver.get("https://kurser.ku.dk/")

    # [] Reject cookies:
    reject_cookies(driver)

    # []
    extract_courses_by_faculty(driver)

    print("!===================================================================================================!")