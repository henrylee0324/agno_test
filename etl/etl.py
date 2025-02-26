from preprocessing.preprocessing import Preprocessor
from vectorstore.postgresql import Postgresql
from graphstore.indexer import Indexer
import os

class ETL:
    def __init__(self, max_chunk_length=300):
        """
        ETL 流程: 讀取文件 -> 清理與切割文本 -> 存入 PostgreSQL
        :param max_chunk_length: 每個文本塊的最大長度，預設為 300
        """
        self.preprocessor = Preprocessor(max_chunk_length=max_chunk_length)
        self.vectorstore = Postgresql()
        self.graphstore_indexer = Indexer()
        

    def process_and_store(self, file_path: str, file_type: str, column: str = None):
        """
        執行完整的 ETL 流程，將處理後的文本存入資料庫。
        
        :param file_path: 要處理的文件路徑
        :param file_type: 文件類型 ('pdf', 'txt')
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        
        # 執行文本預處理 (提取 -> 清理 -> 分塊)
        chunked_data = self.preprocessor.preprocess_file(file_path, file_type)
        
        # 儲存文本至 PostgreSQL
        for chunk in chunked_data:
            self.vectorstore.store_chunk(
                file_name=chunk['file_name'],
                chunk_text=chunk['chunk_text'],
                page_number=chunk['page_number'],
                timestamp=chunk['timestamp']
            )
        
        print(f"{file_path} 處理完成，共存入 {len(chunked_data)} 個文本塊！")
        self.graphstore_indexer.create_index(file_path)

if __name__ == "__main__":
    etl_pipeline = ETL(max_chunk_length=100)  # 設定 chunk 長度為 100
    
    folder = "./etl/data/documents_before_process"
    
    # 確保資料夾存在
    if not os.path.exists(folder):
        print(f"資料夾 {folder} 不存在，請確認路徑")
    else:
        # 執行 ETL 流程 (可依據需求選擇文件類型)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path): 
                file_type = os.path.splitext(filename)[1].lower()[1:]  # 取得副檔名
                print(f"file_type: {file_type}")
                
                try:
                    etl_pipeline.process_and_store(file_path, file_type)
                except Exception as e:
                    print(f"處理 {file_path} 時發生錯誤: {e}")
