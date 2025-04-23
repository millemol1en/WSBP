# LLM APIs:
from openai import OpenAI, OpenAIError
import openai
from google import genai
from google.genai.types import CreateTuningJobConfig, TuningExample, TuningDataset, CreateBatchJobConfig, JobState, HttpOptions
from dotenv import load_dotenv

# Native Python Imports:
import os
import time
from pathlib import Path
import json

# Load in the LLM environment variables using LLM API keys:
load_dotenv()
gpt_key         = os.getenv("OPENAI_API_KEY") 
gemini_key      = os.getenv("GEMINI_API_KEY")
gpt_client      = OpenAI(api_key=gpt_key)
gemini_client   = genai.Client(vertexai=True, project='groningencrawler', location='us-central1')

class LLMFineTuning:
    """ OPENAI FUNCTIONS """
    @staticmethod
    def delete_openai_file(file_id : str):
        try:
            res = gpt_client.files.delete(
                file_id=file_id
            )
            print(res)
        except OpenAIError as e:
            print(e)

    @staticmethod
    def upload_openai_file(file_path : str):
        try: 
            res = gpt_client.files.create(
                file=Path(file_path),
                purpose="fine-tune"
            )
            print(res)
        except OpenAIError as e:
            print(e)

    @staticmethod
    def locally_validate_jsonl_file(file_path : str) -> bool:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Line {i} is invalid: {e}")
                    return False
            return True
        
    @staticmethod
    def create_tuned_model(file_id : str):
        try:
            model = gpt_client.fine_tuning.jobs.create(
                model="gpt-3.5-turbo",
                training_file=file_id,
                hyperparameters={
                    "n_epochs": 5,
                    "batch_size": 3,
                    "learning_rate_multiplier": 0.3
                }
            )

            print(model.id)
            print(model.status)
        except OpenAIError as e:
            print(f"Error occurred: {e}")

    @staticmethod
    def print_openai_model_info():
        models = openai.models.list()
        for model in models.data:
            print(f"ID: {model.id} | Owned by: {model.owned_by}")

    @staticmethod
    def print_openai_file_info():
        files = gpt_client.files.list()  
        for file in files.data:
            print(f"Filename    : {file.filename}")
            print(f"ID          : {file.id}")
            print(f"Status      : {file.status}")
            print(f"Purpose     : {file.purpose}")
            print(f"Expires At  : {file.expires_at}")
            print("-" * 40)

    """ GEMINI / VERTEX FUNCTIONS """
    