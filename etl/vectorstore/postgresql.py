from openai import OpenAI
import psycopg2
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from .vectorstore import Vectorstore  

load_dotenv()

class Postgresql(Vectorstore):
    def __init__(self):
        self.engine = create_engine(
            f'postgresql+psycopg2://{os.getenv("POSTGRE_USERNAME")}:{os.getenv("POSTGRE_PASSWORD")}@localhost/agno_knowledge'
        )
        self.conn = self.engine.connect()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
        super().__init__()

    def _generate_embedding(self, text_input):
        response = self.client.embeddings.create(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            input=[text_input]
        )
        return response.data[0].embedding

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

    def store_chunk(self, file_name, chunk_text, page_number=None, timestamp=None):
        """ 存储文本块到 chunks 表，并存储嵌入 """
        file_id = self.store_file(file_name)  # 每次创建一个新的 file_id
        embedding = self._generate_embedding(chunk_text)
        embedding_json = json.dumps(embedding)  # 转换为 JSON 格式存储

        if timestamp is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        chunk_query = text("""
            INSERT INTO chunks (file_id, page_number, timestamp, chunk_text, embedding)
            VALUES (:file_id, :page_number, :timestamp, :chunk_text, :embedding)
        """)

        self.conn.execute(chunk_query, {
            "file_id": file_id,
            "page_number": page_number,
            "timestamp": timestamp,
            "chunk_text": chunk_text,
            "embedding": embedding_json
        })

        self.conn.commit()


if __name__ == "__main__":
    vectorstore = Postgresql()

    data = {
        'file_name': 'sample.txt',
        'page_number': None,
        'timestamp': '2025-02-24 16:46:02',
        'chunk_text': 'Au Pair 生活變得更加愉快與充實最重要的是保持開放心態珍 惜這次難得的國際交流機會讓自己在這趟旅程中成長茁壯'
    }

    vectorstore.store_chunk(
        file_name=data['file_name'],
        chunk_text=data['chunk_text'],
        page_number=data.get('page_number'),
        timestamp=data.get('timestamp')
    )

    print("文件和文本块已成功存入数据库，每次存入相同的 file_name 也会创建新的 file_id！")
