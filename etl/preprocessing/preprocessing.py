import re
import os
import pandas as pd
import PyPDF2
from typing import List
import nltk
from nltk.tokenize import sent_tokenize
from datetime import datetime
from bs4 import BeautifulSoup

nltk.download('punkt_tab')

class Preprocessor:
    def __init__(self, max_chunk_length: int = 300):
        """
        文本預處理類別，包含清理、分塊（chunking）、與文件處理功能。

        :param max_chunk_length: 每個文本塊的最大長度
        """
        self.max_chunk_length = max_chunk_length

    def clean_text(self, text: str) -> str:
        text = BeautifulSoup(text, "html.parser").get_text()  # 移除 HTML 標籤
        text = re.sub(r"\s+", " ", text)  # 移除多餘空格
        text = re.sub(r"[^\w\s.,!?;:()\"'%-]", "", text)  # 保留更多標點符號
        text = re.sub(r"([.,!?;:()])([^\s])", r"\1 \2", text)  # 確保標點後有空格
        return text.strip()


    def chunk_text(self, text: str) -> List[str]:
        """
        按照單字數量（而非句子）進行切割，確保 metadata 保持一致。

        :param text: 原始文本
        :return: 以 `max_chunk_length` 為單位的文本列表
        """
        words = text.split()  # 直接按單字切割
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + 1 <= self.max_chunk_length:  # 每個單字間有空格，因此長度 +1
                current_chunk.append(word)
                current_length += 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = 1  # 重置長度計算（包含空格）

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks



    def extract_text_from_pdf(self, pdf_path: str) -> List[dict]:
        """
        從 PDF 提取純文本，並以 metadata 方式保留頁碼與檔案名稱。

        :param pdf_path: PDF 文件路徑
        :return: 包含檔案名稱、頁碼、文本的列表
        """
        text_data = []
        file_name = os.path.basename(pdf_path)

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_data.append({
                        "file_name": file_name,
                        "page_number": page_num,
                        "text": self.clean_text(page_text.strip())
                    })
        
        return text_data


    def extract_text_from_txt(self, txt_path: str) -> str:
        """
        從 TXT 文件中提取純文本

        :param txt_path: TXT 文件路徑
        :return: 提取的純文本
        """
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
        return self.clean_text(text)

    def preprocess_text(self, text: str) -> List[str]:
        """
        完整的文本預處理流程：
        1. 清理文本
        2. 分塊處理（Chunking）

        :param text: 原始文本
        :return: 清理和分塊後的文本列表
        """
        cleaned_text = self.clean_text(text)
        return self.chunk_text(cleaned_text)

    def preprocess_file(self, file_path: str, file_type: str) -> List[dict]:
        """
        處理不同類型的文件，並進行文本預處理，保留 metadata（檔案名稱、頁碼、時間戳）。

        :param file_path: 文件路徑
        :param file_type: 文件類型（'pdf', 'txt'）
        :return: 以 metadata 格式存儲的文本列表
        """
        file_name = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 產生當前時間戳

        if file_type == "pdf":
            raw_text_data = self.extract_text_from_pdf(file_path)
        elif file_type == "txt":
            raw_text = self.extract_text_from_txt(file_path)
            raw_text_data = [{"file_name": file_name, "page_number": None, "text": raw_text}]
        else:
            raise ValueError("不支持的文件類型，請選擇 'pdf', 'txt', 或 'csv'")

        # **處理文本分塊 (Chunking)**
        chunked_data = []
        for entry in raw_text_data:
            chunks = self.chunk_text(entry["text"])
            for chunk in chunks:
                chunked_data.append({
                    "file_name": entry["file_name"],
                    "page_number": entry["page_number"],  # PDF 才有頁碼，TXT & CSV 為 None
                    "timestamp": timestamp,  # 加入處理時的時間戳
                    "chunk_text": chunk
                })

        return chunked_data



if __name__ == "__main__":
    preprocessor = Preprocessor(max_chunk_length=30)
    pdf_path = "./etl/samples/sample.pdf"
    txt_path = "./etl/samples/sample.txt"

    if os.path.exists(pdf_path):
        pdf_chunks = preprocessor.preprocess_file(pdf_path, "pdf")
        print("PDF 分塊結果：")
        for chunk in pdf_chunks:
            print(chunk)
    else:
        print(f"文件 {pdf_path} 不存在，跳過測試。")

    if os.path.exists(txt_path):
        txt_chunks = preprocessor.preprocess_file(txt_path, "txt")
        print("TXT 分塊結果：")
        for chunk in txt_chunks:
            print(chunk)
    else:
        print(f"文件 {txt_path} 不存在，跳過測試。")
        
