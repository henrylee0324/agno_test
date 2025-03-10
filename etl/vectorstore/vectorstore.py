from openai import OpenAI
from sqlalchemy import text
import os
from dotenv import load_dotenv
from datetime import datetime
from .meta import Meta

load_dotenv()

# 取得資料庫帳密
username = os.getenv("POSTGRE_USERNAME")
password = os.getenv("POSTGRE_PASSWORD")

class Vectorstore:
    def __init__(self):
        self.engine = self._get_sync_engine()
        self.async_engine = self._get_async_engine()
        self.conn = self.engine.connect()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.meta = Meta()
        
    def _get_sync_engine(self):
        raise NotImplementedError

    def _get_async_engine(self):
        raise NotImplementedError
    
    def _generate_embedding(self, text_input):
        raise NotImplementedError
    
    async def _agenerate_embedding(self, text_input):
        raise NotImplementedError

    def store_file(self, file_name):
        file_query = text("""
            INSERT INTO files (file_name)
            VALUES (:file_name)
            RETURNING file_id
        """)

        result = self.conn.execute(file_query, {"file_name": file_name})
        file_id = result.fetchone()[0]
        self.conn.commit()
        return file_id


    async def astore_file(self, file_name: str):
        async with self.async_engine.begin() as conn:
            result = await conn.execute(
                self.meta.file_table.insert().returning(self.meta.file_table.c.file_id),
                {"file_name": file_name,
                "created_at": datetime.now()
                }
            )
            file_id = result.fetchone()[0]
            return file_id


    def store_chunk(self, file_id, chunk_text, page_number=None, timestamp=None):
        embedding = self._generate_embedding(chunk_text)

        if timestamp is None:
            timestamp = datetime.now()

        chunk_query = text("""
            INSERT INTO chunks (file_id, page_number, timestamp, chunk_text, embedding)
            VALUES (:file_id, :page_number, :timestamp , :chunk_text, :embedding)
        """)

        self.conn.execute(chunk_query, {
            "file_id": file_id,
            "page_number": page_number,
            "timestamp": timestamp,
            "chunk_text": chunk_text,
            "embedding": embedding
        })
        self.conn.commit()


    async def astore_chunk(self, file_id, chunk_text, page_number=None, timestamp=None):
        if timestamp == None:
            timestamp = datetime.now()
        embedding = await self._agenerate_embedding(chunk_text)
        async with self.async_engine.begin() as conn:
            await conn.execute(
            self.meta.chunk_table.insert().returning(self.meta.chunk_table.c.chunk_id),{
                "file_id": file_id,
                "chunk_text": chunk_text,
                "page_number": page_number,
                "timestamp": datetime.now(),
                "embedding": embedding
            }
    )
