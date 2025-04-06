# Locate Departments Target URLS:
# ... ::
# ... ::

# Locate Subject List Department - AMA:
# 2001  :: https://web.archive.org/web/20010503071107/https://www.polyu.edu.hk/ama/ 
# 2008  :: https://web.archive.org/web/20080510141326/https://www.polyu.edu.hk/ama/
# 2015  :: https://web.archive.org/web/20150731063353/https://www.polyu.edu.hk/ama/
# 2025  :: https://web.archive.org/web/20250212043112/https://www.polyu.edu.hk/ama/ 

# Locate Subject List Department - AAE
# 2017  :: https://web.archive.org/web/20170822011903/https://www.polyu.edu.hk/aae/ 
# 2025  :: https://web.archive.org/web/20250320012220/https://www.polyu.edu.hk/aae/ 

# Locate Subject List Department - AP
# 2004  :: https://web.archive.org/web/20040905000428/http://ap.polyu.edu.hk/ 
# 2015  :: https://web.archive.org/web/20150701000000*/https://www.polyu.edu.hk/ap/
# 2025  :: https://web.archive.org/web/20250122172728/https://www.polyu.edu.hk/ap/ 


# Scraping APIs:
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Additionals:
from dotenv import load_dotenv
import os

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(api_key=gemini_key)

# The focus of this class is to determine whether the LLM is able to adjust its pathing
class LLMSelfRepairingScraper(scrapy.Spider):
    """ SR on 'old' and 'new' front page """
    name = "LLMSR_PolyU"
    start_urls = ["https://web.archive.org/web/20201001192436/https://www.polyu.edu.hk/en/education/faculties-schools-departments/", 
                  "https://web.archive.org/web/20241209031021/https://www.polyu.edu.hk/en/education/faculties-schools-departments/"]

    def start_requests(self):
        # Scrape for the departments:
        # yield scrapy.Request(url=self.start_urls[0], callback=self.scrape_departments, meta={'url_type': 'old'})
        # yield scrapy.Request(url=self.start_urls[1], callback=self.scrape_departments, meta={'url_type': 'new'})

        # Applied Physics (AP) URLs
        ap_dept_urls = [
            # AP department through the years
            #{"dept": "AP", "year": 2004, "url": "https://web.archive.org/web/20040905000428/http://ap.polyu.edu.hk/"},
            {"dept": "AP", "year": 2015, "url": "https://web.archive.org/web/20150701000000/https://www.polyu.edu.hk/ap/"},
            #{"dept": "AP", "year": 2025, "url": "https://web.archive.org/web/20250122172728/https://www.polyu.edu.hk/ap/"},
        ]

        for entry in ap_dept_urls:
            yield scrapy.Request(
                url=entry["url"],
                callback=self.locate_subject_list,
                meta={"dept": entry["dept"], "year": entry["year"]}
            )

    # [] The LLM is unable to directly take the raw HTML DOM tree as it is over the limited amount of tokens. 
    def scrape_departments(self, response):
        # [] Use BS to parse HTML:
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")
        clean_html  = self.strip_html_dep(parsed_html)


        # "Return only a JSON array of objects. Each object must have two keys: 'name' and 'href'.\n"
        # "Do not include markdown, code blocks, or any explanation — just valid JSON."
        
        # [] Locate departments prompt:
        scrape_departments_messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant skilled in HTML parsing.\n"
                    "You will be given raw HTML from a university webpage.\n"
                    "Your task is to extract the name and associated 'href' attribute of each academic department.\n"
                    "Return only a Python list of dictionaries, where each dictionary has two keys: 'name' and 'href'.\n"
                    "No extra explanation, no formatting, no commentary — just the list."
                )
            },
            {
                "role": "user",
                "content": f"HTML:\n{clean_html}\n\nReturn the department data as a Python list of dictionaries."
            }
        ]

        departments = self.call_llm(scrape_departments_messages)

        print(f"{departments}")


    #####################################
    #   TEST 02: LOCATE SUBJECT LIST    #
    #####################################
    def locate_subject_list(self, response):
        dept = response.meta["dept"]
        year = response.meta["year"]

        print(f"\n Scanning {dept} ({year}) page for subject list...")

        # [] Use BS to parse raw HTML:
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")
        clean_html  = self.strip_html_sl(parsed_html)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant skilled in HTML parsing.\n"
                    "You will be given raw HTML from a university department page.\n"
                    "Your task is to locate a hyperlink pointing to the department's subject list or syllabus.\n"
                    "The link text might include terms like 'Subject List', 'Subject Syllabus', 'Subject Syllabi', etc.\n"
                    "Additionally, the target link may be further embedded inside an <li> tag also be further embedded inside an additional tag like an <li>. If so, choose the'Bachelor Programme'.\n"
                    "Finally, if unable to locate any subject list it would always be better to return a link re-directing to 'Programmes'.\n"
                    "Return only the URL (href) to the best match.\n"
                )
            },
            {
                "role": "user",
                "content": f"HTML:\n{clean_html}\n\nReturn only the href of the best matching subject list link, or 'None'."
            }
        ]

        # [] Call LLM:
        subject_link = self.call_llm(messages)
        # f = open("subject_list.html", "w")
        # f.write(clean_html.prettify())
        # f.close()

        print(f"  RESULTS =* {response.request.url}{subject_link}")

    # [] 
    def call_llm(self, messages):        
        response = gpt_client.chat.completions.create(
            model="gpt-4o-2024-08-06",                      # Model variant
            messages=messages,                              # Messages
            temperature=0,                                  # Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. 
        )

        content = response.choices[0].message.content.strip()
    
        return content
    

    """ HTML STRIPPING """
    # [] Function to reduce the HTML tags when locating the subject lists:
    def strip_html_sl(self, raw_html : BeautifulSoup):
        kept_tags = []

        # [] 
        for tag_name in ["header", "table"]:
            kept_tags.extend(raw_html.find_all(tag_name))

        print(f"Number of kept tags: {len(tag_name)}")

        # [] Create a new BeautifulSoup doc from the selected tags only:
        stripped_html = BeautifulSoup("<html><body></body></html>", "html.parser")
        body = stripped_html.body

        # [] Append the <header> and or <table> tags to this new raw document:
        for tag in kept_tags:
            body.append(tag)

        return stripped_html
    
    # [] Function to reduce the HTML tags when locating the departments:
    def strip_html_dep(self, raw_html : BeautifulSoup):
        # [] Remove all the none essential tags:
        for tag in raw_html.find_all(["script", "style", "iframe", "link", "meta"]):
            tag.extract()

        # [] Remove any <div> tags which 'bloat' the HTML DOM:
        for div in raw_html.find_all("div"):
            if not div.get("class") and not div.get("id"):
                div.unwrap()

        return raw_html
    

    """ URL HARVESTING """
    def get_url_and_text(self, raw_html : BeautifulSoup):
        # [] Retrieve the <a> URLs:
        urls = []
        for a in raw_html.find_all("a"):
            tag_href = a.get("href")
            tag_text = a.get_text(strip=True)

            if tag_href and tag_text:
                urls.append((f"{tag_text} | {tag_href}"))

        return urls