from openai import OpenAI
import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json 

load_dotenv()

class Vectorstore:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    def _generate_embedding(self, text):
        raise NotImplementedError


    def store_embedding(self, doc):
        raise NotImplementedError


