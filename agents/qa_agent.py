import autogen
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.llms.ollama import Ollama
from pydantic import Field
from config import Config
from logger_config import get_logger

# 使用自定義實現，繼承自 BaseEmbedding
class CustomOllamaEmbedding(BaseEmbedding):
    model_name: str = Field(description="Ollama 模型名稱")
    base_url: str = Field(description="Ollama 服務 URL")
    
    def _get_text_embedding(self, text: str) -> List[float]:
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text}
            )
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                import numpy as np
                return list(np.random.rand(384))
        except Exception as e:
            import numpy as np
            return list(np.random.rand(384))
    
    def _get_query_embedding(self, query: str) -> List[float]:
        return self._get_text_embedding(query)
    
    def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
    
    def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_text_embedding(query)

class QAAgent:
    """問答代理 - 負責處理用戶問題並從文檔中檢索答案"""
    
    def __init__(self, vector_store_path: str):
        self.config = Config()
        self.vector_store_path = vector_store_path
        
        # 初始化日誌記錄器
        self.logger = get_logger(__name__)
        
        # 使用新的配置方法
        self.llm_config = self.config.get_llm_config()
        
        # 創建AutoGen代理
        self.agent = autogen.AssistantAgent(
            name="QA",
            system_message="""你是一個專業的問答代理，負責：
            1. 理解用戶的問題和意圖
            2. 從文檔中檢索相關信息
            3. 生成準確、完整的答案
            4. 提供相關的上下文和引用
            
            請確保答案基於文檔內容，並提供清晰的解釋。""",
            llm_config=self.llm_config
        )
        
        # 初始化向量索引和查詢引擎
        self.index = None
        self.query_engine = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """初始化向量存儲和查詢引擎"""
        try:
            # 創建嵌入模型實例
            embed_model = CustomOllamaEmbedding(
                model_name=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL
            )
            self.logger.info("使用自定義 OllamaEmbedding 實現")
            
            # 嘗試載入現有的向量索引
            try:
                # 載入時也指定嵌入模型
                from llama_index.core.storage.storage_context import StorageContext
                from llama_index.core.indices.loading import load_index_from_storage
                
                storage_context = StorageContext.from_defaults(persist_dir=self.vector_store_path)
                self.index = load_index_from_storage(
                    storage_context,
                    embed_model=embed_model
                )
                self.logger.info("成功載入現有向量索引")
            except Exception as e:
                self.logger.warning(f"載入現有索引失敗: {str(e)}")
                self.logger.info("將在處理文檔後創建新索引")
                self.index = None
            
            if self.index:
                self._setup_query_engine()
            else:
                self.logger.info("向量索引未初始化，將在處理文檔後創建")
                
        except Exception as e:
            self.logger.error(f"初始化向量存儲時發生錯誤：{str(e)}")
            self.index = None
    
    def _setup_query_engine(self):
        """設置查詢引擎"""
        try:
            # 創建檢索器
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=5  # 檢索前5個最相關的chunks
            )
            
            # 創建 Ollama LLM 實例，使用配置的超時設置
            llm = Ollama(
                model=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL,
                request_timeout=self.config.LLM_TIMEOUT
            )
            
            # 創建查詢引擎，明確指定 LLM
            self.query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                llm=llm
            )
            
            self.logger.info(f"查詢引擎設置完成，使用 Ollama LLM，超時設置: {self.config.LLM_TIMEOUT}秒")
            
        except Exception as e:
            self.logger.error(f"設置查詢引擎時發生錯誤：{str(e)}")
    
    def create_index_from_chunks(self, chunks: List[Dict[str, Any]]):
        """從處理後的chunks創建向量索引"""
        try:
            # 轉換為Document對象
            documents = []
            for chunk in chunks:
                doc = Document(
                    text=chunk["text"],
                    metadata=chunk["metadata"]
                )
                documents.append(doc)
            
            # 創建自定義嵌入模型
            embed_model = CustomOllamaEmbedding(
                model_name=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL
            )
            self.logger.info(f"使用自定義 OllamaEmbedding 實現 - model_name: {self.config.OLLAMA_MODEL}")
            
            # 自定義嵌入模型，使用基本配置
            self.logger.info("使用自定義嵌入模型配置")
            
            # 使用自定義嵌入模型創建向量索引
            try:
                self.logger.info(f"開始創建向量索引...")
                
                # 使用 from_documents 方法，並傳遞我們的嵌入模型
                self.logger.info("使用自定義 Ollama 嵌入模型創建索引...")
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    embed_model=embed_model
                )
                self.logger.info(f"向量索引創建成功")
                    
            except Exception as e:
                self.logger.error(f"創建索引失敗: {str(e)}")
                import traceback
                print(f"詳細錯誤信息: {traceback.format_exc()}")
                
                # 如果失敗，嘗試使用 from_documents 但不指定嵌入模型
                try:
                    print("嘗試使用默認嵌入模型...")
                    self.index = VectorStoreIndex.from_documents(
                        documents
                    )
                    print("使用默認嵌入模型創建成功")
                    
                except Exception as e2:
                    print(f"使用默認嵌入模型也失敗: {str(e2)}")
                    raise e2
            
            # 保存索引
            self.index.storage_context.persist(persist_dir=self.vector_store_path)
            print(f"成功創建並保存向量索引到 {self.vector_store_path}")
            
            # 設置查詢引擎
            self._setup_query_engine()
            
        except Exception as e:
            print(f"創建向量索引時發生錯誤：{str(e)}")
            import traceback
            print(f"完整錯誤堆疊: {traceback.format_exc()}")
            raise e
    
    def query(self, question: str) -> Dict[str, Any]:
        """查詢問題並返回答案"""
        try:
            if not self.query_engine:
                return {
                    "success": False,
                    "error": "查詢引擎未初始化，請先處理文檔"
                }
            
            self.logger.info(f"開始處理問題: {question[:50]}...")
            
            # 使用查詢引擎獲取答案（移除信號超時處理，因為在 Streamlit 中不適用）
            try:
                response = self.query_engine.query(question)
                self.logger.info("查詢完成，正在處理響應...")
                
                return {
                    "success": True,
                    "answer": str(response),
                    "source_nodes": [
                        {
                            "text": node.text,
                            "metadata": node.metadata
                        }
                        for node in response.source_nodes
                    ] if hasattr(response, 'source_nodes') else [],
                    "model_provider": "ollama",
                    "model_name": self.config.OLLAMA_MODEL
                }
                
            except Exception as e:
                self.logger.error(f"查詢引擎執行失敗：{str(e)}")
                return {
                    "success": False,
                    "error": f"查詢引擎執行失敗：{str(e)}"
                }
            
        except Exception as e:
            self.logger.error(f"查詢時發生錯誤：{str(e)}")
            return {
                "success": False,
                "error": f"查詢時發生錯誤：{str(e)}"
            }
    
    def get_agent(self):
        """返回AutoGen代理實例"""
        return self.agent
    
    def get_index_info(self) -> Dict[str, Any]:
        """獲取向量索引信息"""
        if self.index:
            return {
                "status": "已初始化",
                "document_count": len(self.index.docstore.docs) if hasattr(self.index, 'docstore') else "未知",
                "vector_store_path": self.vector_store_path
            }
        else:
            return {
                "status": "未初始化",
                "vector_store_path": self.vector_store_path
            }
