import re
import io
import requests
from typing import List
from enum import Enum
from urllib.parse import urlparse, unquote, urljoin
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from PyPDF2 import PdfReader
import pymupdf

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


    # []
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
            # if department.abbr in EXCLUDE_DEPARTMENTS: continue
            if department.abbr != "sft": continue
            # if department.abbr not in { "hti", "rs", "sn", "so" }: continue
            
            # [] 
            (subject_lists, format_type, check) = self.scrap_course_from_department_subject_list(driver, department)
            
            # []
            # TODO: Change to List[Course]
            scraped_courses : List[str] = []

            match format_type:
                # [] Case #1: <main> & <a>
                case SubjectListFormatType.A:
                    # [] 
                    subject_list_url : str = (f"{department.url}{subject_lists[0]}")
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
                        if self.is_url_valid(course_url, department.abbr, check):
                            # print(f"            -> {course_txt} [VALID]")
                            self.scrape_single_course(driver, course_url)
                        else:
                            print(f"            -> {course_txt} [INVALID]")

                # []
                case SubjectListFormatType.B:
                    subject_list_url : str = (f"{department.url}{subject_lists[0]}")
                    driver.get(subject_list_url)
                    driver.implicitly_wait(0.2)

                    print(f"        *= [B :: {check}] {department.name} - {subject_list_url}")

                    # [] Container for courses:
                    main_tag = driver.find_element(By.TAG_NAME, "main")

                    # []
                    tr_tags = main_tag.find_elements(By.TAG_NAME, "tr")

                    print(f"          -> Number of <tr> tags: {len(tr_tags)}")
                    # []
                    test_counter : int = 0 #TODO: REMOVE!
                    for course in tr_tags:
                        if test_counter > 3: continue #TODO: REMOVE!
                        course_url = course.get_attribute("data-href")
                        course_name_parts = course.find_elements(By.TAG_NAME, "td")

                        if course_name_parts: 
                            course_txt = course_name_parts[0].text.strip()
                            if self.is_url_valid(course_url, department.abbr, check):
                                # print(f"            -> {course_txt} [VALID]")
                                self.scrape_single_course(driver, course_url)
                            else:
                                print(f"            -> {course_txt} [INVALID]")

                        test_counter = (test_counter + 1) #TODO: REMOVE!

                # []
                case SubjectListFormatType.C:
                    subject_list_url : str = (f"{department.url}{subject_lists[0]}")
                    
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

                        print(f"          ?= Page Number: {pg_num}") # TODO: REMOVE!
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
                    subject_list_url : str = (f"{department.url}{subject_lists[0]}")

                    print(f"        *= [D :: {check}] {department.name} - {subject_list_url}")


                case SubjectListFormatType.E:
                    subject_list_length : int = len(subject_lists)

                    print(f"        *= [E :: {check}] {department.name} - Subject List Length: {subject_list_length}")


                case _: 
                    print(f"        *= [Type None] {department.name}")

    # SCRAP COURSE LITERATURE METHOD #1
    # TODO: Remove 'driver' from arguments...
    # []
    def scrape_single_course_II(self, driver, course_url):
        # []
        parsed_url = urlparse(course_url)
        base_url = "https://www.polyu.edu.hk/"

        if not parsed_url.netloc: 
            course_url = urljoin(base_url, course_url)

        # []
        r = requests.get(course_url)
        f = io.BytesIO(r.content)

        # []
        reader = PdfReader(f)

        # []
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)

        # []
        full_text = "\n".join(full_text)
        lines = full_text.split('\n')

        # []
        subject_code  = None
        subject_title = None
        reading_list  = []
        capture_lit   = False

        for i, line in enumerate(lines):
            if "Subject Code" in line:
                subject_code = line.replace("Subject Code", "").strip()
            if "Subject Title" in line:
                subject_title = line.replace("Subject Title", "").strip()
            if "Reading List and" in line:  
                print("Reading list located!")
                capture_lit = True  # Start capturing references
                continue  # Skip the header line itself

            if capture_lit:  
                reading_list.append(line.strip())

        print(f"            => Subject Code: {subject_code}")
        print(f"            => Subject Title: {subject_title}")
        print(f"            => Reading List and References:")
        print("\n".join(reading_list))

    # SCRAP COURSE LITERATURE METHOD #2
    def scrape_single_course(self, driver, course_url):
        print(f"{'-'*30}")
        parsed_url = urlparse(course_url)
        base_url = "https://www.polyu.edu.hk/"

        if not parsed_url.netloc: 
            course_url = urljoin(base_url, course_url)

        req       = requests.get(course_url)
        req_data  = req.content
        pdf_doc   = pymupdf.Document(stream=req_data, filetype="pdf")
        num_pages = len(pdf_doc)

        # print(f"Number of pages: {len(pdf_doc)}") 

        # [] For each page in the PDF document, we locate the 'Subject Code', 'Subject Title' and 'Reading List and References'
        for pg_idx in range(0, num_pages, 1):
            # [] Get the current PDF page, locate the tables inside it and target the first (as there is only one table):
            curr_page   = pdf_doc[pg_idx]
            curr_tables = curr_page.find_tables()
            curr_table  = curr_tables[0]

            # []
            subject_code, subject_title, literature = None, None, []
            
            for row_idx, row in enumerate(curr_table.extract()):
                if row[0] in ['Subject Code', 'Subject Title', 'Reading List and\nReferences']:
                    if row[0] == 'Subject Code':
                        subject_code = row[1].strip()
                        print(f"Subject Code: {subject_code}")
                    elif row[0] == 'Subject Title':
                        subject_title = row[1].strip()
                        print(f"Subject Title: {subject_title}")
                    elif row[0].startswith('Reading List'):
                        raw_references = row[1]
                        print(self.clean_citation_text(raw_references))
                        #book_entries = self.extract_citation(self.clean_citation_text(raw_references))
                        #literature.extend(book_entries)

        for lit in literature:
            print(lit)

        print(f"{'-'*30}")
        
    # []
    # All citations are stored in APA citation format:
    def extract_citation(self, text):
        # Step 3: Regex to match citations in APA format
        citation_pattern = re.compile(r"([A-Za-z\s.,&'-]+)\((\d{4})\)\. (.+?)\.\s*([A-Za-z\s&:,]+)\.")
        
        citations = []
        for match in citation_pattern.finditer(text):
            authors = match.group(1).strip()
            year = match.group(2).strip()
            title = match.group(3).strip()
            publisher = match.group(4).strip()

            citations.append({
                "authors": authors,
                "year": year,
                "title": title,
                "publisher": publisher
            })

        return citations
    
    # [] Clean Citation Pipeline:
    def clean_citation_text(self, raw_text):
        # Step 1: Remove unwanted newlines within a citation
        cleaned_text = re.sub(r"(\w)-\n(\w)", r"\1\2", raw_text)        # Fix hyphenated words split by newlines
        cleaned_text = re.sub(r"\n+", " ", cleaned_text)                # Replace newlines with spaces within citations
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()     # Remove extra spaces

        # Step 2: Ensure correct punctuation spacing
        cleaned_text = re.sub(r" ,", ",", cleaned_text)                 # Fix space before commas
        cleaned_text = re.sub(r" \.", ".", cleaned_text)                # Fix space before periods
        cleaned_text = re.sub(r" :", ":", cleaned_text)                 # Fix space before colons
        cleaned_text = re.sub(r"\.(?=\w)", ". ", cleaned_text)          # Ensure space after periods
        
        # Step 3: 
        cleaned_text = re.sub(r"\((\d{4})\),", r"(\1).", cleaned_text)  # Commas proceeding a publication year will be converted to full-stop
        cleaned_text = re.sub(r"\b(ed|edition)\b", "Edition", cleaned_text, flags=re.IGNORECASE)  # Standardize "ed" and "edition"
        # cleaned_text = re.sub(r"\b(\d+)(st|nd|rd|th) Edition\b", r"\1 Edition", cleaned_text)

        return cleaned_text

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
    def scrap_course_from_department_subject_list(self, driver, department) -> (List[str] | SubjectListFormatType | bool):
        match department.abbr:
            case "lgt":  return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.C, False) # Department of Logistics and Maritime Studies              :: 
            case "mm":   return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.A, False) # Department of Management and Marketing                    :: 
            case "af":   return (["/study/subject-syllabi/"],                                                                               SubjectListFormatType.C, True)  # Department of Accounting and Finance                      :: 
            
            case "ama":  return (["/study/subject-library/"],                                                                               SubjectListFormatType.B, False) # Department of Applied Mathematics                         :: 
            case "dsai": return (["/study/ug/bsc-scheme-in-data-science-and-artificial-intelligence/subjects/"],                            SubjectListFormatType.B, False) # Department of Data Science and Artificial Intelligence    :: 
            
            case "bre":  return (["/study/undergraduate-programmes/subjects_syllabi/2023-2024/"],                                           SubjectListFormatType.A, True)  # Department of Building and Real Estate                    :: 
            case "cee":  return (["/current-students/teaching-and-learning/syllabus/"],                                                     SubjectListFormatType.A, False) # Department of Civil and Environmental Engineering         :: 
            case "lsgi": return (["/study/lsgi-subject-list/"],                                                                             SubjectListFormatType.A, False) # Department of Land Surveying and Geo-Informatics          :: 
            
            case "aae":  return (["/study/subject-list/"],                                                                                  SubjectListFormatType.A, False) # Department of Aeronautical and Aviation Engineering       :: 
            case "bme":  return (["/study/undergraduate-programme/admissions/list-of-subjects-and-subject-description-forms/", 
                                  "/study/taught-postgraduate-programme/master-of-science-in-biomedical-engineering/programme-structure/"], SubjectListFormatType.A, True)  # Department of Biomedical Engineering                      :: 
            case "ise":  return (["/study/information-for-current-students/programme-related-info/subject-syllabi/"],                       SubjectListFormatType.A, False) # Department of Industrial and Systems Engineering          :: 
            case "eee":  return (["/study/information-for-current-students/subject-syllabi/"],                                              SubjectListFormatType.A, False) # Department of Electrical and Electronic Engineering       :: 
            case "me":   return (["/study/course-info/subject-list/"],                                                                      SubjectListFormatType.A, False) # Department of Mechanical Engineering                      :: 

            case "apss": return (["docdrive/subject/"],                                                                                     SubjectListFormatType.D, False) # Department of Applied Social Sciences                     :: 
            case "hti":  return (self.query_for_course_urls(driver, department), SubjectListFormatType.E, False)
            case "rs":   return (self.query_for_course_urls(driver, department), SubjectListFormatType.E, False)
            case "sn":   return (self.query_for_course_urls(driver, department), SubjectListFormatType.E, False)
            case "so":   return (self.query_for_course_urls(driver, department), SubjectListFormatType.E, False)
            
            # TODO ... add the others ... 

            case "cbs":  return (["/study/undergraduate-programmes/gur-subjects-offered-by-cbs/cluster-area-requirements/", 
                                  "/study/undergraduate-programmes/gur-subjects-offered-by-cbs/service-learning/"],                         SubjectListFormatType.A, False) # Chinese and Bilingual Studies                             :: 
            case "chc":  return (["/study/undergraduate-programmes/bachc--list-of-all-subjects/"],                                          SubjectListFormatType.A, True)  # The Chinese History Center                                :: 

            case "clc":  return (["/subjects/chinese-discipline-specific-requirement-subjects/subject-information/", 
                                  "/subjects/chinese-language-and-communication-requirement-subjects/", 
                                  "/subjects/chinese-subjects-for-non-chinese-speaking-students/"],                                         SubjectListFormatType.A, True)  # Chinese Language Center                                   :: 
            case "engl": return (["/study/full-subject-list/"],                                                                             SubjectListFormatType.A, False) # Department of English & Communication                     :: 
            case "elc":  return (["/subjects/all-subjects/"],                                                                               SubjectListFormatType.A, True)  # English Language Center                                   :: 

            case "ap":   return (["/study/subject-list/bachelor-programme/", "/study/subject-list/master-programme/"],                      SubjectListFormatType.B, False) # Department of Applied Physics                             :: 

            case "abct": return (["/study/undergraduate-programmes/list-of-all-subjects_ug/", 
                                 "/study/taught-postgraduate-programmes/list-of-all-subjects_tpg/", 
                                 "/study/research-postgraduate-programme/list-of-all-subjects_rpg/"],                                       SubjectListFormatType.A, False) # Department of Applied Biology and Chemical Technology     :: 

            case "fsn":  return (["/study/list-of-all-subjects/"],                                                                          SubjectListFormatType.A, True)  # Department of Food Science and Nutrition                  :: 
            case "sft":  return (["/programme-information/subject-synopsis/"],                                                              SubjectListFormatType.B, False) # School of Fashion and Textiles                            :: 

            case _:      return ([],                                                                                                        SubjectListFormatType.F, False) 


    # []
    def query_for_course_urls(self, driver, department) -> List[str]:
        # [] 
        query_string_url = f"{department.url}/search-result/?query=Subject+Description+Form"

        # [] 
        driver.get(query_string_url)
        search_results = driver.find_elements(By.TAG_NAME, "article")

        # [] 
        subject_urls = [] 

        # [] 
        for result in search_results:
            res_tag  = result.find_element(By.CSS_SELECTOR, "a.underline-link")  # The <a> tag within the first of 3 <p> tags
            res_url  = res_tag.get_attribute("href")

            if res_url:
                subject_urls.append(res_url)

        return subject_urls

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