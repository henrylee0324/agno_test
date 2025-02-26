from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools.graph_retriever_tool import GraphRetrieverTools

class GraphRetrieverAgent:
    def __init__(self):
        self.agent = Agent(
            name="Retriever Agent",
            role="Retrieve relevant data from the neo4j database according to the query",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are responsible for retrieving relevant data from the index according to the query.",
                "Please ensure the accuracy and relevance of the retrieved data.",
            ],
            tools=[GraphRetrieverTools(use_rerank=False)],  # 啟用 RerankRetriever 提升結果準確性
            show_tool_calls=True,
            debug_mode=True
        )

    def ask(self, prompt: str):
        """
        處理用戶的查詢並逐步回傳結果。
        
        :param prompt: 用戶輸入的查詢
        :return: 逐步產生的回應
        """
        streaming_response = self.agent.run(
            prompt,
            stream=True
        )

        for text in streaming_response:
            yield text.content
