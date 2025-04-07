# Scrapying APIs
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Native Python Packages:
from urllib.parse import urlparse, urljoin
import os
import re
import time

# .env Support:
from dotenv import load_dotenv

# Local Structs:
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO
from Infrastructure.ScrapyInfrastructure.ScrapyAbstractCrawler import ScrapyAbstractCrawler, LLMType

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

# TODO: Need an LLM orientated solution for these universities - not "comp" as it is a duplicate of "dsai"
EXCLUDE_DEPARTMENTS = {  "beee", "hti", "rs", "sn", "so", "cihk", "comp", "dsai" }

class LLMPolyUCrawler(ScrapyAbstractCrawler):
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

            # [] 
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

        # if-case necessary for Faculty-Department mix...

    def scrape_department_courses(self, response):
        dep_name = response.meta['department_name']
        dep_abbr = response.meta['department_abbr']
        
        # [] Parse the raw HTML and strip it down to the fundamental parts:
        raw_html          = response.text
        parsed_html       = BeautifulSoup(raw_html, "html.parser")
        header_links_raw  = self.strip_html_slu(parsed_html, dep_abbr)
        # header_links_json = json.dumps(header_links_raw, ensure_ascii=False, indent=4)
        
        # [] 
        core_message : str = f"""
        "You are a helpful web scraping assistant skilled in HTML parsing.\n"
        "You will be given raw HTML from a university department page.\n"
        "Your task is to locate a hyperlink pointing to that department's subject list.\n"
        "The link text may be phrased in a multitude of ways, most often it is a direct hyperlink named 'Subject List', 'Subject Syllabus', 'Subject Syllabi' or 'Course Info'.\n"
        "However, it may also be the case that it an <li> tag named 'Subject List' or 'Undergraduate Programmes' contains the target hyperlinks.\n"
        "In such a case, you should choose, 'CAR Subjects' or 'Undergraduate Programmes' as the returned hyperlink.\n"
        "Return only the URL (href) to the best match. No additional text.\n"
        "HTML:\n{header_links_raw}"
        """

        # [] 
        subject_list_link = self.call_llm(core_message)
        print(f"{dep_name} | {response.request.url}")
        print(f"   *= {subject_list_link}")

        # f = open("subject_list.html", "a", encoding="utf-8")
        # f.write(f"\n\n<!--{dep_name.upper()}-->\n{header_links_raw.prettify()}")
        # f.close()

    
    def scrape_single_course(self, response):
        return super().scrape_single_course(response)
    

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
    
    # [LM #2] TODO: This might be temporary...
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

    # [] TODO: Place this into a generalized LLM specific file:
    def call_llm(self, core_message):        
        match self.llm_type:
            case LLMType.CHAT_GPT:
                response = gpt_client.chat.completions.create(
                    model="gpt-4o-2024-08-06",                      
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