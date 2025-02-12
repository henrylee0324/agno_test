from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

class WebAgent:
    def __init__(self):
        self.agent = Agent(
            name="Web Searcher",
            role="Get seach queries on a topic",
            instructions=[
                "You are responsible for searching the web.",
                "When you receive a message:",
                "1. Look for the main topic in the message",
                "2. The source of the information(link) should be attached",
                "3. Provide the user with the most relevant information",
            ],
            tools=[DuckDuckGoTools()],
        )

    def ask(self, prompt: str):
        streaming_response = self.agent.run(
            prompt,
            stream=True
        )

        for text in streaming_response:
            yield text.content