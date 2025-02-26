from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
import shutil
import os
from .environment import Environment
from llama_index.llms.openai import OpenAI
from agno.utils.log import logger

class Indexer:
    def __init__(self):
        load_dotenv()
        self.environment = Environment() 
        self.llm:str = os.getenv('OPENAI_LLM')
        self.embedding_model:str = os.getenv('OPENAI_EMBEDDING_MODEL')

        return
    
    def create_index(self, file_path: str):
        """
        針對單一檔案建立索引，並將處理完成的檔案移動至 processed 資料夾。
        :param file_path: 檔案的完整路徑
        """
        if not os.path.exists(file_path):
            logger.error(f"檔案不存在: {file_path}")
            return
        try:
            # 讀取單個檔案
            document = SimpleDirectoryReader(input_files=[file_path]).load_data()
            if not document:
                logger.warning(f"無法讀取文件: {file_path}")
                return
            
            # 建立索引
            index = PropertyGraphIndex.from_documents(
                documents=document,
                embed_model=OpenAIEmbedding(model_name=self.embedding_model),
                kg_extractors=[
                    SimpleLLMPathExtractor(
                        llm=OpenAI(model=self.llm, temperature=0.0)
                    )
                ],
                property_graph_store=self.environment.get_graph_store(),
                show_progress=True,
            )
            logger.debug(f"graph 處理文件 {file_path} 成功")
        
        except Exception as e:
            logger.error(f"處理文件 {file_path} 時發生錯誤: {e}")
    
    def get_index(self):
        index = PropertyGraphIndex.from_existing(
        property_graph_store=self.environment.get_graph_store(),
        llm=OpenAI(model=self.llm, temperature=0.3),
        embed_model=OpenAIEmbedding(model_name=self.embedding_model),
        )

        return index
    
if __name__ == "__main__":
    indexer = Indexer()
    indexer.create_index(data_dir="./etl/graphstore/data/documents_before_process")


    