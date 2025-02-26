from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor, SimpleLLMPathExtractor
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
    
    def create_index(self, data_dir: str = "./data/documents_before_process", processed_dir: str = "./data/processed_documents"):
        os.makedirs(processed_dir, exist_ok=True)
        
        documents:list = self._get_documents(data_dir)
        if len(documents) == 0:
            return 
        
        index = PropertyGraphIndex.from_documents(
            documents,
            embed_model=OpenAIEmbedding(model_name=self.embedding_model),
            kg_extractors=[
                SimpleLLMPathExtractor(
                    llm=OpenAI(model=self.llm, temperature=0.0)
                )
            ],
            property_graph_store=self.environment.get_graph_store(),
            show_progress=True,
        )
        
        # 處理完文件後，將它們移動到 processed_dir
        for file_name in os.listdir(data_dir):
            source_path = os.path.join(data_dir, file_name)
            destination_path = os.path.join(processed_dir, file_name)
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)
                print(f"Moved: {file_name} -> {processed_dir}")
        
        return index
    
    def get_index(self):
        index = PropertyGraphIndex.from_existing(
        property_graph_store=self.environment.get_graph_store(),
        llm=OpenAI(model=self.llm, temperature=0.3),
        embed_model=OpenAIEmbedding(model_name=self.embedding_model),
        )

        return index

    def _get_documents(self, data_dir:str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        files = os.listdir(data_dir)
        if not files:
            return []
        documents = SimpleDirectoryReader(self.data_dir).load_data()

        return documents
    
if __name__ == "__main__":
    indexer = Indexer()
    query = "川普想做什麼?"
    query_engine = indexer.get_index().as_query_engine(
    include_text=True, 
    #sub_retrievers=[self.custom_sub_retriever]
    )
    response = query_engine.query(query)
    print(str(response))

    