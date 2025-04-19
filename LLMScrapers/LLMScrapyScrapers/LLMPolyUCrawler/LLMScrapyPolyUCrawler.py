# Scraper APIs:
from bs4 import BeautifulSoup
import scrapy 

# Native Python Packages:
import re 
import requests
import os
import json
import time
import threading
import inspect
from enum import Enum
from urllib.parse import urlparse, unquote, urljoin

# Local Imports:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO, ScrapyErrorDTO
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMScrapyAbstractCrawler, LLMType

# Additional Imports:
import pymupdf

# LLM Imports:
from openai import OpenAI
from google import genai
from dotenv import load_dotenv

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp", "clc", "elc" }

class LLMPolyUCrawler(LLMScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    # [1] 
    def scrape_departments(self, response):
        faculty_containers = response.xpath("//*[contains(@class, 'ITS_Content_News_Highlight_Collection')]")

        for fac_container in faculty_containers:
            # [] Faculty Components:
            fac_header = fac_container.xpath(".//p[contains(@class, 'list-highlight__heading')]")
            fac_name   = fac_header.xpath(".//a//span[contains(@class, 'underline-link__line')]/text()").get().strip()

            # [] Department Components:
            dep_containers = fac_container.xpath(".//ul[contains(@class, 'border-link-list')]//li//a")

            # TODO: Remove this! Only for testing...
            if fac_name != "School of Hotel and Tourism Management": continue

            for dep_container in dep_containers:
                raw_url  = dep_container.xpath("./@href").get()
                dep_url  = self.sanitize_department_url(raw_url)
                dep_name = dep_container.xpath(".//span[contains(@class, 'underline-link__line')]/text()").get().strip()
                dep_abbr = self.get_department_abbreviation(dep_url)
                
                # dep_name != "School of Accounting and Finance" or 
                if dep_abbr in EXCLUDE_DEPARTMENTS : continue

                # [] Prior to each we will sleep in order to prevent a 429 Error - too many requests.
                time.sleep(1.5)
                yield scrapy.Request(
                    url=dep_url,
                    callback=self.scrape_department_courses,
                    meta={'department_name': dep_name, 'department_abbr': dep_abbr}
                )

            if fac_name in ["School of Fashion and Textiles", "School of Hotel and Tourism Management"]:
                fac_url  = fac_header.xpath(".//a/@href").get()
                fac_url  = self.sanitize_department_url(fac_url)
                fac_abbr = self.get_department_abbreviation(fac_url)

                print(f"Running for {fac_name}")

                time.sleep(1.5)
                yield scrapy.Request(
                    url=fac_url,
                    callback=self.scrape_department_subject_list,
                    meta={'department_name': fac_name, 'department_abbr': fac_abbr}
                )

    # [1.5] 
    def scrape_department_subject_list(self, response):
        department_name   = response.meta['department_name']
        department_abbr   = response.meta['department_abbr']

        subject_element   = None
        subject_link_href = None

        json_path = "./LLMScrapers/LLMScrapyScrapers/LLMPolyUCrawler/DepSubListXpath.json"

        # [] We load the JSON file and try to use the currently stored XPath. If we fail we will go further down
        #    to trigger the LLM call:
        try:
            with open(json_path, "r") as f:
                dep_subject_list_xpaths = json.load(f)

            xpath_query = dep_subject_list_xpaths.get(department_abbr)

            subject_element   = response.xpath(xpath_query).get()
            subject_link_href = response.xpath(xpath_query).attrib.get("href") if subject_element else None

        except ValueError as e:
            print(f"XPath failed with error: {e}")
            subject_element   = None
            subject_link_href = None

        # [] 
        if subject_link_href == None:
            # [] Parse the raw HTML and strip it down to the fundamental parts:
            raw_html          = response.text
            parsed_html       = BeautifulSoup(raw_html, "html.parser")
            header_links_raw  = self.truncate_html_sublist_url(parsed_html, department_abbr)
            file_lock = threading.Lock()
            
            # [] 
            core_message = f"""
            You are a helpful web scraping assistant skilled in HTML parsing and Scrapy XPath.

            ### GOAL
            Your task is to find the most appropriate XPath query that selects a hyperlink element (<a>) pointing to the department's subject list.

            ### INSTRUCTIONS
            - The hyperlink might be labeled with terms such as:
            - "Subject List", "Subject Syllabus", "Subject Syllabi", "Course Info", etc.
            - In some cases, these links may be nested inside <li> or other tags.
            - If there's no direct subject list, fallback options might include links like:
            - "CAR Subjects", "Undergraduate Programmes", or even "Programmes".
            - Return only the internal portion of the XPath query that selects this <a> tag.
            - Do **not** include `response.xpath(...)`, just the string inside the parentheses.
            - Do **not** return any extra text or explanation.

            ### EXAMPLE OUTPUT
            //a[contains(text(), "Subject List")]

            ### HTML INPUT
            {header_links_raw}
            """

            # [] Call the LLM and retrieve the subject list 'href' attribute
            llm_response      = self.call_llm(core_message)
            subject_element   = response.xpath(llm_response).get()
            subject_link_href = response.xpath(llm_response).attrib.get("href") if subject_element else None

            # TODO: Remove!
            print(f"{department_name} | {response.request.url}")
            print(f"   *= Raw LLM Res: {llm_response}")
            print(f"   *= Subject Link Href: {subject_link_href}")

            # [] Using thread locks we ensure that when we write the XPath to the file we dont' have read/write
            #    conflicts:
            with file_lock:
                with open(json_path, "r") as f:
                    dep_subject_list_xpaths = json.load(f)

                dep_subject_list_xpaths[department_abbr] = llm_response.strip()

                with open(json_path, "w") as f:
                    json.dump(dep_subject_list_xpaths, f, indent=2)

        # []
        if subject_link_href != None:
            department_url = (f"https://www.polyu.edu.hk/{subject_link_href}")

            print(f"Located Target URL: {department_url}")

            # TODO: Clean this up...
            # [] Thus far, the LLMs are incapable of diving deep down the URLs:
            if department_abbr == 'me':  (f"{department_url}subject-list/")
            if department_abbr == 'bre': (f"{department_url}2023-2024/")

            # [] Scrape the department courses:
            yield scrapy.Request(
                url=department_url,
                callback=self.scrape_department_courses,
                meta={'department_name': department_name, 'department_abbr': department_abbr, 'department_url': department_url}
            )

        else:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )

    # [2]  
    def scrape_department_courses(self, response):
        department_name   = response.meta['department_name']
        department_abbr   = response.meta['department_abbr']
        department_url    = response.meta['department_url' ]

        # [] Parse the department's SubList HTML
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")
        course_urls = self.get_subject_list_hrefs(parsed_html, department_abbr, response.request.url)

        for course_url in course_urls:
            print(f"Raw Course URL:       =* {course_url}")
            print(f"Sanitized Course URL: =* {self.sanitize_course_url(department_url, course_url)}")
            
            # yield scrapy.Request(
            #     url=course_url,
            #     callback=self.scrape_single_course,
            #     meta={'department_name': department_name}
            # )

    # [3] Scrape the Single Courses using LLMs to handle the literature:
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

            #! LLM Trigger:
            #TODO: Change this to use "call_llm" as opposed to the "clean_literature" which needs to be removed
            literature = self.clean_literature(literature)

            yield {
                'name': subject_title,
                'code': subject_code,
                'literature': literature,
                'department': department_name
            }

        except Exception as e:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )

    # [4]
    def call_llm(self, core_message):
        match self.llm_type:
            case LLMType.CHAT_GPT:
                response = gpt_client.chat.completions.create(
                    model="gpt-4-turbo",                      
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                core_message
                            )
                        }
                    ],
                    temperature=0,                                  # Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. 
                )

                content = response.choices[0].message.content.strip()
            
                return content
            
            case LLMType.GEMINI:
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=core_message,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': list[str], 
                    }
                    
                )

                return response.text
            
            case _: pass

    """ LOCAL METHODS """
    # [LM #1] Takes the department URL and reformats it if necessary. Some departments will write "https://www.DEP_ABBR.polyu.edu.hk/" or will only have the abbreviation
    #         however, it should be "https://www.polyu.edu.hk/DEP_ABBR/":
    def sanitize_department_url(self, dep_url) -> str:
        parsed_url = urlparse(dep_url)

        if not parsed_url.netloc or "polyu.edu.hk" not in parsed_url.netloc:
            return urljoin("https://www.polyu.edu.hk/", dep_url.lstrip("/"))

        if parsed_url.netloc.endswith("polyu.edu.hk") and parsed_url.netloc != "www.polyu.edu.hk":
            subdomain = parsed_url.netloc.split(".")[0]
            return f"https://www.polyu.edu.hk/{subdomain}/"
        
        return dep_url
    
    # [LM #2] Takes the course URL and makes sure that it is properly associated with the correct department as some
    #         departments will have courses from other departments, resulting in duplicates:
    def sanitize_course_url(self, dep_url, course_url) -> str:
        parsed_url = urlparse(course_url)

        if not parsed_url.netloc: 
            course_url = urljoin(dep_url, course_url)

        return course_url
    
    # [LM #2] Harvest the university abbreviation to be used for correct association between the course and department:
    def get_department_abbreviation(self, dep_url) -> str:
        abbreviation = dep_url.rstrip("/").split("/")[-1]
        if abbreviation == "lms": abbreviation = "lgt"
        return abbreviation
    
    # [LM #3] Used to confirm that the retrieved URL is a PDF file as that indicates it is a course
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
    
    # [LM #4] Used in conjunction with finding the "Subject List URL"
    #         We remove everything but the <header> tag and append it to a clean <body> tag
    def truncate_html_sublist_url(self, raw_html : BeautifulSoup, dep_abbr : str) -> BeautifulSoup:
        # [] Parsed the raw HTML:
        parsed_html = BeautifulSoup("<html><body></body></html>", "html.parser")
        body = parsed_html.body 

        # [] 
        nav = raw_html.find("nav", class_="mn__nav")
        if nav:
            ul = nav.find("ul", class_="mn__list--1")
            if ul:
                li_tags = ul.find_all("li", class_="mn__item--1 has-sub")
                if len(li_tags) >= 2:
                    # [] Unfortunately, a huge draw back to all of this is still the need to truncate the data. 
                    if dep_abbr == "cee":
                        second_li = li_tags[2]  
                        body.append(second_li)
                    elif dep_abbr == "sft":
                        third_li = li_tags[3]
                        body.append(third_li)
                    else:
                        second_li = li_tags[1] 
                        body.append(second_li)

        # [] Method to harvest all the <a> tags located in the <header>
        # for tag in header_tag:
            # for a in tag.find_all("a"):
            #     tag_href = a.get("href")
            #     tag_text = a.get_text(strip=True)

            #     if tag_href and tag_text:
            #         if tag_href == "javascript:void(0);": continue

            #         header_links.append({
            #             "aTagText": tag_text,
            #             "aTagHref": tag_href
            #         })

        return body
    
    # [LM #5] 
    #         This method is necessary because unfortunately, AI can't fix the raw html and the many flaws 
    def get_subject_list_hrefs(self, raw_html : BeautifulSoup, dep_abbr : str, dep_url : str) -> str:
        def get_dep_type(abbr : str) -> str:
            match abbr:
                # Faculty of Business:
                case "lgt" : return "pt"     # Pagination Table      :: Aggregate Data
                case "mm"  : return "tl"     # Table List            :: Retrieve Table
                case "af"  : return "pt"     # Pagination Table      :: Aggregate Data
                case "tls" : return "tls"    # Table List(s)         :: Retrieve all the Tables

                # Faculty of Computer and Mathematical Sciences:
                case "ama" : return "tls"    # Table List(s)         :: Retrieve all the Tables

                # Faculty of Construction and Environment:
                case "bre" : return "tl"     # Table List            :: Retrieve Table
                case "cee" : return "tls"    # Table List(s)         :: Retrieve all the Tables
                case "lsgi": return "tls"    # Table List(s)         :: Retrieve all the Tables

                # Faculty of Engineering:
                case "aae" : return "con"    # <a> tags              :: Retrieve <div class="container">
                case "bme" : return "tls"    # Table List(s)         :: Retrieve all the Tables
                case "eee" : return "con"    # <ul>/<li> tags        :: Retrieve <div class="container"> TODO: Might still be too much!
                case "ise" : return "con"    # <ul>/<li> tags        :: Retrieve <div class="container">
                case "me"  : return "tl"     # Table List            :: Retrieve Table 

                # Faculty of Health and Social Sciences:
                # NONE

                # Faculty of Humanities:
                case "chc" : return "tl"    # Table List            :: 
                case "cbs" : return "tl"    # Table List            :: TODO: Fix is required! Needs to travel deeper in. Make sure that no HTML is lost during truncation
                case "engl": return "con"   # <ul>/<li> tags        :: Retrieve <div class="container">
            
                # Faculty of Sciences:
                case "abct": return "tl"    # Table List            :: Retrieve Table
                case "ap"  : return "tl"    # Table List            :: Retrieve Table
                case "fsn" : return "tl"    # Table List            :: Retrieve Table

                # Fashion & Hotel:
                case "sft" : return "tl"    # Table List            :: Retrieve Table
                case "shtm": return "pt"    # Pagination Table      :: Aggregate Data

        dep_type = get_dep_type(dep_abbr)
        course_urls = []

        # [] 
        match dep_type:
            case "pt" : 
                # Originally this was Scrapy 
                num_pages_element = raw_html.select("li.pagination-list__itm.pagination-list__itm--number a")
                num_pages = int(num_pages_element[-1].get_text(strip=True))
                
                # [] For each of the pagination pages we 
                for page_num in range(1, num_pages + 1):
                    page_url     = (f"{dep_url}?&page={page_num}")
                    raw_html     = requests.get(page_url)
                    parsed_html  = BeautifulSoup(raw_html.text, 'html.parser')
                    page_courses = parsed_html.find_all("tr", attrs={"data-href": True})

                    # [] Extend the list with the scraped courses from this paginated iteration:
                    course_urls.extend(tr["data-href"] for tr in page_courses)
            
            case "tl" : 
                raw_html     = requests.get(dep_url)
                parsed_html  = BeautifulSoup(raw_html.text, 'html.parser')
                page_courses = parsed_html.find_all("tr", attrs={"data-href": True})
                
                # [] Extend the list with the scraped courses from this paginated iteration:
                course_urls.extend(tr["data-href"] for tr in page_courses)
            
            case "tls": 
                raw_html     = requests.get(dep_url)
                parsed_html  = BeautifulSoup(raw_html.text, 'html.parser')
                page_courses = parsed_html.find_all("tr", attrs={"data-href": True})

                # [] Extend the list with the scraped courses from this paginated iteration:
                course_urls.extend(tr["data-href"] for tr in page_courses)
                
            case "con": 
                raw_html     = requests.get(dep_url)
                parsed_html  = BeautifulSoup(raw_html.text, 'html.parser')
                page_courses = parsed_html.find("container")
                
                return ""
            
            case _: return None
            
        return course_urls