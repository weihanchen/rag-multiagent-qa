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

## 🐳 Docker 快速啟動

### 生產環境部署

```bash
# 1. 創建必要目錄
mkdir -p data/vector_store data/uploads data/workspace

# 2. 啟動生產服務
docker compose up -d

# 3. 下載模型
docker exec rag-ollama ollama pull llama2:7b

# 4. 檢查狀態
docker compose ps
```

### 開發環境部署

```bash
# 1. 創建必要目錄
mkdir -p data/vector_store data/uploads data/workspace

# 2. 啟動開發服務 (支持熱重載)
docker compose -f compose.dev.yml up -d

# 3. 下載模型
docker exec rag-ollama ollama pull llama2:7b

# 4. 檢查狀態
docker compose -f compose.dev.yml ps
```

### 訪問系統
- **Web 界面**: http://localhost:8501
- **Ollama 服務**: http://localhost:11434

## 🔧 系統架構

### 服務架構
```
┌─────────────────┐    ┌─────────────────┐
│   Ollama 服務   │    │   RAG 應用      │
│   Port: 11434   │◄──►│   Port: 8501    │
└─────────────────┘    └─────────────────┘
```

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
├── compose.yml             # 生產環境 Docker Compose 配置
├── compose.dev.yml         # 開發環境 Docker Compose 配置
├── Dockerfile              # Python 應用 Docker 配置
├── data/                   # 數據持久化目錄
│   ├── vector_store/       # 向量索引存儲
│   ├── uploads/            # 文件上傳目錄
│   └── workspace/          # 工作目錄
├── agents/                 # 代理定義
├── config.py               # 配置文件
├── app.py                  # Streamlit Web應用
└── requirements.txt        # Python依賴
```

### 模型選擇建議
- **開發測試**: Llama2-7B (4GB+ RAM)
- **生產環境**: Llama2-13B (8GB+ RAM)
- **資源受限**: 使用量化版本 `llama2:7b:q4_0`

## 🔄 升級和維護

### 備份和恢復
```bash
# 備份向量索引
tar -czf data_backup.tar.gz data/

# 備份 Ollama 模型
docker exec rag-ollama ollama list > models_backup.txt
```

## 開發指南

### 開發環境設置

#### 快速啟動 (推薦)
```bash
# Windows PowerShell
.\dev-start.ps1

# Linux/macOS
chmod +x dev-start.sh
./dev-start.sh
```

#### 手動啟動
```bash
# 1. 創建必要目錄
mkdir -p data/vector_store data/uploads data/workspace

# 2. 啟動開發服務 (支持熱重載)
docker compose -f compose.dev.yml up -d --build

# 3. 下載模型
docker exec rag-ollama ollama pull llama2:7b

# 4. 檢查服務狀態
docker compose -f compose.dev.yml ps
```

### 開發工作流程

1. **啟動開發容器**: 使用 `.\dev-start.ps1` 或 `./dev-start.sh`
2. **進入容器**: `docker exec -it rag-app bash`
3. **容器內開發**: 直接在容器內編輯代碼、使用 git 命令
4. **自動重載**: Streamlit 會自動檢測代碼變更並重新加載
5. **即時測試**: 在瀏覽器中驗證功能
6. **版本控制**: 在容器內直接進行 git 操作，可手動設定用戶信息
7. **目錄同步**: 整個項目目錄實時同步，支持本地和容器內編輯

### 容器內開發優勢

- **環境一致性**: 開發環境與生產環境完全一致
- **依賴管理**: 無需本地安裝 Python 環境和依賴
- **熱重載**: 代碼變更自動重新加載，無需重啟容器
- **隔離性**: 開發環境與本地系統完全隔離
- **協作友好**: 團隊成員可以使用相同的開發環境
- **Git 集成**: 容器內可直接進行版本控制操作
- **權限管理**: 使用 root 用戶，確保有足夠權限進行各種操作
- **開發工具**: 支持完整的 Python 開發環境
- **目錄掛載**: 整個項目目錄直接掛載，支持即時編輯和同步

### 常用開發命令

```bash
# 進入應用容器
docker exec -it rag-app bash

# 查看容器日誌
docker compose -f compose.dev.yml logs -f rag-app

# 重啟開發服務
docker compose -f compose.dev.yml restart rag-app

# 停止開發服務
docker compose -f compose.dev.yml down

# 容器內 Git 配置 (首次使用時)
git config --global user.name "您的姓名"
git config --global user.email "您的郵箱"
```

## 📚 使用方法

1. 使用 Docker 啟動腳本一鍵部署
2. 上傳PDF或Markdown文件
3. 系統會自動處理並建立向量索引
4. 在聊天界面中提出問題
5. 系統會通過多個代理協作回答您的問題



