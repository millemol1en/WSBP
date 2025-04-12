import scrapy 
import pymupdf
import re 
import requests
from urllib.parse import urlparse, unquote, urljoin
from enum import Enum
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType


# TODO: Move to "Defs.py"
EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp" }

class SubjectListFormatType(Enum):
    A = "<main>+<a>"
    B = "<main>+<tr>"
    C = "<main>+<tr>+pagination"
    D = "<a>"
    E = "buildup"
    F = "none"

class LLMPolyUCrawler(LLMScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    def scrape_departments(self, response):
        
        faculty_containers = response.css(".ITS_Content_News_Highlight_Collection")

        for fac_container in faculty_containers:
            # [] Faculty Components:
            fac_header     = fac_container.css("p.list-highlight__heading")
            fac_name       = fac_header.css("a span.underline-link__line::text").get().strip() 
            
            # [] Department Components:
            dep_containers = fac_container.css("ul.border-link-list li a")

            if fac_name != "School of Fashion and Textiles": continue

            for dep_container in dep_containers:
                # []
                dep_url  = dep_container.css("::attr(href)").get()
                dep_name = dep_container.css("span.underline-link__line::text").get().strip()
                dep_url  = self.sanitize_department_url(dep_url)
                dep_abbr = self.get_department_abbreviation(dep_url)

                # []
                (subject_list_urls, format_type, check) = self.scrape_course_from_department_subject_list(dep_url, dep_abbr)

                #if format_type != SubjectListFormatType.E: continue
                
                # TODO: LIST WITH MULTIPLE VLAUES REQUIRES A SOLUTION
                if len(subject_list_urls) < 1: continue
                
                # []
                yield scrapy.Request(
                    url=subject_list_urls[0], 
                    callback=self.scrape_department_courses,
                    meta={'department_name': dep_name, 'department_abbr': dep_abbr, 'subject_list_urls': subject_list_urls, 'format_type': format_type, 'check': check}
                )
            
            # TODO: UNDO THIS! + CODE DUPLICATION
            #Specialty case required for Faculties which are also departments:
            if fac_name == "School of Fashion and Textiles":
                # []
                fac_url  = fac_header.css("a::attr(href)").get()
                fac_url  = self.sanitize_department_url(fac_url)
                fac_abbr = self.get_department_abbreviation(fac_url)
            
                # []
                (subject_list_urls, format_type, check) = self.scrape_course_from_department_subject_list(fac_url, fac_abbr)

                # TODO: LIST WITH MULTIPLE VLAUES REQUIRES A SOLUTION
                if len(subject_list_urls) < 1: continue

                yield scrapy.Request(
                    url=subject_list_urls[0],  
                    callback=self.scrape_department_courses,
                    meta={'department_name': fac_name, 'department_abbr': fac_abbr, 'format_type': format_type, 'check': check}
                )

    def scrape_department_courses(self, response):
        department_name   = response.meta['department_name']
        department_abbr   = response.meta['department_abbr']
        format_type       = response.meta['format_type']
        check             = response.meta['check']

        scraped_courses = []

        num_courses_collected = 0

        match format_type:
            # [Case #1] <main> & <a>
            case SubjectListFormatType.A:

                main_tag = response.css("main")
                a_tags = main_tag.css("a")

                for a_tag in a_tags:
                    course_name = a_tag.css("::text").get().strip()
                    course_url  = a_tag.css("::attr(href)").get()

                    if self.is_url_valid(course_url, department_abbr, check):
                        if course_name: print(f"       -:< {course_name}")
                        print(f"            => {course_url}")

            # [Case #2] <main> & <tr>
            case SubjectListFormatType.B:
                print(f"   *= {department_name}: {response.request.url} - {check}")
            
                main_tag = response.css("main")

                tr_tags = main_tag.css("tr")
                
                for tr_tag in tr_tags:
                    if num_courses_collected > 10: break # TODO: REMOVE THIS [Data Accuracy - Viggo]
                    course_url  = tr_tag.css("::attr(data-href)").get()

                    if self.is_url_valid(course_url, department_abbr, check):
                        sanitized_url = self.sanitize_course_url(response.request.url, course_url)
                        
                        yield scrapy.Request(
                            url=sanitized_url,
                            callback=self.scrape_single_course,
                            meta={'department_name': department_name, 'department_abbr': department_abbr, 'check': check}
                        )

                    num_courses_collected += 1 # TODO: REMOVE THIS [Data Accuracy - Viggo]
            
            # [Case #3] ...
            case SubjectListFormatType.C:
                print(f"   *= {department_name}: {response.request.url} - {check}")
            
                main_tag = response.css("main")

                pag_elements = main_tag.css("li.pagination-list__itm.pagination-list__itm--number a::text").getall()
                if pag_elements:
                    last_element_num = int(pag_elements[-1].strip())

                    for pg_num in range(1, last_element_num + 1):
                        pag_url = (f"{response.request.url}?page={pg_num}")
                        print(f"        -> {pag_url}")
                        
                        yield scrapy.Request(
                            url=pag_url,
                            callback=self.handle_format_type_c,
                            meta={'department_name': department_name, 'department_abbr': department_abbr, 'check': check}
                        )


            # [Case #4] ...
            case SubjectListFormatType.D:
                print(f"   *= {department_name}: {response.request.url} - {check}")
                
                course_urls = response.css("a::attr(href)").getall()

                for course_url in course_urls:
                    sanitized_url = self.sanitize_course_url(response.request.url, course_url)
                    #print(f"            => {course_url}")

                    # [] In some instances the URL is not complete and we need to append university base URL

                    yield scrapy.Request(
                        url=sanitized_url,
                        callback=self.scrape_single_course,
                        meta={'department_name': department_name}
                    )          
        
            # [Case #5] ...
            case SubjectListFormatType.E:

                search_results = response.css("article p a")
                print(f"   *= {department_name}: {response.request.url} - {check} - Num Res: {len(search_results)}")

                for search_result in search_results:
                    search_result_link = search_result.css("::attr(href)").get()
                    # print(f"       -> {search_result_link}")

                    yield scrapy.Request(
                        url=search_result_link,
                        callback=self.scrape_single_course,
                        meta={'department_name': department_name}
                    )

            case _:
                print(f"   *= {department_name}: None!")

    # []
    def scrape_single_course(self, response):
        department_name = response.meta['department_name']

        try:
            # [] Retrieve the link to the PDF:
            pdf_doc   = pymupdf.Document(stream=response.body, filetype="pdf")
            num_pages = len(pdf_doc)
            
            # [] The variable we use to store the necessary content
            subject_code, subject_title, literature = None, None, []

            reading_list_bool = False
            for pg_idx in range(0, num_pages, 1):
                # [] Get the current PDF page, locate the tables inside it and target the first (as there is only one table):
                curr_page   = pdf_doc[pg_idx]
                curr_tables = curr_page.find_tables()
                curr_table  = curr_tables[0]

                # [] Navigate the PDF, targetting specific pieces of content:
                for row_idx, row in enumerate(curr_table.extract()):
                    if row[0] in ['Subject Code', 'Subject Title', 'Reading List and\nReferences']:
                        match row[0]:
                            case 'Subject Code':
                                subject_code = row[1].strip()
                                print(f"      -> Subject Code: {subject_code}")
                            case 'Subject Title':
                                subject_title = row[1].strip()
                                #print(f"      -> Subject Title: {subject_title}")
                            case 'Reading List and\nReferences':
                                reading_list_bool = True
                                literature = row[1:]
                                #print(f"      -> Reading List: {literature}")
                            case _: continue     
                    elif reading_list_bool:
                        literature.extend(row[1:])

            literature = self.clean_literature(literature)
            print(f"      -> Literature: {literature}\n -||- \n")
            yield {
                'course_name': subject_title,
                'course_code': subject_code,
                'literature': literature,
                'dep_name': department_name
            }

        except Exception:
            return


    """ LOCAL METHODS """
    # [LM #1] ...
    def sanitize_department_url(self, dep_url) -> str:
        parsed_url = urlparse(dep_url)

        if not parsed_url.netloc or "polyu.edu.hk" not in parsed_url.netloc:
            return urljoin("https://www.polyu.edu.hk/", dep_url.lstrip("/"))

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_url
    
    # [LM #2] Takes the department URL (base_url) are mashes it together 
    def sanitize_course_url(self, dep_url, course_url) -> str:
        parsed_url = urlparse(course_url)

        if not parsed_url.netloc: 
            course_url = urljoin(dep_url, course_url)

        return course_url
    
    # [LM #2] ...
    def get_department_abbreviation(self, dep_url) -> str:
        abbreviation = dep_url.rstrip("/").split("/")[-1]
        if abbreviation == "lms": abbreviation = "lgt"
        return abbreviation

    # [LM #3] ...
    def search_for_course_urls(self, response):
        print("is being called yo!")

    # [LM #4] ...
    def scrape_course_from_department_subject_list(self, dep_url, dep_abbr) -> (list[str] | SubjectListFormatType | bool):
        match dep_abbr:
            case "lgt":  return ([(f"{dep_url}/study/subject-syllabi/")],                                                                               SubjectListFormatType.C, False) # Department of Logistics and Maritime Studies              :: 
            case "mm":   return ([(f"{dep_url}/study/subject-syllabi/")],                                                                               SubjectListFormatType.A, False) # Department of Management and Marketing                    :: 
            case "af":   return ([(f"{dep_url}/study/subject-syllabi/")],                                                                               SubjectListFormatType.C, True)  # Department of Accounting and Finance                      :: 
            
            case "ama":  return ([(f"{dep_url}/study/subject-library/")],                                                                               SubjectListFormatType.A, False) # Department of Applied Mathematics                         :: 
            case "dsai": return ([(f"{dep_url}/study/ug/bsc-scheme-in-data-science-and-artificial-intelligence/subjects/")],                            SubjectListFormatType.A, False) # Department of Data Science and Artificial Intelligence    :: 
            
            case "bre":  return ([(f"{dep_url}/study/undergraduate-programmes/subjects_syllabi/2023-2024/")],                                           SubjectListFormatType.A, True)  # Department of Building and Real Estate                    :: 
            case "cee":  return ([(f"{dep_url}/current-students/teaching-and-learning/syllabus/")],                                                     SubjectListFormatType.A, False) # Department of Civil and Environmental Engineering         :: 
            case "lsgi": return ([(f"{dep_url}/study/lsgi-subject-list/")],                                                                             SubjectListFormatType.A, False) # Department of Land Surveying and Geo-Informatics          :: 
            
            case "aae":  return ([(f"{dep_url}/study/subject-list/")],                                                                                  SubjectListFormatType.A, False) # Department of Aeronautical and Aviation Engineering       :: 
            case "bme":  return ([(f"{dep_url}/study/undergraduate-programme/admissions/list-of-subjects-and-subject-description-forms/"), 
                                  (f"{dep_url}/study/taught-postgraduate-programme/master-of-science-in-biomedical-engineering/programme-structure/")], SubjectListFormatType.A, True)  # Department of Biomedical Engineering                      :: 
            case "ise":  return ([(f"{dep_url}/study/information-for-current-students/programme-related-info/subject-syllabi/")],                       SubjectListFormatType.A, False) # Department of Industrial and Systems Engineering          :: 
            case "eee":  return ([(f"{dep_url}/study/information-for-current-students/subject-syllabi/")],                                              SubjectListFormatType.A, False) # Department of Electrical and Electronic Engineering       :: 
            case "me":   return ([(f"{dep_url}/study/course-info/subject-list/")],                                                                      SubjectListFormatType.A, False) # Department of Mechanical Engineering                      :: 

            case "apss": return ([(f"{dep_url}docdrive/subject/")],                                                                                     SubjectListFormatType.D, False) # Department of Applied Social Sciences                     :: 
            # TODO: Think of a nifty solution... rip
            case "hti":  return ([(f"{dep_url}/search-result/?query=Subject+Description+Form")],                                                        SubjectListFormatType.E, True)
            case "rs":   return ([(f"{dep_url}/search-result/?query=Subject+Description+Form")],                                                        SubjectListFormatType.E, True)
            case "sn":   return ([(f"{dep_url}/search-result/?query=Subject+Description+Form")],                                                        SubjectListFormatType.E, True)
            case "so":   return ([(f"{dep_url}/search-result/?query=Subject+Description+Form")],                                                        SubjectListFormatType.E, True)
            
            case "cbs":  return ([(f"{dep_url}/study/undergraduate-programmes/gur-subjects-offered-by-cbs/cluster-area-requirements/"), 
                                  (f"{dep_url}/study/undergraduate-programmes/gur-subjects-offered-by-cbs/service-learning/")],                         SubjectListFormatType.A, False) # Chinese and Bilingual Studies                             :: 
            case "chc":  return ([(f"{dep_url}/study/undergraduate-programmes/bachc--list-of-all-subjects/")],                                          SubjectListFormatType.A, True)  # The Chinese History Center                                :: 

            case "clc":  return ([(f"{dep_url}/subjects/chinese-discipline-specific-requirement-subjects/subject-information/"), 
                                  (f"{dep_url}/subjects/chinese-language-and-communication-requirement-subjects/"), 
                                  (f"{dep_url}/subjects/chinese-subjects-for-non-chinese-speaking-students/")],                                         SubjectListFormatType.A, True)  # Chinese Language Center                                   :: 
            case "engl": return ([(f"{dep_url}/study/full-subject-list/")],                                                                             SubjectListFormatType.A, False) # Department of English & Communication                     :: 
            case "elc":  return ([(f"{dep_url}/subjects/all-subjects/")],                                                                               SubjectListFormatType.A, True)  # English Language Center                                   :: 

            case "ap":   return ([(f"{dep_url}/study/subject-list/bachelor-programme/"), (f"{dep_url}/study/subject-list/master-programme/")],          SubjectListFormatType.B, False) # Department of Applied Physics                             :: 

            case "abct": return ([(f"{dep_url}/study/undergraduate-programmes/list-of-all-subjects_ug/"), 
                                 (f"{dep_url}/study/taught-postgraduate-programmes/list-of-all-subjects_tpg/"), 
                                 (f"{dep_url}/study/research-postgraduate-programme/list-of-all-subjects_rpg/")],                                       SubjectListFormatType.A, False) # Department of Applied Biology and Chemical Technology     :: 

            case "fsn":  return ([(f"{dep_url}/study/list-of-all-subjects/")],                                                                          SubjectListFormatType.A, True)  # Department of Food Science and Nutrition                  :: 
            case "sft":  return ([(f"{dep_url}/programme-information/subject-synopsis/")],                                                              SubjectListFormatType.B, False) # School of Fashion and Textiles                            :: 

            case _:      return ([],                                                                                                        SubjectListFormatType.F, False)

    # [LM #5] Used to confirm that the retrieved URL is a PDF file as that indicates it is a course
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
    
    # [LM #6]  
    def handle_format_type_c(self, response):
        department_name = response.meta['department_name']
        department_abbr = response.meta['department_abbr']
        check           = response.meta['check']

        tr_tags    = response.css("tr.ITS_clickableTableRow")
        
        for course in tr_tags:
            course_url = course.css("::attr(data-href)").get()

            if self.is_url_valid(course_url, department_abbr, check):
                
                yield scrapy.Request(
                    url=course_url,
                    callback=self.scrape_single_course,
                    meta={'department_name': department_name, 'department_abbr': department_abbr, 'check': check}
                )

    def spider_closed():
        print("PolyU Finished!")

    def call_llm(self):
        return super().call_llm()