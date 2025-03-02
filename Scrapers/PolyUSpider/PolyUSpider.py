import re
from typing import List
from enum import Enum
from urllib.parse import urlparse, unquote
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from Infrastructure.UniSpider import UniSpider
from DataObjects.Department import Department

EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp" }

class SubjectListFormatType(Enum):
    A = "<main>+<a>"
    B = "<main>+<tr>"
    C = "<main>+<tr>+pagination"
    D = "<a>"
    E = "buildup"
    F = "none"

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
                new_department_obj = self.create_department_object(dep_link)

                self.departments.append(new_department_obj)
            
            # [] We need a specialty case for faculties which are themselves departments:
            if fac_name == "School of Fashion and Textiles":
                fac_link = fac_header.find_element(By.TAG_NAME, "a")
                new_department_obj = self.create_department_object(fac_link)

                self.departments.append(new_department_obj)


    # [] Creates a new Department object and sanitizes the URL in the process:
    def create_department_object(self, department_url) -> Department:
        d_url  = department_url.get_attribute("href").strip()                
        d_name = department_url.text.strip()

        if d_url and d_name:
            sanitized_dep_link  = self.sanitize_department_url(d_url) 
            abbreviation        = sanitized_dep_link.rstrip("/").split("/")[-1]

            # [] Although named Department of Logistics & Maritime Studies (LMS) and its URL containing that as an abbreviation, the subjects
            #    themselves are stored with department code "lgt". Why? I don't know.
            if abbreviation == "lms": abbreviation = "lgt"
            
            return (Department(d_name, sanitized_dep_link, [], abbreviation))
        else:
            None

    # [] 
    #    Problems: 
    #           1. Some departments may have multiple subject lists
    #           2. Some departments will store the courses in a <table>, but not all.
    #           3. One department doesn't have <main> container for the provided courses - namely "apss".
    #           4. 

    #    For every conceivable approach, there will always be one or more departments which are the outliers to the established system:
    #           1. 
    # TODO: Remove all "print()" functions
    def scrap_department_courses(self, driver):
        for department in self.departments:
            if department.abbr in EXCLUDE_DEPARTMENTS: continue
            
            # [] 
            (url, format_type, check) = self.scrap_course_from_department_subject_list(department.abbr)
            
            match format_type:
                # [] Case #1: <main> & <a>
                case SubjectListFormatType.A:
                    # [] 
                    subject_list_url : str = (f"{department.url}{url[0]}")
                    driver.get(subject_list_url)
                    driver.implicitly_wait(0.2)

                    print(f"        *= [A :: {check}] {department.name} - {subject_list_url}")

                    # [] Container for courses:
                    main_tag = driver.find_element(By.TAG_NAME, "main")

                    # []
                    a_tags = main_tag.find_elements(By.TAG_NAME, "a")

                    # []
                    for course in a_tags:
                        course_url = course.get_attribute("href")
                        course_txt = course.text.strip()
                        if self.is_url_valid(course_url, department.url, False):
                            print(f"            -> {course_txt} [VALID]")
                        else:
                            print(f"            -> {course_txt} [INVALID]")

                # []
                case SubjectListFormatType.B:
                    subject_list_url : str = (f"{department.url}{url[0]}")

                    print(f"        *= [B :: {check}] {department.name} - {subject_list_url}")

                # []
                case SubjectListFormatType.C:
                    subject_list_url : str = (f"{department.url}{url[0]}")
                    
                    print(f"        *= [C :: {check}] {department.name} - {subject_list_url}")

                    driver.get(subject_list_url)
                    driver.implicitly_wait(0.2)

                    # [] Container for courses:
                    main_tag = driver.find_element(By.TAG_NAME, "main")

                    # [] Pagination:
                    pag_elements = main_tag.find_elements(By.CLASS_NAME, "pagination-list__itm--number")
                    if pag_elements:
                        last_element_num = int(pag_elements[-1].text.strip())
                    
                    # []   
                    for pg_num in range(1, last_element_num + 1):
                        # [] Update the URL with a specific page number:
                        subject_list_url_pg = (f"{subject_list_url}?page={pg_num}")
                        driver.get(subject_list_url_pg)

                        # [] These <tr> tags are all the courses for that specific page:
                        tr_tags  = driver.find_elements(By.TAG_NAME, "tr")


                        print(f"          ?= Page Number: {pg_num}")
                        # [] 
                        for course in tr_tags:
                            td_tags = course.find_elements(By.TAG_NAME, "td")

                            if td_tags: 
                                full_course_code = td_tags[0].text.strip().split(' ')[0]

                                extracted_prefix = full_course_code[:len(department.abbr)]

                                if extracted_prefix.lower() == department.abbr:
                                    print(f"            -> {full_course_code} [VALID]")
                                else:
                                    print(f"            -> {full_course_code} [INVALID]")

                case SubjectListFormatType.D:
                    subject_list_url : str = (f"{department.url}{url[0]}")

                    print(f"        *= [D :: {check}] {department.name} - {subject_list_url}")


                case SubjectListFormatType.E:
                    subject_list_url : str = (f"{department.url}{url[0]}")

                    print(f"        *= [E :: {check}] {department.name} - {subject_list_url}")


                case _: 
                    print(f"        *= [Type None] {department.name}")

                

        
    def scrape_single_course(self, driver):
        return super().scrape_single_course(driver)
                

    # [] 
    def is_url_valid(self, url : str, dep_abbr : str, check_abbr : bool) -> bool:
        parsed_url = urlparse(url)

        decoded_path = unquote(parsed_url.path).split('?')[0] 

        if not re.search(r'\.pdf$', decoded_path, re.IGNORECASE):
            return False
        
        if check_abbr:
            try:
                filename = decoded_path.split('/')[-1]
                course_identifier = filename.rsplit('.', 1)[0]
                match = re.match(r'([a-zA-Z]+)', course_identifier)
                extracted_dept = match.group(1).lower()

                return (extracted_dept == dep_abbr)

            except Exception as e:
                print(e)
                return False
        
        return True
    
    # [] ...
    def sanitize_department_url(self, dep_link):    
        parsed_url = urlparse(dep_link)

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_link
    

    # []
    #    Problems:
    #          1. URL stored in "href" is flawed
    #          2. In most cases, the URL will contain the department abbreviation - but not always
    #          3. Some departments will have different abbreviations for their course codes, for example "lms" has LGT and "sft" will have "ICT" and "SFT"


    # Types Include:
    #           1. SubjectListFormatType.A = <main> & <a>
    #           2. SubjectListFormatType.B = <main> & <tr>
    #           3. SubjectListFormatType.C = <main> & <tr> & <pagination>
    #           4. SubjectListFormatType.D = <a>
    #           5. SubjectListFormatType.A = "buildup"
    def scrap_course_from_department_subject_list(self, dep_abbr) -> (List[str] | SubjectListFormatType | bool):
        match dep_abbr:
            case "lgt":  return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.C, False)                                                                                    # Department of Logistics and Maritime Studies              :: URL LOC = <tr> tags; Get course code via first <td>;     [NO NEED TO CHECK]
            case "mm":   return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.A, False)                                                                                    # Department of Management and Marketing                    :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            case "af":   return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.C, True)                                                                                    # Department of Accounting and Finance                      :: URL LOC = <tr> tags; Get course code via first <td>;     [YES NEED TO CHECK]
            
            case "ama":  return (["/study/subject-library/"],                                                                               SubjectListFormatType.B, False)                                                                                   # Department of Applied Mathematics                         :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK] (BROKEN URL)
            case "dsai": return (["/study/ug/bsc-scheme-in-data-science-and-artificial-intelligence/subjects/"],                            SubjectListFormatType.B, False)                                # Department of Data Science and Artificial Intelligence    :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            
            case "bre":  return (["/study/undergraduate-programmes/subjects_syllabi/2023-2024/"],                                           SubjectListFormatType.A, True)                                               # Department of Building and Real Estate                    :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
            case "cee":  return (["/current-students/teaching-and-learning/syllabus/"],                                                     SubjectListFormatType.A, False)                                                         # Department of Civil and Environmental Engineering         :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            case "lsgi": return (["/study/lsgi-subject-list/"],                                                                             SubjectListFormatType.A, False)                                                                                 # Department of Land Surveying and Geo-Informatics          :: URL LOC = <a>  tags; Get course code via URL = DIFFICULT;[NO NEED TO CHECK]
            
            case "aae":  return (["/study/subject-list/"],                                                                                  SubjectListFormatType.A, False)                                                                                      # Department of Aeronautical and Aviation Engineering       :: URL LOC = <a>  tags; Get course code via URL = NO;       [NO NEED TO CHECK]
            case "bme":  return (["/study/undergraduate-programme/admissions/list-of-subjects-and-subject-description-forms/", 
                                  "/study/taught-postgraduate-programme/master-of-science-in-biomedical-engineering/programme-structure/"], SubjectListFormatType.A, True)     # Department of Biomedical Engineering                      :: URL LOC = <a> / fst <td>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
            case "ise":  return (["/study/information-for-current-students/programme-related-info/subject-syllabi/"],                       SubjectListFormatType.A, False)                           # Department of Industrial and Systems Engineering          :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK] (AUTO-DOWNLOAD)
            case "eee":  return (["/study/information-for-current-students/subject-syllabi/"],                                              SubjectListFormatType.A, False)                                                  # Department of Electrical and Electronic Engineering       :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            case "me":   return (["/study/course-info/subject-list/"],                                                                      SubjectListFormatType.A, False)                                                                          # Department of Mechanical Engineering                      :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]

            case "apss": return (["docdrive/subject/"],                                                                                     SubjectListFormatType.D, False)                                                                                         # Department of Applied Social Sciences                     :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            # TODO ... add the others ... 

            case "cbs":  return (["/study/undergraduate-programmes/gur-subjects-offered-by-cbs/cluster-area-requirements/", 
                                  "/study/undergraduate-programmes/gur-subjects-offered-by-cbs/service-learning/"],                         SubjectListFormatType.A, False)                             # Chinese and Bilingual Studies                             :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            case "chc":  return (["/study/undergraduate-programmes/bachc--list-of-all-subjects/"],                                          SubjectListFormatType.A, True)                                              # The Chinese History Center                                :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK] - same as "bme"

            case "clc":  return (["/subjects/chinese-discipline-specific-requirement-subjects/subject-information/", 
                                  "/subjects/chinese-language-and-communication-requirement-subjects/", 
                                  "/subjects/chinese-subjects-for-non-chinese-speaking-students/"],                                         SubjectListFormatType.A, True)                                             # Chinese Language Center                                   :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
            case "engl": return (["/study/full-subject-list/"],                                                                             SubjectListFormatType.A, False)                                                                                 # Department of English & Communication                     :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            case "elc":  return (["/subjects/all-subjects/"],                                                                               SubjectListFormatType.A, True)                                                                                   # English Language Center                                   :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]

            case "ap":   return (["/study/subject-list/bachelor-programme/", "/study/subject-list/master-programme/"],                      SubjectListFormatType.B, False)                          # Department of Applied Physics                             :: URL LOC = <td> tags; Get course code via URL = YES;      [NO NEED TO CHECK]

            case "abct": return (["/study/undergraduate-programmes/list-of-all-subjects_ug/", 
                                 "/study/taught-postgraduate-programmes/list-of-all-subjects_tpg/", 
                                 "/study/research-postgraduate-programme/list-of-all-subjects_rpg/"],                                       SubjectListFormatType.A, False)                                           # Department of Applied Biology and Chemical Technology     :: URL LOC = <a>  tags; Get course code via URL = NO;      [NO NEED TO CHECK]

            case "fsn":  return (["/study/list-of-all-subjects/"],                                                                          SubjectListFormatType.A, True)                                                                              # Department of Food Science and Nutrition                  :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
            case "sft":  return (["/programme-information/subject-synopsis/"],                                                              SubjectListFormatType.B, False)                                                                  # School of Fashion and Textiles                            :: URL LOC = <tr> tags; Get course code via first <td>;     [NO NEED TO CHECK]

            case _:      return ([],                                                                                                        SubjectListFormatType.F, False)


    #############################################
    #                                           #
    #                                           #
    #               APPROACH #1                 #
    #                                           #
    #                                           #
    #############################################
    def run_approach_I():
            print("Running approach II")




    #############################################
    #                                           #
    #                                           #
    #               APPROACH #2                 #
    #                                           #
    #                                           #
    #############################################
    def run_approach_II():
        print("Running approach II")



    # []
    #    Problems:
    #          1. URL stored in "href" is flawed
    #          2. In most cases, the URL will contain the department abbreviation - but not always
    #          3. Some departments will have different abbreviations for their course codes, for example "lms" has LGT and "sft" will have "ICT" and "SFT"
    # def scrap_course_from_department_subject_list(self, dep_abbr) -> List[str]:
    #     match dep_abbr:
    #         case "lms": return (["/study/subject-syllabi/"])                                                                                    # Department of Logistics and Maritime Studies              :: URL LOC = <tr> tags; Get course code via first <td>;     [NO NEED TO CHECK]
    #         case "mm":  return (["/study/subject-syllabi/"])                                                                                    # Department of Management and Marketing                    :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         case "af":  return (["/study/subject-syllabi/"])                                                                                    # Department of Accounting and Finance                      :: URL LOC = <tr> tags; Get course code via first <td>;     [YES NEED TO CHECK]
            
    #         case "ama":  return (["/study/subject-library/"])                                                                                   # Department of Applied Mathematics                         :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK] (BROKEN URL)
    #         case "dsai": return (["/study/ug/bsc-scheme-in-data-science-and-artificial-intelligence/subjects/"])                                # Department of Data Science and Artificial Intelligence    :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
            
    #         case "bre":  return (["/study/undergraduate-programmes/subjects_syllabi/2023-2024/"])                                               # Department of Building and Real Estate                    :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
    #         case "cee":  return (["/current-students/teaching-and-learning/syllabus/"])                                                         # Department of Civil and Environmental Engineering         :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         case "lsgi": return (["/study/lsgi-subject-list/"])                                                                                 # Department of Land Surveying and Geo-Informatics          :: URL LOC = <a>  tags; Get course code via URL = DIFFICULT;[NO NEED TO CHECK]
            
    #         case "aae":  return (["/study/subject-list/"])                                                                                      # Department of Aeronautical and Aviation Engineering       :: URL LOC = <a>  tags; Get course code via URL = NO;       [NO NEED TO CHECK]
    #         case "bme":  return (["/study/undergraduate-programme/admissions/list-of-subjects-and-subject-description-forms/", 
    #                               "/study/taught-postgraduate-programme/master-of-science-in-biomedical-engineering/programme-structure/"])     # Department of Biomedical Engineering                      :: URL LOC = <a> / fst <td>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
    #         case "ise":  return (["/study/information-for-current-students/programme-related-info/subject-syllabi/"])                           # Department of Industrial and Systems Engineering          :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK] (AUTO-DOWNLOAD)
    #         case "eee":  return (["/study/information-for-current-students/subject-syllabi/"])                                                  # Department of Electrical and Electronic Engineering       :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         case "me":   return (["/study/course-info/subject-list/"])                                                                          # Department of Mechanical Engineering                      :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]

    #         case "apss": return (["docdrive/subject/"])                                                                                         # Department of Applied Social Sciences                     :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         # TODO ... add the others ... 

    #         case "cbs":  return (["/study/undergraduate-programmes/gur-subjects-offered-by-cbs/cluster-area-requirements/", 
    #                               "/study/undergraduate-programmes/gur-subjects-offered-by-cbs/service-learning/"])                             # Chinese and Bilingual Studies                             :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         case "chc":  return (["/study/undergraduate-programmes/bachc--list-of-all-subjects/"])                                              # The Chinese History Center                                :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK] - same as "bme"

    #         case "clc":  return (["/subjects/chinese-discipline-specific-requirement-subjects/subject-information/", 
    #                               "/subjects/chinese-language-and-communication-requirement-subjects/", 
    #                               "/subjects/chinese-subjects-for-non-chinese-speaking-students/"])                                             # Chinese Language Center                                   :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
    #         case "engl": return (["/study/full-subject-list/"])                                                                                 # Department of English & Communication                     :: URL LOC = <a>  tags; Get course code via URL = YES;      [NO NEED TO CHECK]
    #         case "elc":  return (["/subjects/all-subjects/"])                                                                                   # English Language Center                                   :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]

    #         case "ap":   return (["/study/subject-list/bachelor-programme/", "/study/subject-list/master-programme/"])                          # Department of Applied Physics                             :: URL LOC = <td> tags; Get course code via URL = YES;      [NO NEED TO CHECK]

    #         case "abct": return (["/study/undergraduate-programmes/list-of-all-subjects_ug/", 
    #                              "/study/taught-postgraduate-programmes/list-of-all-subjects_tpg/", 
    #                              "/study/research-postgraduate-programme/list-of-all-subjects_rpg/"])                                           # Department of Applied Biology and Chemical Technology     :: URL LOC = <a>  tags; Get course code via URL = NO;      [NO NEED TO CHECK]

    #         case "fsn":  return (["/study/list-of-all-subjects/"])                                                                              # Department of Food Science and Nutrition                  :: URL LOC = <a>  tags; Get course code via URL = YES;      [YES NEED TO CHECK]
    #         case "sft":  return (["/programme-information/subject-synopsis/"])                                                                  # School of Fashion and Textiles                            :: URL LOC = <tr> tags; Get course code via first <td>;     [NO NEED TO CHECK]
    #             # case "shtm": return (["/study/subject-syllabi/"])                                                                             # School of Hotel & Tourism Management

    #         case _: return ([])