from typing import List
from urllib.parse import urlparse
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.UniSpider import UniSpider
from DataObjects.Department import Department

KEYWORDS = ["subject synopsis", "list of subjects", "subject library", "subject syllabi", "syllabus", "subject list", "subjects"]

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

            # [] For each department, we get its URL and append the search query string:
            for link in links:
                # [] Get the URL
                dep_link = link.get_attribute("href").strip()
                
                # [] Get the name of the department
                dep_name = link.text.strip()

                # [] 
                if dep_link and dep_name:                                           # Ensure no empty values
                    sanitized_dep_link = self.sanitize_department_url(dep_link)     # Sanitize the department URL, shifting around the URL if necessary [MENTION IN REPORT]
                    sanitized_dep_link += "/search-result/?query=Subject+List"      # Append the desired search query in the URL
                    department_links.append((dep_name, sanitized_dep_link))         # Add to the outgoing list

        return department_links

    def get_department_courses(self, driver, departments):
        # []
        subject_lists = []

        # []
        for (depName, depLink) in departments:
            # [] 
            driver.get(depLink)

            # []
            search_results = driver.find_elements(By.TAG_NAME, "article")

            # []
            print(f"      := {depName} ~ {depLink} ~ {len(search_results)}")
            try:
                for result in search_results:
                    link_element = result.find_element(By.CSS_SELECTOR, "a.underline-link")
                    link_text = link_element.text.lower()

                    if any(keyword in link_text for keyword in KEYWORDS):
                        print(f"           => {link_text}")
                        subject_lists.append(link_element.get_attribute("href"))
                        break
                    else:
                        print(f"           -: {link_text}")

            except Exception as e:
                print(e)
        
        return subject_lists

    
    def scrape_single_course(self, driver):
        return super().scrape_single_course(driver)
    
    def sanitize_department_url(self, dep_link):
        print(f"Original: {dep_link}")

        parsed_url = urlparse(dep_link)

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            print(f"Altered: {dep_link}")
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_link
    

"""
    - Department of Logistics and Maritime Studies              :: YES # https://www.polyu.edu.hk/lms/search-result/?query=Subject+List
    - Department of Management and Marketing                    :: YES # https://www.polyu.edu.hk/mm/search-result/?query=Subject+List
    - School of Accounting and Finance                          :: YES # https://www.polyu.edu.hk/af/search-result/?query=Subject+List
    - Department of Applied Mathematics                         :: YES # https://www.polyu.edu.hk/ama/search-result/?query=Subject+List 
    - Department of Computing                                   :: SKIP!
    - Department of Data Science and Artificial Intelligence    :: YES # https://www.polyu.edu.hk/dsai/search-result/?query=Subject+List 
    - Department of Building Environment and Energy Engineering :: YES # https://www.polyu.edu.hk/beee/search-result/?query=Subject+List
                                                                    ^ !!! This one doesn't have a specific 'Subject List' but instead a collection of "Subject Description Form"s in the results
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
    - Department of Health Technology and Informatics           :: YES # https://www.polyu.edu.hk/hti/search-result/?query=Subject+List
                                                                    ^ !!! This one doesn't have a specific 'Subject List' but instead a collection of "Subject Description Form"s in the results
    - Department of Rehabilitation Sciences                     :: YES # https://www.polyu.edu.hk/rs/search-result/?query=Subject+List
                                                                    ^ !!! This one doesn't have a specific 'Subject List' but instead a collection of "Subject Description Form"s in the results
    - School of Nursing                                         :: SKIP!
    - School of Optometry                                       :: YES # https://www.polyu.edu.hk/so/search-result/?query=Subject+List
                                                                    ^ !!! This one doesn't have a specific 'Subject List' but instead a collection of "Subject Description Form"s in the results

    - Department of Chinese History and Culture                 :: NO! For this we would have to specifically search for "文學士" and "科目表"
    - Department of Chinese and Bilingual Studies               :: NO! For this we would have to specifically search: "https://www.polyu.edu.hk/cbs/search-result/?query=Subjects+Subject+List"
    - Department of English and Communication                   :: YES # https://www.polyu.edu.hk/engl/search-result/?query=Subject+List
    - Chinese Language Centre                                   :: NO! For this we would have to specifically search for the key term "科目"
    - Confucius Institute of Hong Kong                          :: NO!
    - English Language Centre                                   :: YES # https://www.polyu.edu.hk/elc/search-result/?query=Subject+List 
    - Department of Applied Biology and Chemical Technology     :: YES # https://www.polyu.edu.hk/abct/search-result/?query=Subject+List
                                                                    ^ !!! Good example to make you aware of "Undergrad" VS "Postgrad"
    - Department of Applied Physics                             :: YES # https://www.polyu.edu.hk/ap/search-result/?query=Subject+List
                                                                    ^ !!! Be aware of "Bachelor Program", "Master Programme" and "Research Postgraduate Programme"
    - Department of Food Science and Nutrition                  :: YES # https://www.polyu.edu.hk/fsn/search-result/?query=Subject+List 
    - School of Design                                          :: NO!
    - School of Fashion and Textiles                            :: NO! # https://www.polyu.edu.hk/sft/search-result/?query=Subject+Synopsis
                                                                    ^ !!! Needs this stupid special case.
    - School of Hotel and Tourism Management                    :: YES # https://www.polyu.edu.hk/shtm/search-result/?query=Subject+List

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
        1. "Subject Synopsis"
        2. "List of Subjects"
        3. "Subject Syllabi" 
        4. "Syllabus"
        5. "Subject List"
        6. "... Bachelors" [for further specification]

    Things to exclude:
        1. Any text containing the word "Form" will be entirely excluded

        

    THE URLS ARE FUCKED FROM THE START PAGE - THEY NEED TO BE SHIFTED AROUND
"""