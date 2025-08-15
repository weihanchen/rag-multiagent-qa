import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    """系統配置類 - 專注於 Ollama 本地模型"""
    
    # Ollama 本地模型配置 - 自動檢測Docker環境
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")
    
    # 向量資料庫配置
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    
    # 系統配置
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # 超時配置
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "180.0"))  # 請求超時時間（秒）
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "180.0"))          # LLM 響應超時時間（秒）
    QUERY_TIMEOUT = float(os.getenv("QUERY_TIMEOUT", "180.0"))      # 查詢引擎超時時間（秒）
    
    # 代理配置
    ENABLE_HUMAN_INPUT = os.getenv("ENABLE_HUMAN_INPUT", "false").lower() == "true"
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    
    # 文件處理配置
    SUPPORTED_FORMATS = [".pdf", ".md", ".txt"]
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate(cls):
        """驗證配置"""
        # 檢查 Ollama 服務是否可用
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ValueError(f"無法連接到 Ollama 服務: {cls.OLLAMA_BASE_URL}")
        except Exception as e:
            raise ValueError(f"Ollama 服務連接失敗: {str(e)}")
        
        if cls.VECTOR_STORE_TYPE not in ["faiss", "chroma"]:
            raise ValueError("VECTOR_STORE_TYPE 必須是 'faiss' 或 'chroma'")
        
        return True
    
    @classmethod
    def get_llm_config(cls):
        """返回 Ollama LLM 配置"""
        return {
            "config_list": [{
                "model": cls.OLLAMA_MODEL,
                "base_url": cls.OLLAMA_BASE_URL,
                "api_key": "ollama",  # 本地服務無需真實 API key
                "timeout": cls.LLM_TIMEOUT
            }],
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "timeout": cls.LLM_TIMEOUT
        }
    
    @classmethod
    def get_embedding_config(cls):
        """返回 Ollama 嵌入模型配置"""
        return {
            "model": cls.OLLAMA_MODEL,
            "base_url": cls.OLLAMA_BASE_URL,
            "timeout": cls.REQUEST_TIMEOUT
        }
