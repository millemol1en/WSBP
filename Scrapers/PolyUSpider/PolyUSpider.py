from typing import List
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.UniSpider import UniSpider
from DataObjects.Department import Department

class PolyUSpider(UniSpider):
    """ INHERITED FUNCTIONS """
    def run_spider(self, driver):
        # TODO: Remove!
        print(f"    !---------------------------------------------{self.name}---------------------------------------------!")

        # []
        driver.get(self.url)
        driver.implicitly_wait(0.5)

        # []
        departments = self.get_departments(driver)
        
        # []
        department_courses = self.get_department_courses(driver, departments)

        # TODO: Remove!

        print("    !----------------------------------------------------------------------------------------------!")
    
    def get_departments(self, driver):
        # [] Each faculty is stored inside a <div> tag with the specified class. 
        #    Extremely violatile. 
        faculty_divs = driver.find_elements(By.CLASS_NAME, "ITS_Content_News_Highlight_Collection")

        # []
        department_links = []

        # []
        for fac_div in faculty_divs:
            # TODO: Remove!
            fac_name = fac_div.find_element(By.XPATH, ".//div[contains(@class, 'list-highlight__left')]/p[contains(@class, 'list-highlight__heading')]").text

            # [] Retrieve the container <div> tags which hold all of the faculties:
            links = fac_div.find_elements(By.XPATH, ".//ul[contains(@class, 'border-link-list')]/li/a")  # Locate <a> inside <ul>

            # []
            for link in links:
                dep_link = link.get_attribute("href")
                dep_name = link.text.strip()
                if dep_link and dep_name:  # Ensure no empty values
                    department_links.append((dep_name, dep_link))

        return department_links

    
    def get_department_courses(self, driver, departments):
        # []
        for (depName, depLink) in departments:
            
            # [] We then call function nr. '4'
            subject_list_href = self.get_subject_list_url(driver, depLink)
            
            print(f"         := {depName}: {subject_list_href}")

    
    def scrape_single_course(self, driver):
        return super().scrape_single_course(driver)
    
    """ LOCAL FUNCTIONS """
    # [4] This function is used to find the links containing the departments subject list:
    def get_subject_list_url(self, driver, department_url):
        # [] 
        driver.get(department_url)

        # [] 
        programs_url = []

        # [] 
        nav_menu = driver.find_element(By.CLASS_NAME, "mn__nav")

        """ CASE 2 """
        # [] 
        links = nav_menu.find_elements(By.TAG_NAME, "a")

        # [] 
        for link in links:
            text = link.get_attribute("href").strip().lower()
            if "subject" in text:  # Check for keyword match
                return link.get_attribute("href")
        
        # [] In case we fail
        return None
    

"""
    - Department of Logistics and Maritime Studies              :: YES # https://www.polyu.edu.hk/lms/search-result/?query=Subject+List
    - Department of Management and Marketing                    :: YES # https://www.polyu.edu.hk/mm/search-result/?query=Subject+List
    - School of Accounting and Finance                          :: YES # https://www.polyu.edu.hk/af/search-result/?query=Subject+List
    - Department of Applied Mathematics                         :: YES # https://www.polyu.edu.hk/ama/search-result/?query=Subject+List 
    - Department of Computing                                   :: SKIP!
    - Department of Data Science and Artificial Intelligence    :: YES # https://www.polyu.edu.hk/dsai/search-result/?query=Subject+List 
    - Department of Building Environment and Energy Engineering :: YES # https://www.polyu.edu.hk/beee/search-result/?query=Subject+List
                                                                    ^ !!! This one doesn't have a specific 'Subject List' but instead 
    - Department of Building and Real Estate                    :: YES # https://www.polyu.edu.hk/bre/search-result/?query=Subject+List
    - Department of Civil and Environmental Engineering         :: YES # https://www.polyu.edu.hk/cee/search-result/?query=Subject+List
    - Department of Land Surveying and Geo-Informatics          :: YES # https://www.polyu.edu.hk/lsgi/search-result/?query=Subject+List 
    - Department of Aeronautical and Aviation Engineering       :: YES # https://www.polyu.edu.hk/aae/search-result/?query=Subject+List 
    - Department of Biomedical Engineering                      :: YES # https://www.polyu.edu.hk/bme/search-result/?query=Subject+List
                                                                    ^ !!! This one writes "Admissions - List of Subjects and Subject Description Forms | Department of Biomedical Engineering" 
                                                                          containing the word "Forms", so a key differentiation between "Form" and "Forms" is needed
    - Department of Electrical and Electronic Engineering       :: YES # https://www.polyu.edu.hk/eee/search-result/?query=Subject+List 
    - Department of Industrial and Systems Engineering          :: YES # https://www.polyu.edu.hk/ise/search-result/?query=Subject+List
    - Department of Mechanical Engineering                      :: YES # https://www.polyu.edu.hk/me/search-result/?query=Subject+List
    - Department of Applied Social Sciences                     :: YES # https://www.polyu.edu.hk/apss/search-result/?query=Subject+List 
                                                                    ^ !!! The target document is untitled
    - Department of Health Technology and Informatics           :: 
    - Department of Rehabilitation Sciences                     :: 
    - School of Nursing                                         :: 
    - School of Optometry                                       :: 
    - Department of Chinese History and Culture                 :: 
    - Department of Chinese and Bilingual Studies               :: 
    - Department of English and Communication                   :: 
    - Chinese Language Centre                                   :: 
    - Confucius Institute of Hong Kong                          :: 
    - English Language Centre                                   ::
    - Department of Applied Biology and Chemical Technology     :: 
    - Department of Applied Physics                             :: 
    - Department of Food Science and Nutrition                  :: 
    - School of Design                                          :: 
    - School of Fashion and Textiles                            :: 
    - School of Hotel and Tourism Management                    :: 

    |========================================================SEARCH QUERY HTML========================================================|

        <div id="its_search_result">
            ^ <ul class="border-seplist">
                ^ <li class="border-seplist__itm" style="border-top: 0px; --darkreader-inline-border-top: 0px;" !important; data-darkreader-inline-border-top>…</li>
                    ^ <li class="border-seplist__itm">
                        ^ <article class="search-item-blk">
                            ^ <p class="search-item-blk__title">
                                ^ <a href="https://www.polyu.edu.hk/mm/study/subject-syllabi/" class="underline-link">
                            <p class="search-item-blk__link">…</p>
                            <p class="search-item-blk__desc">
                                ^ Contains some sort of description of what it is, so like: "<b>List</b> of <b>Subjects</b>"
                                
    |=================================================================================================================================|
                                
    Key words we a looking for in the nested <a> tag are [order in which we search]: 
        1. "List of Subjects"
        1. "Subject Syllabi" 
        2. "Syllabus"
        3. "Subject List"
        5. "... Bachelors" [for further specification]

    Things to exclude:
        1. Any text containing the word "Form" will be entirely excluded

"""