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

EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp" }

class LLMPolyUCrawler(LLMScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", _llm_type=LLMType.NULL_AI, **kwargs):
        super().__init__(_name=_name, _url=_url, _llm_type=_llm_type, **kwargs)

    def parse(self, response):
        yield from self.scrape_departments(response)

    def scrape_departments(self, response):
        faculty_containers = response.xpath("//*[contains(@class, 'ITS_Content_News_Highlight_Collection')]")

        for fac_container in faculty_containers:
            # [] Faculty Components:
            fac_header = fac_container.xpath(".//p[contains(@class, 'list-highlight__heading')]")
            fac_name   = fac_header.xpath(".//a//span[contains(@class, 'underline-link__line')]/text()").get().strip()

            # [] Department Components:
            dep_containers = fac_container.xpath(".//ul[contains(@class, 'border-link-list')]//li//a")

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

    def scrape_department_courses(self, response):
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
            header_links_raw  = self.strip_html_slu(parsed_html, department_abbr)
            file_lock = threading.Lock()
            
            # [] 
            # 
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

            # [] 
            llm_response      = self.call_llm(core_message)
            subject_element   = response.xpath(llm_response).get()
            subject_link_href = response.xpath(llm_response).attrib.get("href") if subject_element else None

            print(f"{department_name} | {response.request.url}")
            print(f"   *= Raw LLM Res: {llm_response}")
            print(f"   *= Subject Link Href: {subject_link_href}")

            with file_lock:
                with open(json_path, "r") as f:
                    dep_subject_list_xpaths = json.load(f)

                dep_subject_list_xpaths[department_abbr] = llm_response.strip()

                with open(json_path, "w") as f:
                    json.dump(dep_subject_list_xpaths, f, indent=2)

        if subject_link_href != None:

            department_url = f"https://www.polyu.edu.hk/{subject_link_href}"

            yield scrapy.Request(
                url=department_url,
                callback=self.scrape_department_courses,
                meta={'department_name': department_name, 'department_abbr': department_abbr}
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

            #! LLM Trigger:
            literature = self.clean_literature(literature)
            print(f"      -> Literature: {literature}\n -||- \n")
            yield {
                'name': subject_title,
                'code': subject_code,
                'literature': literature,
                'department': department_name
            }

        except Exception:
            return

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
    
    # [LM #2] ...
    def get_department_abbreviation(self, dep_url) -> str:
        abbreviation = dep_url.rstrip("/").split("/")[-1]
        if abbreviation == "lms": abbreviation = "lgt"
        return abbreviation


    # [LM #3] Used in conjunction with finding the "Subject List URL"
    #         We remove everything but the <header> tag and append it to a clean <body> tag
    def strip_html_slu(self, raw_html : BeautifulSoup, dep_abbr : str) -> BeautifulSoup:
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
                    # [] Department of Civil Environmental Engineering wanted to be really quirky and put it in the
                    #    3rd <li> tag rather than the 2nd like everyone else. Nice.
                    if dep_abbr == "cee":
                        second_li = li_tags[2]  
                        body.append(second_li)
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
    
    # [LM #4] Used to confirm that the retrieved URL is a PDF file as that indicates it is a course
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