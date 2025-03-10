from openai import OpenAI
from sqlalchemy.types import DateTime
from sqlalchemy import create_engine, text
from sqlalchemy import Column, MetaData, select, String, Table, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import asyncio
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from .meta import Meta
from .vectorstore import Vectorstore  


load_dotenv()

# 取得資料庫帳密
username = os.getenv("POSTGRE_USERNAME")
password = os.getenv("POSTGRE_PASSWORD")

class Postgresql(Vectorstore):
    def __init__(self):
        super().__init__()
        
    def _get_sync_engine(self):
        return create_engine(f'postgresql+psycopg2://{username}:{password}@localhost/agno_knowledge')
    
    def _get_async_engine(self):
        return create_async_engine(f'postgresql+asyncpg://{username}:{password}@localhost/agno_knowledge', echo=True)

    def _generate_embedding(self, text_input):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            input=[text_input]
        )
        return response.data[0].embedding
    
    async def _agenerate_embedding(self, text_input):
        response = await asyncio.to_thread(
            self.client.embeddings.create,
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            input=[text_input]
        )
        return response.data[0].embedding


        

