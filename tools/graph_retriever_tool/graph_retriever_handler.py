import functools
from pathlib import Path
from typing import Optional, List

from agno.tools import Toolkit
from agno.utils.log import logger
from .indexer import Indexer
from .retriever.subretriever.rerank_retriever import RerankRetriever
import os

@functools.lru_cache(maxsize=None)
def warn() -> None:
    logger.warning("RetrieverTools allows querying and retrieving indexed data. Ensure proper query handling.")

class GraphRetrieverTools(Toolkit):
    def __init__(
        self,
        use_rerank: bool = False  # 是否啟用 RerankRetriever
    ):
        super().__init__(name="retriever_tools")
        self.indexer = Indexer()
        self.use_rerank = use_rerank

        if self.use_rerank:
            self.rerank_retriever = RerankRetriever(
                self.indexer.environment.get_graph_store(),
                include_text=True,
                cohere_api_key=os.getenv('COHERE_API_KEY'),
            )
        else:
            self.rerank_retriever = None

        # 註冊工具
        self.register(self.retrieve_answer_tool)
        self.register(self.retrieve_nodes_tool)

    def retrieve_answer_tool(self, query: str) -> str:
        """
        根據查詢返回完整的回答。

        :param query: 用戶輸入的查詢字串。
        :return: 查詢結果的字串格式。
        """
        try:
            warn()
            logger.info(f"Retrieving answer for query: {query}")
            query_engine = self.indexer.get_index().as_query_engine(
                include_text=True,
                #sub_retrievers=[self.rerank_retriever] if self.use_rerank else []
            )

            response = query_engine.query(query)
            logger.info(f"關於用戶問題{query}，根據資料庫的回答為以下內容\n{str(response)}")
            return f"關於用戶問題{query}，根據資料庫的回答為以下內容\n{str(response)}"

        except Exception as e:
            logger.error(f"Error in retrieve_answer_tool: {e}")
            return f"Error retrieving answer: {str(e)}"

    def retrieve_nodes_tool(self, query: str) -> List[str]:
        """
        根據查詢返回多個檢索到的節點。

        :param query: 用戶輸入的查詢字串。
        :return: 檢索到的節點列表。
        """
        try:
            warn()
            logger.info(f"Retrieving nodes for query: {query}")
            retriever = self.indexer.get_index().as_retriever(
                include_text=False,
                #sub_retrievers=[self.rerank_retriever] if self.use_rerank else []
            )

            nodes = retriever.retrieve(query)
            logger.info(f"{[str(node) for node in nodes]}")
            return str([str(node) for node in nodes]) # 轉換成字串列表返回

        except Exception as e:
            logger.error(f"Error in retrieve_nodes_tool: {e}")
            return [f"Error retrieving nodes: {str(e)}"]
        
