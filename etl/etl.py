from preprocessing.preprocessing import Preprocessor
from vectorstore.postgresql import Postgresql
import os

class ETL:
    def __init__(self, max_chunk_length=300):
        """
        ETL 流程: 讀取文件 -> 清理與切割文本 -> 存入 PostgreSQL
        :param max_chunk_length: 每個文本塊的最大長度，預設為 300
        """
        self.preprocessor = Preprocessor(max_chunk_length=max_chunk_length)
        self.vectorstore = Postgresql()

    def process_and_store(self, file_path: str, file_type: str, column: str = None):
        """
        執行完整的 ETL 流程，將處理後的文本存入資料庫。
        
        :param file_path: 要處理的文件路徑
        :param file_type: 文件類型 ('pdf', 'txt', 'csv')
        :param column: 若文件類型為 'csv'，需指定欄位名稱
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        
        # 執行文本預處理 (提取 -> 清理 -> 分塊)
        chunked_data = self.preprocessor.preprocess_file(file_path, file_type, column)
        
        # 儲存文本至 PostgreSQL
        for chunk in chunked_data:
            self.vectorstore.store_chunk(
                file_name=chunk['file_name'],
                chunk_text=chunk['chunk_text'],
                page_number=chunk['page_number'],
                timestamp=chunk['timestamp']
            )
        
        print(f"{file_path} 處理完成，共存入 {len(chunked_data)} 個文本塊！")

if __name__ == "__main__":
    etl_pipeline = ETL(max_chunk_length=100)  # 設定 chunk 長度為 100
    
    sample_pdf = "./etl/samples/sample.pdf"
    sample_txt = "./etl/samples/sample.txt"
    sample_csv = "./etl/samples/sample.csv"
    
    # 執行 ETL 流程 (可依據需求選擇文件類型)
    for file_path, file_type, column in [(sample_pdf, "pdf", None), (sample_txt, "txt", None), (sample_csv, "csv", "text_column")]:
        try:
            etl_pipeline.process_and_store(file_path, file_type, column)
        except Exception as e:
            print(f"處理 {file_path} 時發生錯誤: {e}")
