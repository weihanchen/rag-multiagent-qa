import autogen
from typing import List, Dict, Any
import os
from pathlib import Path
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser
from config import Config
from logger_config import get_logger

class DataLoaderAgent:
    """數據載入代理 - 負責讀取和處理PDF/Markdown文件"""
    
    def __init__(self):
        self.config = Config()
        # 使用新的配置方法
        self.llm_config = self.config.get_llm_config()
        
        # 初始化日誌記錄器
        self.logger = get_logger(__name__)
        
        # 創建AutoGen代理
        self.agent = autogen.AssistantAgent(
            name="DataLoader",
            system_message="""你是一個專業的數據載入代理，負責：
            1. 讀取和解析PDF、Markdown和文本文件
            2. 將文件內容分割成適當的chunks
            3. 提取關鍵信息和元數據
            4. 準備數據以供向量化處理
            
            請確保數據的完整性和準確性。""",
            llm_config=self.llm_config
        )
    
    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """載入多個文件並返回Document對象列表"""
        documents = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                self.logger.warning(f"文件 {file_path} 不存在")
                continue
                
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.config.SUPPORTED_FORMATS:
                self.logger.warning(f"不支持的文件格式 {file_ext}")
                continue
            
            try:
                # 使用LlamaIndex讀取文件
                reader = SimpleDirectoryReader(input_files=[file_path])
                docs = reader.load_data()
                documents.extend(docs)
                self.logger.info(f"成功載入文件：{file_path}")
                
            except Exception as e:
                self.logger.error(f"載入文件 {file_path} 時發生錯誤：{str(e)}")
        
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """處理文檔並分割成chunks"""
        try:
            # 使用簡單節點解析器分割文檔
            parser = SimpleNodeParser.from_defaults(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            
            nodes = parser.get_nodes_from_documents(documents)
            
            # 轉換為字典格式
            processed_chunks = []
            for i, node in enumerate(nodes):
                chunk_data = {
                    "id": f"chunk_{i}",
                    "text": node.text,
                    "metadata": node.metadata,
                    "embedding": None  # 將在向量化時填充
                }
                processed_chunks.append(chunk_data)
            
            self.logger.info(f"成功處理 {len(documents)} 個文檔，生成 {len(processed_chunks)} 個chunks")
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"處理文檔時發生錯誤：{str(e)}")
            return []
    
    def get_agent(self):
        """返回AutoGen代理實例"""
        return self.agent
    
    def analyze_document_structure(self, file_path: str) -> Dict[str, Any]:
        """分析文檔結構和內容"""
        try:
            documents = self.load_documents([file_path])
            if not documents:
                return {"error": "無法載入文檔"}
            
            doc = documents[0]
            
            # 分析文檔結構
            analysis = {
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "text_length": len(doc.text),
                "metadata": doc.metadata,
                "estimated_chunks": len(doc.text) // self.config.CHUNK_SIZE + 1,
                "model_provider": "ollama",
                "chunk_size": self.config.CHUNK_SIZE,
                "chunk_overlap": self.config.CHUNK_OVERLAP
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"分析文檔時發生錯誤：{str(e)}"}
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計信息"""
        return {
            "supported_formats": self.config.SUPPORTED_FORMATS,
            "max_file_size": self.config.MAX_FILE_SIZE,
            "chunk_size": self.config.CHUNK_SIZE,
            "chunk_overlap": self.config.CHUNK_OVERLAP,
            "model_provider": "ollama"
        }
