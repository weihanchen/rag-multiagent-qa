#!/bin/bash

# RAG 多代理問答系統 - 開發環境啟動腳本

echo "🚀 啟動 RAG 多代理問答系統開發環境..."

# 創建必要的目錄
echo "📁 創建必要的目錄..."
mkdir -p data/vector_store data/uploads data/workspace

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker Desktop"
    exit 1
fi

# 構建並啟動開發服務
echo "🔨 構建並啟動開發服務..."
docker compose -f compose.dev.yml up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "📊 檢查服務狀態..."
docker compose -f compose.dev.yml ps

# 顯示訪問信息
echo ""
echo "✅ 開發環境啟動完成！"
echo ""
echo "🌐 訪問地址："
echo "   - Web 界面: http://localhost:8501"
echo "   - Ollama 服務: http://localhost:11434"
echo ""
echo "🔧 開發命令："
echo "   - 進入容器: docker exec -it rag-app bash"
echo "   - 查看日誌: docker compose -f compose.dev.yml logs -f rag-app"
echo "   - 重啟服務: docker compose -f compose.dev.yml restart rag-app"
echo "   - 停止服務: docker compose -f compose.dev.yml down"
echo ""
echo "📝 注意："
echo "   - 代碼變更會自動重新加載"
echo "   - 可以在容器內直接使用 git 命令"
echo "   - 所有開發操作都在容器內進行"
echo "   - 支持完整的版本控制操作"
