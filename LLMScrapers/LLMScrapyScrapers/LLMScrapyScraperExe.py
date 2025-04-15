# OpenAI Tuning Job: ftjob-2R7NqA5q1CtvTizLnUmjKruD
# VertexAI API Key: groningencrawler

# API Imports:
from scrapy.crawler import CrawlerProcess

# Local Imports:
from LLMScrapers.LLMScrapyScrapers.LLMKUCrawler.LLMScrapyKUCrawler import LLMKUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMGronigenCrawler.LLMScrapyGroningen import LLMGroningenCrawler
from LLMScrapers.LLMScrapyScrapers.LLMDTUCrawler.LLMScrapyDTUCrawler import LLMDTUCrawler
from LLMScrapers.LLMScrapyScrapers.LLMSelfRepairing.LLMSelfRepairingScraper import LLMSelfRepairingScraper
from Infrastructure.ScrapyInfrastructure.LLMScrapyAbstractCrawler import LLMType

# TEMP! #
from openai import OpenAI, OpenAIError
import openai
from google import genai
from google.genai.types import CreateTuningJobConfig, TuningExample, TuningDataset, CreateBatchJobConfig, JobState, HttpOptions
from dotenv import load_dotenv
import os
import time
from pathlib import Path
import json

load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(vertexai=True, project='groningencrawler', location='us-central1')

def llm_scrapy_scraper_executor():
    process = CrawlerProcess({
        # [] Logging:
        'LOG_LEVEL': 'ERROR', # INFO, ERROR, CRITICAL, DEBUG

        # [] ...:
        # 'FEEDS': {
        #      'dtu_gemini.json': {'format': 'json', 'overwrite': True, 'encoding': 'utf-8'},
        # },

        # Pipeline Configuration:
        'ITEM_PIPELINES': {
            'Infrastructure.ScrapyInfrastructure.ScrapyDataPipeline.DataPipeline': 1
        },

        # Performance Optimization
        'CONCURRENT_ITEMS': 256,
        'CONCURRENT_REQUESTS': 64,                  # Increase concurrency
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,       # Balance load per domain
        'DOWNLOAD_DELAY': 0.0,                      # At "0.0" this may cause an overloader so 0.25 would be safer
        
        # AutoThrottle (Adaptive Speed Control)
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 1,
        # 'AUTOTHROTTLE_MAX_DELAY': 5,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 10,

        # Middleware Optimizations
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
        },

        # Cache (Optional for even faster scraping if data is static)
        # 'HTTPCACHE_ENABLED': True,
        # 'HTTPCACHE_EXPIRATION_SECS': 86400,  # Cache for 1 day
        # 'HTTPCACHE_DIR': 'httpcache',
    })

    """ Self Repairing """
    process.crawl(LLMSelfRepairingScraper, "Self Repairing Scraper", LLMType.CHAT_GPT)
    process.start()

    """ Data Accuracy - KU """
    # process.crawl(LLMKUCrawler, _name="København Universitet", _url="https://kurser.ku.dk/", _llm_type=LLMType.CHAT_GPT)
    # process.start()

    """ Data Accuracy - DTU """
    # process.crawl(LLMDTUCrawler, _name="Danmarks Tekniske Universitet", _url="https://kurser.dtu.dk/", _llm_type=LLMType.GEMINI)
    # process.start()

    """ Crawling Accuracy - Groningen """
    # process.crawl(LLMGroningenCrawler, _name="University of Groningen", _url="https://ocasys.rug.nl/api/faculty/catalog/2024-2025", _llm_type=LLMType.CHAT_GPT)
    # process.start()

    # response = gemini_client.models.generate_content(
    #     model='gemini-2.0-flash-001', contents='Why is the sky blue?'
    # )

    # print(response.text)

    # DELETE A FILE
    # try:
    #     res = gpt_client.files.delete(
    #         file_id="file-WSBrESNH7EwvV9B2drwBs4"
    #     )
    #     print(res)
    # except OpenAIError as e:
    #     print(e)

    # CREATE A NEW FILE
    # try: 
    #     res = gpt_client.files.create(
    #         file=Path("./LLMScrapers/LLMScrapyScrapers/LLMGronigenCrawler/OpenAIFTDataset.jsonl"),
    #         purpose="fine-tune"
    #     )
    #     print(res)
    # except OpenAIError as e:
    #     print(e)

    # CREATE A NEW TUNED MODEL:
    # try:
    #     # response = gpt_client.files.list()  
    #     # print(response)
    #     model = gpt_client.fine_tuning.jobs.create(
    #         model="gpt-3.5-turbo",
    #         training_file="file-2BkkkJEXV7kBXJVLWGoize",
    #         hyperparameters={
    #             "n_epochs": 5,
    #             "batch_size": 3,
    #             "learning_rate_multiplier": 0.3
    #         }
    #     )

    #     print(model.id)
    #     print(model.status)
    # except OpenAIError as e:
    #     print(f"Error occurred: {e}")


    # def check_fine_tuning_status():
    #     try:
    #         # Retrieve the list of fine-tuning jobs
    #         response = gpt_client.fine_tuning.jobs.list()
    #         print(f"!===================RESPONSE===================!\n\n{response}")
    #         print(f"\n!================================================================!")
    #     except OpenAIError as e:
    #         print(f"Error occurred: {e}")
        
    # check_fine_tuning_status()

        
    