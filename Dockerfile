# 使用 Python 3.12.3 作為基礎映像
FROM python:3.12.3

# 設定工作目錄
WORKDIR /app

# 複製需求文件並安裝套件
COPY . .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY main.py .

# 執行程式
CMD ["python", "main.py"]
