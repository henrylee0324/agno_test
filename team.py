from textwrap import dedent
from teams import V2MTeam
from agents import WebAgent, YfinanceAgent, FileAgent, GraphRetrieverAgent, VectorRetrieverAgent
from datetime import datetime

from agno.utils.log import logger
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app


web_agent = WebAgent()
yfinance_agent=YfinanceAgent()
file_agent = FileAgent()
graph_retriever_agent = GraphRetrieverAgent()
vector_retriever_agent = VectorRetrieverAgent()

def initv2m():
    return V2MTeam(
    team=[file_agent.agent, web_agent.agent, graph_retriever_agent.agent],
    instructions = [
    "Today's date is " + datetime.now().strftime("%Y-%m-%d"),
    "You are a Leader of other sub-agent(s), responsible for understanding the user’s request in detail and determining which Agent(s) are needed based on the request’s nature and complexity.",
    "Think step by step to ensure you gather any relevant information before deciding on the best approach.",
    "After identifying the required Agent(s), use them to fulfill the user’s request carefully and accurately.",
    "If you discover that certain details are missing or unclear, ask the user for clarification.",
    "After the task is finished, provide a clear confirmation to the user that the task is complete.",
    "Use zh_tw for all communications unless the user explicitly requests another language.",
    "If you need to confirm or clarify anything, do so while remaining sensitive to the user’s needs and context.",
    "Follow lawful or safe interpretations if the user’s query could have both legal and illegal aspects, and always strive to help with the user’s request in a responsible way.",
    "Remain aware of the current date and include the current date in your communications only when relevant.",
    "If any part of the user’s request requires external or missing information, rely on the chosen Agent(s) to obtain it in a secure and appropriate manner.",
]
    )
v2m_team = initv2m()

app = Playground(agents=[graph_retriever_agent.agent, vector_retriever_agent.agent , yfinance_agent.agent, web_agent.agent, v2m_team.team]).get_app()




if __name__ == "__main__":
    serve_playground_app('team:app')


