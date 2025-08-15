import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
import json

class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""
    
    # ANSI 顏色代碼
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 綠色
        'WARNING': '\033[33m',    # 黃色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加顏色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # 格式化日誌訊息
        formatted = super().format(record)
        
        # 為錯誤和警告添加額外的視覺提示
        if record.levelno >= logging.ERROR:
            formatted = f"🚨 {formatted}"
        elif record.levelno >= logging.WARNING:
            formatted = f"⚠️  {formatted}"
        elif record.levelno >= logging.INFO:
            formatted = f"ℹ️  {formatted}"
        else:
            formatted = f"🔍 {formatted}"
            
        return formatted

class JSONFormatter(logging.Formatter):
    """JSON 格式日誌格式化器，用於結構化日誌"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'process_id': record.process,
            'thread_id': record.thread
        }
        
        # 添加異常信息
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 添加額外字段
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logger(
    name: str = None,
    level: str = "INFO",
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
    json_format: bool = False
) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌文件路徑
        max_bytes: 單個日誌文件最大大小
        backup_count: 保留的備份文件數量
        console_output: 是否輸出到控制台
        json_format: 是否使用JSON格式
    
    Returns:
        配置好的日誌記錄器
    """
    
    # 創建日誌記錄器
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重複添加處理器
    if logger.handlers:
        return logger
    
    # 控制台處理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # 文件處理器
    if log_file:
        # 確保日誌目錄存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 RotatingFileHandler 進行日誌輪轉
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    獲取已配置的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
    
    Returns:
        日誌記錄器實例
    """
    return logging.getLogger(name or __name__)

# 預設日誌配置
def setup_default_logging():
    """設置預設日誌配置"""
    
    # 從環境變數獲取配置
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'data/logs/app.log')
    json_format = os.getenv('LOG_JSON_FORMAT', 'false').lower() == 'true'
    
    # 設置根日誌記錄器
    root_logger = setup_logger(
        name='root',
        level=log_level,
        log_file=log_file,
        json_format=json_format
    )
    
    # 設置第三方庫的日誌級別
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('streamlit').setLevel(logging.WARNING)
    
    return root_logger

# 便捷的日誌記錄函數
def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    帶上下文的日誌記錄
    
    Args:
        logger: 日誌記錄器
        level: 日誌級別
        message: 日誌訊息
        **kwargs: 額外的上下文信息
    """
    extra_fields = {'extra_fields': kwargs}
    
    if level.upper() == 'DEBUG':
        logger.debug(message, extra=extra_fields)
    elif level.upper() == 'INFO':
        logger.info(message, extra=extra_fields)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra_fields)
    elif level.upper() == 'ERROR':
        logger.error(message, extra=extra_fields)
    elif level.upper() == 'CRITICAL':
        logger.critical(message, extra=extra_fields)

# 如果直接運行此模組，設置預設日誌配置
if __name__ == "__main__":
    setup_default_logging()
    logger = get_logger(__name__)
    
    logger.debug("這是一條調試訊息")
    logger.info("這是一條信息訊息")
    logger.warning("這是一條警告訊息")
    logger.error("這是一條錯誤訊息")
    logger.critical("這是一條嚴重錯誤訊息")
    
    # 測試帶上下文的日誌
    log_with_context(
        logger, 
        'INFO', 
        '用戶登入成功', 
        user_id='12345', 
        ip_address='192.168.1.1'
    )

# 自動初始化日誌配置
# 當模組被導入時，自動設置預設日誌配置
try:
    # 檢查是否已經設置過根日誌記錄器
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        setup_default_logging()
        print("✅ 日誌系統已自動初始化")
except Exception as e:
    print(f"⚠️ 自動初始化日誌系統時發生錯誤: {e}")
