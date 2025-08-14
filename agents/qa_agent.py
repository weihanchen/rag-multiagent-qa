import autogen
from typing import List, Dict, Any, Optional
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from config import Config

class QAAgent:
    """問答代理 - 負責處理用戶問題並從文檔中檢索答案"""
    
    def __init__(self, vector_store_path: str):
        self.config = Config()
        self.vector_store_path = vector_store_path
        
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
            # 使用 Ollama 嵌入模型
            from llama_index.embeddings.base import BaseEmbedding
            import requests
            import numpy as np
            
            class OllamaEmbedding(BaseEmbedding):
                def __init__(self, model_name: str, base_url: str):
                    super().__init__()
                    self.model_name = model_name
                    self.base_url = base_url
                
                def _get_query_embedding(self, query: str) -> List[float]:
                    return self._get_text_embedding(query)
                
                def _get_text_embedding(self, text: str) -> List[float]:
                    try:
                        response = requests.post(
                            f"{self.base_url}/api/embeddings",
                            json={"model": self.model_name, "prompt": text}
                        )
                        if response.status_code == 200:
                            return response.json()["embedding"]
                        else:
                            # 如果嵌入失敗，返回隨機向量作為備用
                            print(f"警告：Ollama 嵌入失敗，使用備用向量")
                            return list(np.random.rand(384))  # 384維向量
                    except Exception as e:
                        print(f"嵌入請求失敗：{str(e)}，使用備用向量")
                        return list(np.random.rand(384))
            
            embed_model = OllamaEmbedding(
                model_name=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL
            )
            
            # 創建服務上下文
            service_context = ServiceContext.from_defaults(
                embed_model=embed_model,
                chunk_size=self.config.CHUNK_SIZE
            )
            
            # 嘗試載入現有的向量索引
            try:
                self.index = VectorStoreIndex.load(
                    self.vector_store_path,
                    service_context=service_context
                )
                print("成功載入現有向量索引")
            except:
                print("未找到現有向量索引，將在處理文檔後創建")
                self.index = None
            
            if self.index:
                self._setup_query_engine()
                
        except Exception as e:
            print(f"初始化向量存儲時發生錯誤：{str(e)}")
    
    def _setup_query_engine(self):
        """設置查詢引擎"""
        try:
            # 創建檢索器
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=5  # 檢索前5個最相關的chunks
            )
            
            # 創建查詢引擎
            self.query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                service_context=self.index.service_context
            )
            
            print("查詢引擎設置完成")
            
        except Exception as e:
            print(f"設置查詢引擎時發生錯誤：{str(e)}")
    
    def create_index_from_chunks(self, chunks: List[Dict[str, Any]]):
        """從處理後的chunks創建向量索引"""
        try:
            from llama_index import Document
            
            # 轉換為Document對象
            documents = []
            for chunk in chunks:
                doc = Document(
                    text=chunk["text"],
                    metadata=chunk["metadata"]
                )
                documents.append(doc)
            
            # 創建向量索引
            from llama_index.embeddings.base import BaseEmbedding
            import requests
            import numpy as np
            
            class OllamaEmbedding(BaseEmbedding):
                def __init__(self, model_name: str, base_url: str):
                    super().__init__()
                    self.model_name = model_name
                    self.base_url = base_url
                
                def _get_query_embedding(self, query: str) -> List[float]:
                    return self._get_text_embedding(query)
                
                def _get_text_embedding(self, text: str) -> List[float]:
                    try:
                        response = requests.post(
                            f"{self.base_url}/api/embeddings",
                            json={"model": self.model_name, "prompt": text}
                        )
                        if response.status_code == 200:
                            return response.json()["embedding"]
                        else:
                            print(f"警告：Ollama 嵌入失敗，使用備用向量")
                            return list(np.random.rand(384))
                    except Exception as e:
                        print(f"嵌入請求失敗：{str(e)}，使用備用向量")
                        return list(np.random.rand(384))
            
            embed_model = OllamaEmbedding(
                model_name=self.config.OLLAMA_MODEL,
                base_url=self.config.OLLAMA_BASE_URL
            )
            
            service_context = ServiceContext.from_defaults(
                embed_model=embed_model,
                chunk_size=self.config.CHUNK_SIZE
            )
            
            self.index = VectorStoreIndex.from_documents(
                documents,
                service_context=service_context
            )
            
            # 保存索引
            self.index.storage_context.persist(persist_dir=self.vector_store_path)
            print(f"成功創建並保存向量索引到 {self.vector_store_path}")
            
            # 設置查詢引擎
            self._setup_query_engine()
            
        except Exception as e:
            print(f"創建向量索引時發生錯誤：{str(e)}")
            raise e
    
    def query(self, question: str) -> Dict[str, Any]:
        """查詢問題並返回答案"""
        try:
            if not self.query_engine:
                return {
                    "error": "查詢引擎未初始化，請先處理文檔"
                }
            
            # 使用查詢引擎獲取答案
            response = self.query_engine.query(question)
            
            return {
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
            return {
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
