import os 
from dotenv import load_dotenv
import yaml
from pyprojroot import here
import shutil
from openai import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
import chromadb


print("Environment variables loaded from .env file", load_dotenv())

class LoadConfig:
    def __init__(self)-> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)