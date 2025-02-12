from agno.agent import Agent
from tools.file_tools_v2 import FileToolsV2
from agno.models.openai import OpenAIChat

class FileAgent:
    def __init__(self):
        self.agent = Agent(
            name="File Agent",
            role="with given infomation, helping for creating, reading, and saving files in docx(word file) and pdf formats",
            model=OpenAIChat(id="gpt-4o"),
            instructions=[
            "You are responsible for creating, reading, and saving files in txt, docx and pdf formats.",
            "When creating files:",
            "- Use the format parameter to specify the file type",
            "Example:",
            "- Correct: file_name='report', format='pdf' -> 'report.pdf'", 
            "- Incorrect: file_name='report.pdf', format='pdf' -> 'report.pdf.pdf'",
            "The supported formats are: txt, docx, and pdf."
        ],
            tools=[FileToolsV2()],
        )

    def ask(self, prompt: str):
        streaming_response = self.agent.run(
            prompt,
            stream=True
        )

        for text in streaming_response:
            yield text.content