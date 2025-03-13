import scrapy 
import pymupdf
import re 
from urllib.parse import urlparse, unquote, urljoin
from enum import Enum

from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler

EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp" }

class SubjectListFormatType(Enum):
    A = "<main>+<a>"
    B = "<main>+<tr>"
    C = "<main>+<tr>+pagination"
    D = "<a>"
    E = "buildup"
    F = "none"

class PolyUCrawler(ScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    def scrape_departments(self, response):
        faculty_containers = response.css(".ITS_Content_News_Highlight_Collection")

        for fac_container in faculty_containers:
            fac_header     = fac_container.css("p.list-highlight__heading")
            fac_name       = fac_header.css("a span.underline-link__line::text").get().strip() if fac_header.css("::text").get() else "Unknown"
            dep_urls       = fac_container.css("ul.border-link-list li a::attr(href)").getall()

            print(f"  *= {fac_name}") # TODO: REMOVE!

            for dep_url in dep_urls:
                print(f"     -> Dep Link: {self.sanitize_department_url(dep_url)}")

                dep_url  = self.sanitize_department_url(dep_url)
                dep_abbr = self.get_department_abbreviation(dep_url)

                yield scrapy.Request(
                    url=dep_url,
                    callback=self.scrape_department_courses,
                    meta={'department_name': dep_url, 'department_abbr': dep_abbr}
                )

            # Specialty case required for Faculties which are also departments:
            if fac_name == "School of Fashion and Textiles":
                fac_link = fac_header.css("a::attr(href)").get()
                print(f"     -> Dep Link: {self.sanitize_department_url(fac_link)}")
                fac_link = self.sanitize_department_url(fac_link)
                dep_abbr = self.get_department_abbreviation(fac_link)

                yield scrapy.Request(
                    url=fac_link,
                    callback=self.scrape_department_courses,
                    meta={'department_name': dep_url, 'department_abbr': dep_abbr}
                )

    def scrape_department_courses(self, response):
        pass
    
    def scrape_single_course(self, response, course_url):
        pass


    """ LOCAL METHODS """
    # [LM #1]
    def sanitize_department_url(self, dep_url) -> str:
        parsed_url = urlparse(dep_url)

        if not parsed_url.netloc or "polyu.edu.hk" not in parsed_url.netloc:
            return urljoin("https://www.polyu.edu.hk/", dep_url.lstrip("/"))

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_url
    
    def get_department_abbreviation(self, dep_url) -> str:
        abbreviation = dep_url.rstrip("/").split("/")[-1]
        if abbreviation == "lms": abbreviation = "lgt"
        return abbreviation

    # [LM #2]
    def search_for_course_urls(self, response, dep_url):
        query_string_url = (f"{dep_url}/search-result/?query=Subject+Description+Form")

    
    # [LM #3]
    def scrape_course_from_department_subject_list(self, driver, department) -> (list[str] | SubjectListFormatType | bool):
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