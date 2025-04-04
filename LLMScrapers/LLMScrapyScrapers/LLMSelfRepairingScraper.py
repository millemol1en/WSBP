# Scraping APIs:
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

# Python APIs:
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
        yield scrapy.Request(url=self.start_urls[0], callback=self.scrape_departments, meta={'url_type': 'old'})
        #yield scrapy.Request(url=self.start_urls[1], callback=self.scrape_departments, meta={'url_type': 'new'})

    # [] The LLM is unable to directly take the raw HTML DOM tree as it is over the limited amount of tokens. 
    def scrape_departments(self, response):
        # [] 
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")

        stripped_html = self.strip_html(parsed_html)

        self.call_llm(stripped_html)
        
    # [] Function to reduce the HTML tags an HTML DOM to just the essential
    #    Necessary to reduce the token count when prompting with GPT
    def strip_html(self, raw_html : BeautifulSoup):
        # [] Remove all the none essential tags:
        for tag in raw_html.find_all(["script", "style", "iframe", "link", "meta"]):
            tag.extract()

        # [] Remove any <div> tags which 'bloat' the HTML DOM:
        for div in raw_html.find_all("div"):
            if not div.get("class") and not div.get("id"):
                div.unwrap()

        return raw_html
    

    def get_url_and_text(self, raw_html : BeautifulSoup):
        # [] Retrieve the <a> URLs:
        urls = []
        for a in raw_html.find_all("a"):
            tag_href = a.get("href")
            tag_text = a.get_text(strip=True)

            if tag_href and tag_text:
                urls.append((f"{tag_text} | {tag_href}"))

        return urls

        # with open("./urls.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(urls))

    def call_llm(self, html):        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant skilled in HTML parsing.\n"
                    "You will be given raw HTML from a university page.\n"
                    "Your task is to extract the names AND the associated 'href' attribute value, for all academic departments.\n"
                    "Return only a Python list of department names as strings. No explanations."
                )
            },
            {
                "role": "user",
                "content": f"HTML:\n{html}\n\nReturn ONLY a Python list of department names."
            }
        ]

        response = gpt_client.chat.completions.create(
            model="gpt-4o-2024-08-06",                      # Model variant
            messages=messages,                              # Messages
            temperature=0,                                  # Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. 
        )

        content = response.choices[0].message.content.strip()
    
        print("Scraped Departments:", content)


    """ Self-repairing on specific departments """