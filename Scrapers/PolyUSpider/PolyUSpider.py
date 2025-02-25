import re
from typing import List
from enum import Enum
from urllib.parse import urlparse
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.UniSpider import UniSpider
from DataObjects.Department import Department

class PolyUSpider(UniSpider):
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)
        driver.implicitly_wait(1.0)

        # []
        self.get_departments(driver)

        # []
        self.scrap_department_courses(driver)

        # TODO: Remove!
        print("    !----------------------------------------------------------------------------------------------!")

    def get_departments(self, driver):
        # [] Each faculty is stored inside a <div> tag which we need to get and iterate over to locate
        #    all the associated departments:
        faculty_containers = driver.find_elements(By.CLASS_NAME, "ITS_Content_News_Highlight_Collection")
    
        for fac_container in faculty_containers:
            # [] Retrieve the title <p> tag and the list of associated departments stored as <ul> & <li> tags
            fac_header     = fac_container.find_element(By.XPATH, ".//p[contains(@class, 'list-highlight__heading')]")
            fac_name       = fac_header.text.strip()
            dep_links      = fac_container.find_elements(By.XPATH, ".//ul[contains(@class, 'border-link-list')]/li/a") 

            # [] For each URL we retrieved we can create a department
            for dep_link in dep_links:
                new_department_obj = self.create_department_object(dep_link, fac_name)

                self.departments.append(new_department_obj)
            
            # [] We need a specialty case for faculties which are themselves departments:
            if fac_name == "School of Hotel and Tourism Management" or fac_name == "School of Fashion and Textiles":
                fac_link = fac_header.find_element(By.TAG_NAME, "a")
                new_department_obj = self.create_department_object(fac_link, fac_name)

                self.departments.append(new_department_obj)


    # [] Creates a new Department object
    def create_department_object(self, department_url, associated_faculty):
        d_url  = department_url.get_attribute("href").strip()                
        d_name = department_url.text.strip()

        if d_url and d_name:
            sanitized_dep_link = self.sanitize_department_url(d_url) 
            abbreviation = sanitized_dep_link.rstrip("/").split("/")[-1]    # Get the department abbreviation

            match abbreviation:

                case "cbs":
                    sanitized_dep_link += "/search-result/?query=Subjects"

                case "clc":
                    sanitized_dep_link += "/search-result/?query=科目"

                case "sft":
                    sanitized_dep_link += "/search-result/?query=Subject+Synopsis"

                case _:
                    sanitized_dep_link += "/search-result/?query=Subject+List"

        new_department = Department(d_name, sanitized_dep_link, [], abbreviation, associated_faculty)
        return new_department

    # TODO: Store it temporarily in a Set<> to check for duplicate values:
    def scrap_department_courses(self, driver):
        for department in self.departments:
            if department.abbr in { "beee", "hti", "rs", "sn", "so", "ap", "abct", "chc", "cbs" }: continue
            
            driver.get(department.url)
            driver.implicitly_wait(0.2)

            search_results = driver.find_elements(By.TAG_NAME, "article")

            print(f"        *= {department.name} ({department.abbr}):")

            for result in search_results:
                res_tag  = result.find_element(By.CSS_SELECTOR, "a.underline-link")  # The <a> tag within the first of 3 <p> tags
                res_url  = res_tag.get_attribute("href")
                res_text = res_tag.text.strip().lower()
                
                pattern = r"(subject\s*(list|syllabi|library))|syllabus"

                if re.search(pattern, res_text) and self.is_valid_link(res_url):
                    print(f"           != {res_text}")  # Debugging: See what matches
                else:
                    print(f"           -> {res_text}")  # Debugging: See what matches
                

    def is_valid_link(self, url):
        parsed_url = urlparse(url)

        if parsed_url.path.endswith((".pdf", ".htm")):
            return False
        
        return True
    
    def scrape_single_course(self, driver):
        return super().scrape_single_course(driver)
    
    def sanitize_department_url(self, dep_link):    
        parsed_url = urlparse(dep_link)

        # []
        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_link