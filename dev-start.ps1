# RAG 多代理問答系統 - 開發環境啟動腳本 (PowerShell)

Write-Host "🚀 啟動 RAG 多代理問答系統開發環境..." -ForegroundColor Green

# 創建必要的目錄
Write-Host "📁 創建必要的目錄..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data/vector_store" | Out-Null
New-Item -ItemType Directory -Force -Path "data/uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "data/workspace" | Out-Null

# 檢查 Docker 是否運行
Write-Host "🔍 檢查 Docker 狀態..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker 正在運行" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 未運行，請先啟動 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 構建並啟動開發服務
Write-Host "🔨 構建並啟動開發服務..." -ForegroundColor Yellow
docker compose -f compose.dev.yml up -d --build

# 等待服務啟動
Write-Host "⏳ 等待服務啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 檢查服務狀態
Write-Host "📊 檢查服務狀態..." -ForegroundColor Yellow
docker compose -f compose.dev.yml ps

# 顯示訪問信息
Write-Host ""
Write-Host "✅ 開發環境啟動完成！" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 訪問地址：" -ForegroundColor Cyan
Write-Host "   - Web 界面: http://localhost:8501" -ForegroundColor White
Write-Host "   - Ollama 服務: http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "🔧 開發命令：" -ForegroundColor Cyan
Write-Host "   - 進入容器: docker exec -it rag-app bash" -ForegroundColor White
Write-Host "   - 查看日誌: docker compose -f compose.dev.yml logs -f rag-app" -ForegroundColor White
Write-Host "   - 重啟服務: docker compose -f compose.dev.yml restart rag-app" -ForegroundColor White
Write-Host "   - 停止服務: docker compose -f compose.dev.yml down" -ForegroundColor White
Write-Host ""
Write-Host "📝 注意：" -ForegroundColor Cyan
Write-Host "   - 代碼變更會自動重新加載" -ForegroundColor White
Write-Host "   - 可以在容器內直接使用 git 命令" -ForegroundColor White
Write-Host "   - 所有開發操作都在容器內進行" -ForegroundColor White
Write-Host "   - 支持完整的版本控制操作" -ForegroundColor White
