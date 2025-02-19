#import streamlit as st
from textwrap import dedent
from teams import V2MTeam
from agents import WebAgent, YfinanceAgent, FileAgent, RetrieverAgent
from tools import SpeechProcessor
from tools.speech_processor import WhisperTranscriptionService, GoogleTranscriptionService
from datetime import datetime

from agno.utils.log import logger
from agno.models.openai import OpenAIChat

web_agent = WebAgent()
yfinance_agent=YfinanceAgent()
file_agent = FileAgent()
retriever_agent = RetrieverAgent()
speech_processor = SpeechProcessor(WhisperTranscriptionService())


def initv2m():
    return V2MTeam(
    team=[retriever_agent.agent],
    instructions = [
    "Today’s date is " + datetime.now().strftime("%Y-%m-%d"),
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
if __name__ == "__main__":
    # audio_file_path = r"C:\Users\User\Desktop\CathayAgent_prototype\test.mp3"
    # #text_prompt = speech_processor.process_audio(audio_file_path)
    # if text_prompt:
    #     text_prompt = text_prompt
    # else:
    text_prompt = """
    寄送:
    1. 本週新聞摘要
    2. 台積電收盤價
    3. 做成pdf檔
    """
    text_prompt_2 = " 有多少人或組織跟川普之間有利害關係?請給我清單。"

    #print(text_prompt)
    v2m_team = initv2m()
    response_text = ""
    for response in v2m_team.ask(text_prompt_2):
        response_text += response  # 拼接片段
    print(response_text.strip())  # 去除多餘空格

