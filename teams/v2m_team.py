import os
from typing import List, Dict, Any
from agno.agent import Agent
from dotenv import load_dotenv
from agno.models.openai import OpenAIChat

load_dotenv()

class V2MTeam:
    def __init__(self, instructions: List[str], team: List[Agent]):
        self.instructions = instructions
        self.team = Agent(
            name="V2MTeam",
            team=team,
            model=OpenAIChat(id="gpt-4o", api_key=os.getenv('OPENAI_API_KEY')),
            instructions=self.instructions,
            show_tool_calls=True,
            markdown=True,
            debug_mode=True
        )
        
    def ask(self, prompt: str):
        streaming_response = self.team.run(
            prompt,
            stream=True
        )

        for text in streaming_response:
            yield text.content