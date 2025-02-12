from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI
from google.cloud import speech
from agno.utils.log import logger
import os

class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, audio_file_path: str) -> str:
        pass

class WhisperTranscriptionService(TranscriptionService):
    """OpenAI Whisper 語音辨識服務"""
    def __init__(self):
        self.client = OpenAI()
    
    def transcribe(self, audio_file_path: str) -> str:
        logger.info("使用 OpenAI Whisper 進行語音辨識")
        with open(audio_file_path, "rb") as audio_file:
            return self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                temperature=0.1
            )

class GoogleTranscriptionService(TranscriptionService):
    """Google Speech-to-Text 語音辨識服務"""
    def __init__(self):
        self.client = speech.SpeechClient()
    
    def transcribe(self, audio_file_path: str) -> str:
        logger.info("使用 Google Speech-to-Text 進行語音辨識")
        # 讀取音檔
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()
        
        # 設定音訊檔案格式 (這裡假設是 wav 格式，實際使用時可能需要調整)
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="zh-TW",  # 可以根據需求調整語言
            sample_rate_hertz=16000,
        )
        
        # 進行辨識
        response = self.client.recognize(config=config, audio=audio)
        
        # 組合所有辨識結果
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        
        return transcript.strip()

class SpeechProcessor:
    def __init__(self, service: TranscriptionService):
        """
        初始化語音處理器
        :param service: 選擇要使用的語音辨識服務
        """
        self.service = service
    
    def set_service(self, service: TranscriptionService):
        """
        更換語音辨識服務
        :param service: 新的語音辨識服務
        """
        self.service = service
        logger.info(f"切換到新的語音辨識服務: {type(service).__name__}")
    
    def process_audio(self, audio_file_path: str) -> Optional[str]:
        """
        將語音檔案轉換為文字
        :param audio_file_path: 音檔路徑
        :return: 轉換後的文字，如果發生錯誤則返回 None
        """
        try:
            logger.info("即將開始處理語音檔案...")
            transcription = self.service.transcribe(audio_file_path)
            
            if not transcription:
                logger.warning("未取得轉換結果")
                return None
            
            logger.info(f"語音轉換結果: {transcription}")
            return transcription
            
        except FileNotFoundError:
            logger.error(f"找不到檔案: {audio_file_path}")
            return None
            
        except Exception as e:
            logger.error(f"語音處理錯誤: {e}")
            import traceback
            logger.debug(f"詳細錯誤: {traceback.format_exc()}")
            return None
