import autogen
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from config import Config
from .data_loader_agent import DataLoaderAgent
from .qa_agent import QAAgent
from logger_config import get_logger

class MultiAgentManager:
    """多代理協作管理器 - 協調DataLoader和QA代理的工作"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        # 初始化日誌記錄器
        self.logger = get_logger(__name__)
        
        # 初始化代理
        self.data_loader_agent = DataLoaderAgent()
        self.qa_agent = QAAgent(self.config.VECTOR_STORE_PATH)
        
        # 創建用戶代理
        self.user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "workspace"},
            llm_config=False
        )
        
        # 創建群聊
        self.groupchat = autogen.GroupChat(
            agents=[
                self.user_proxy,
                self.data_loader_agent.get_agent(),
                self.qa_agent.get_agent()
            ],
            messages=[],
            max_round=50
        )
        
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.data_loader_agent.llm_config
        )
    
    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """處理文檔並建立向量索引"""
        try:
            self.logger.info(f"開始處理 {len(file_paths)} 個文檔")
            
            # 使用DataLoader代理處理文檔
            documents = self.data_loader_agent.load_documents(file_paths)
            if not documents:
                return {"success": False, "error": "沒有成功載入的文檔"}
            
            # 處理文檔並分割成chunks
            chunks = self.data_loader_agent.process_documents(documents)
            if not chunks:
                return {"success": False, "error": "文檔處理失敗"}
            
            # 使用QA代理創建向量索引
            self.qa_agent.create_index_from_chunks(chunks)
            
            return {
                "success": True,
                "documents_processed": len(documents),
                "chunks_created": len(chunks),
                "vector_index_created": True,
                "model_provider": "ollama"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"處理文檔時發生錯誤：{str(e)}"
            }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """向系統提問"""
        try:
            if not self.qa_agent.query_engine:
                return {
                    "success": False,
                    "error": "查詢引擎未初始化，請先處理文檔"
                }
            
            # 使用QA代理回答問題
            answer = self.qa_agent.query(question)
            
            # 如果QA代理返回成功，則包裝結果
            if answer.get("success", False):
                return {
                    "success": True,
                    "question": question,
                    "answer": answer.get("answer", ""),
                    "source_nodes": answer.get("source_nodes", []),
                    "model_provider": "ollama"
                }
            else:
                return answer  # 直接返回錯誤信息
            
        except Exception as e:
            return {
                "success": False,
                "error": f"回答問題時發生錯誤：{str(e)}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            return {
                "config": {
                    "model_provider": "ollama",
                    "model_name": self.config.OLLAMA_MODEL,
                    "vector_store_type": self.config.VECTOR_STORE_TYPE,
                    "vector_store_path": self.config.VECTOR_STORE_PATH,
                    "chunk_size": self.config.CHUNK_SIZE,
                    "max_tokens": self.config.MAX_TOKENS
                },
                "agents": {
                    "data_loader": "已初始化",
                    "qa_agent": "已初始化",
                    "user_proxy": "已初始化"
                },
                "vector_index": self.qa_agent.get_index_info(),
                "supported_formats": self.config.SUPPORTED_FORMATS,
                "processing_stats": self.data_loader_agent.get_processing_stats()
            }
        except Exception as e:
            return {
                "error": f"獲取系統狀態時發生錯誤：{str(e)}"
            }
    
    def reset_system(self):
        """重置系統狀態"""
        try:
            # 清除向量索引
            if os.path.exists(self.config.VECTOR_STORE_PATH):
                import shutil
                shutil.rmtree(self.config.VECTOR_STORE_PATH)
                self.logger.info("向量索引已清除")
            
            # 重新初始化QA代理
            self.qa_agent = QAAgent(self.config.VECTOR_STORE_PATH)
            
            self.logger.info("系統已重置")
            
        except Exception as e:
            self.logger.error(f"重置系統時發生錯誤：{str(e)}")
    
    def get_agent_conversation_history(self) -> List[Dict[str, Any]]:
        """獲取代理對話歷史"""
        try:
            return self.groupchat.messages
        except Exception as e:
            self.logger.error(f"獲取對話歷史時發生錯誤：{str(e)}")
            return []
    
    def test_model_connection(self) -> Dict[str, Any]:
        """測試 Ollama 模型連接"""
        try:
            # 測試 Ollama 連接
            import requests
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "success",
                    "provider": "ollama",
                    "base_url": self.config.OLLAMA_BASE_URL,
                    "available_models": [model["name"] for model in models],
                    "response": "連接測試成功"
                }
            else:
                return {
                    "status": "error",
                    "provider": "ollama",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
        except Exception as e:
            return {
                "status": "error",
                "provider": "ollama",
                "error": str(e)
            }
