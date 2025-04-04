# Scraping APIs:
import scrapy
from bs4 import BeautifulSoup

# LLM APIs:
from openai import OpenAI
from google import genai

class LLMSelfRepairingScraper(scrapy.Spider):
    name = "LLMSR_PolyU"
    start_urls = ["https://web.archive.org/web/20201001192436/https://www.polyu.edu.hk/en/education/faculties-schools-departments/", 
                  "https://web.archive.org/web/20241209031021/https://www.polyu.edu.hk/en/education/faculties-schools-departments/"]
    
    # gpt_client = OpenAI(api_key=OPEN_AI_KEY)
    # gemini_client = genai.Client(api_key=GEMINI_KEY)

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.scrape_departments, meta={'url_type': 'old'})
        #yield scrapy.Request(url=self.start_urls[1], callback=self.scrape_departments, meta={'url_type': 'new'})

    # [] The LLM is unable to directly take the raw HTML DOM tree as it is over the limited amount of tokens. 
    def scrape_departments(self, response):
        # []
        raw_html    = response.text
        parsed_html = BeautifulSoup(raw_html, "html.parser")

        # [] Retrieve the <a> URLs:
        urls = [a.get("href") for a in parsed_html.find_all("a") if a.get("href")]

        # [] Remove all the tags which are not 
        for tag in parsed_html.find_all(["script", "style", "iframe"]):
            tag.extract()

        # [] 
        for div in parsed_html.find_all("div"):
            if not div.get("class") and not div.get("id"):
                div.unwrap()

        # with open("./urls.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(urls))
        



    def call_llm(self, html):
        print("Calling LLM")
        gpt_client = OpenAI(api_key=OPEN_AI_KEY)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant skilled in HTML parsing.\n"
                    "You will be given raw HTML from a university page.\n"
                    "Your task is to extract the names of all academic departments.\n"
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
        
        try:
            department_list = eval(content) if content.startswith("[") else []
        except Exception as e:
            department_list = []
            print("Failed to parse LLM output:", e)
        

        print("Scraped Departments:", department_list)