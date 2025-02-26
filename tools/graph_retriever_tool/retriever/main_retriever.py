from ..indexer import Indexer
from .subretriever.rerank_retriever import RerankRetriever
import os

class Retriever:
    def __init__(self, indexer:Indexer):
        self.indexer = indexer
        self.custom_sub_retriever = RerankRetriever(
        indexer.environment.get_graph_store(),
        include_text=True,
        cohere_api_key=os.getenv('COHERE_API_KEY'),
    )

    def get_response(self, query:str) -> str:
        query_engine = self.indexer.get_index().as_query_engine(include_text=True, 
        #sub_retrievers=[self.custom_sub_retriever]
        )
        response = query_engine.query(query)
        print(str(response))

        return str(response)

    def retrieve(self, query:str)->list:
        retriever = self.indexer.get_index().as_retriever(
        include_text=False,
        #sub_retrievers=[self.custom_sub_retriever]
        )
        nodes = retriever.retrieve(query)

        return nodes