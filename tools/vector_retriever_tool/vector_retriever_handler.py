import functools
import numpy as np
from openai import OpenAI
from sqlalchemy import create_engine, text
from agno.tools import Toolkit
from agno.utils.log import logger
import os

@functools.lru_cache(maxsize=None)
def warn() -> None:
    logger.warning("RetrieverTools allows querying and retrieving indexed data. Ensure proper query handling.")

class VectorRetrieverTools(Toolkit):
    def __init__(self):
        super().__init__(name="vector_retriever_tools")
        self.engine = create_engine(
            f'postgresql+psycopg2://{os.getenv("POSTGRE_USERNAME")}:{os.getenv("POSTGRE_PASSWORD")}@localhost/agno_knowledge'
        )
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
        self.register(self.retrieve_similar_content)
        
    def _generate_embedding(self, text_input):
        """ 生成文本的 OpenAI 嵌入，并转换为 `VECTOR(1536)` 兼容格式 """
        response = self.client.embeddings.create(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            input=[text_input]
        )
        embedding = np.array(response.data[0].embedding, dtype=np.float32).tolist()  # 确保为 `float32`
        return embedding

    def retrieve_similar_content(self, query, top_k=5, threshold=0):
        """ 通过向量相似度搜索检索最相近的内容，并返回 Cosine Similarity """
        query_embedding = self._generate_embedding(query)  # 获取查询向量
        
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT chunk_text, 
                        1 - (embedding <=> CAST(:query_embedding AS vector)) AS cosine_similarity
                    FROM chunks
                    WHERE (1 - (embedding <=> CAST(:query_embedding AS vector))) >= :threshold
                    ORDER BY cosine_similarity DESC
                    LIMIT :top_k
                """),
                {"query_embedding": query_embedding, "top_k": top_k, "threshold": threshold}  
            )
            
            returnvalue = ""
            for row in result:
                chunk_text, cosine_similarity = row
                returnvalue += f"文本: {chunk_text}\n相似度: {cosine_similarity:.4f}\n\n"
            
            return returnvalue if returnvalue else "没有找到符合相似度要求的内容。"

