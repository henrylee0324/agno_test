from agno.agent import Agent
from tools.email_tools_v2 import EmailToolsV2
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
import os


class EmailAgent:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_name = os.getenv("SENDER_NAME")
        self.sender_passkey = os.getenv("SENDER_PASSKEY")
        self.agent = Agent(
            name="Email Agent",
            role="Send an email with the given content",
            instructions = [
            "You are responsible for sending emails.",
            "When you receive a message:",
            "1. Look for email addresses in the message.",
            "2. Make the format of email addresses correct (like 'at' to '@', 'dot' to '.').",
            "3. If you find an email, use it as the receiver_email.",
            "4. When calling email_user, include the found email in the receiver_email parameter.",
            "5. If emailing is required, maintain a gentle and polite tone, and follow proper formatting guidelines.",
            "6. Ensure the email format is clear and professional.",
            "7. Always use zh_tw as the language for all communications.",
            "8. When drafting an email, adhere to proper email etiquette, including a polite salutation, clear content, and a courteous closing."
        ],
            tools=[
                EmailToolsV2(
                    sender_email=self.sender_email,
                    sender_name=self.sender_name,
                    sender_passkey=self.sender_passkey,
                )
            ]
        )