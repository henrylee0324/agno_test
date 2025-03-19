# 專案啟動指南

## 先決條件

請確保您的環境已安裝以下軟體：
- [Docker](https://www.docker.com/get-started)
- [Neo4j](https://neo4j.com/download/)
- Python 3.x（建議使用最新版）

## 啟動步驟

1. **開啟 Docker**
   - 確保 Docker 服務已啟動，若未啟動，請先開啟 Docker。

2. **啟動 Neo4j 資料庫**
   - 執行 `start-neo4j.bat` 來啟動 Neo4j 資料庫。
   - 確保 Neo4j 服務成功啟動後，才進行下一步。

3. **啟動虛擬環境**
   - 執行以下指令來啟動虛擬環境：
     ```sh
     env\Scripts\activate.bat
     ```
   - 確保虛擬環境已成功啟動，然後繼續下一步。

4. **執行主程式**
   - 使用以下指令執行 `main.py`：
     ```sh
     python main.py
     ```
   - 若有使用虛擬環境，請確保已正確啟動。


## 注意事項
- 確保 Neo4j 連線正常，並且正確設定了登入憑證（若有需要）。
- 若遇到 `ModuleNotFoundError`，請安裝相關的 Python 套件，例如：
  ```sh
  pip install -r requirements.txt
  ```
- 如有任何問題，請參考專案內的文件或聯繫開發團隊。
