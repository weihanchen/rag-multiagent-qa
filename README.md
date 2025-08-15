# RAG 多代理文件問答系統 - Docker 化部署版

這是一個基於AutoGen和LlamaIndex的智能文件問答系統，能夠處理PDF和Markdown文件，並通過多個AI代理進行智能問答。

## 特色功能

- 🐳 Docker 一鍵部署
- 🚀 多代理協作處理
- 📚 支持PDF和Markdown格式
- 🔍 智能文檔檢索
- 💬 自然語言問答
- 🎯 高精度答案生成
- 🌐 友好的Web界面
- 🦙 完全本地化運行

## 🚀 快速開始

### 開發環境
建議一律採用容器化開發模式

```bash
# Linux/macOS
chmod +x dev.sh
./dev.sh setup

# Attach to  Container進行容器化開發
# 打開工作目錄到/app底下
cp .env.example .env

# Windows PowerShell
.\dev.ps1
```

### 生產環境

```bash
# 啟動服務
docker compose up -d

# 下載模型
docker exec rag-ollama ollama pull llama2:7b

# 檢查狀態
docker compose ps
```

### 訪問系統
- **Web 界面**: http://localhost:8501
- **Ollama 服務**: http://localhost:11434

## 🔧 系統架構

### 核心組件
- **Data Loader Agent**: 負責讀取和處理PDF/Markdown文件
- **QA Agent**: 接收用戶問題，從文件中擷取相關答案
- **Vector Database**: 使用FAISS存儲文檔向量
- **RAG Pipeline**: 基於LlamaIndex的檢索增強生成流程

### 技術棧
- **AutoGen**: 多代理協作框架
- **LlamaIndex**: 文檔索引和檢索
- **Ollama**: 本地大語言模型服務
- **FAISS**: 向量資料庫
- **Streamlit**: Web界面

## 📁 目錄結構

```
rag-multiagent-qa/
├── compose.yml             # 生產環境配置
├── compose.dev.yml         # 開發環境配置
├── Dockerfile              # Python 應用配置
├── dev.sh                  # 開發環境管理腳本 (Linux/macOS)
├── dev.ps1                 # 開發環境管理腳本 (Windows)
├── data/                   # 數據持久化目錄
├── agents/                 # 代理定義
├── config.py               # 配置文件
├── app.py                  # Streamlit Web應用
└── requirements.txt        # Python依賴
```

## 🛠️ 開發指南

### 使用 dev.sh 腳本

我們提供了一個強大的開發環境管理腳本，讓您可以用簡潔的命令管理整個開發環境：

```bash
# 基本操作
./dev.sh up -d          # 後台啟動服務
./dev.sh down -v        # 停止服務並清理卷
./dev.sh restart        # 重啟服務
./dev.sh ps             # 查看服務狀態

# 日誌和調試
./dev.sh logs -f        # 跟隨日誌
./dev.sh exec rag-app bash  # 進入應用容器

# 初始設置
./dev.sh setup          # 一鍵完成所有設置
./dev.sh help           # 顯示幫助信息
```

### 模型選擇建議
- **輕量級**: gemma:2b, phi:2.7b (2-4GB RAM)
- **中等級**: llama2:7b:q4_0, mistral:7b:q4_0 (4-6GB RAM)
- **標準級**: llama2:7b, mistral:7b (6GB+ RAM)

## 📚 使用方法

1. 使用 `./dev.sh setup` 一鍵部署
2. 上傳PDF或Markdown文件
3. 系統自動處理並建立向量索引
4. 在聊天界面中提出問題
5. 系統通過多個代理協作回答

