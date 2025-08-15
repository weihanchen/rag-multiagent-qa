#!/bin/bash

# RAG 多代理問答系統 - 開發環境管理腳本

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示幫助信息
show_help() {
    echo -e "${BLUE}🚀 RAG 多代理問答系統 - 開發環境管理腳本${NC}"
    echo ""
    echo "用法:"
    echo "  ./dev.sh [命令] [選項]"
    echo ""
    echo "常用命令:"
    echo "  up         啟動所有服務"
    echo "  down       停止所有服務"
    echo "  down -v    停止所有服務並刪除卷"
    echo "  restart    重啟所有服務"
    echo "  logs       查看服務日誌"
    echo "  ps         查看服務狀態"
    echo "  build      重新構建服務"
    echo "  exec       進入容器 (例如: ./dev.sh exec rag-app bash)"
    echo "  setup      初始設置 (創建目錄、下載模型)"
    echo "  help       顯示此幫助信息"
    echo ""
    echo "示例:"
    echo "  ./dev.sh up -d          # 後台啟動服務"
    echo "  ./dev.sh down -v        # 停止服務並清理"
    echo "  ./dev.sh logs -f        # 跟隨日誌"
    echo "  ./dev.sh exec rag-app bash  # 進入應用容器"
}

# 創建必要的目錄
create_directories() {
    echo -e "${BLUE}📁 創建必要的目錄...${NC}"
    mkdir -p data/vector_store data/uploads data/workspace data/ollama
    echo -e "${GREEN}✅ 目錄創建完成${NC}"
}

# 檢查 Docker 是否運行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker 未運行，請先啟動 Docker Desktop${NC}"
        exit 1
    fi
}

# 初始設置
setup() {
    echo -e "${BLUE}🔧 執行初始設置...${NC}"
    
    check_docker
    create_directories
    
    # 啟動服務
    echo -e "${BLUE}🔨 啟動服務...${NC}"
    docker compose -f compose.dev.yml up -d
    
    # 等待服務啟動
    echo -e "${BLUE}⏳ 等待服務啟動...${NC}"
    sleep 10
    
    # 檢查服務狀態
    echo -e "${BLUE}📊 檢查服務狀態...${NC}"
    docker compose -f compose.dev.yml ps
    
    # 模型下載提示
    echo ""
    echo -e "${YELLOW}🤖 模型下載 (必需步驟):${NC}"
    echo "   選擇適合您筆電的模型："
    echo "   - 輕量級 (2-4GB RAM): gemma:2b, phi:2.7b"
    echo "   - 中等級 (4-6GB RAM): llama2:7b:q4_0, mistral:7b:q4_0"
    echo "   - 標準級 (6GB+ RAM): llama2:7b, mistral:7b"
    echo ""
    
    # 詢問用戶選擇模型
    read -p "請輸入要下載的模型名稱 (直接按 Enter 使用預設 gemma:2b): " MODEL_NAME
    
    # 如果用戶沒有輸入，使用預設的輕量級模型
    if [ -z "$MODEL_NAME" ]; then
        MODEL_NAME="gemma:2b"
        echo -e "${GREEN}🤖 使用預設模型: $MODEL_NAME (適合筆電環境)${NC}"
    fi
    
    echo -e "${BLUE}📥 正在下載模型: $MODEL_NAME${NC}"
    docker exec rag-multiagent-qa-ollama-1 ollama pull "$MODEL_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 模型下載完成！${NC}"
    else
        echo -e "${RED}❌ 模型下載失敗，請檢查網絡連接或模型名稱${NC}"
        echo -e "${YELLOW}💡 您可以稍後手動執行：docker exec rag-multiagent-qa-ollama-1 ollama pull gemma:2b${NC}"
    fi
    
    show_access_info
}

# 顯示訪問信息
show_access_info() {
    echo ""
    echo -e "${GREEN}✅ 開發環境啟動完成！${NC}"
    echo ""
    echo -e "${BLUE}🌐 訪問地址：${NC}"
    echo "   - Web 界面: http://localhost:8501"
    echo "   - Ollama 服務: http://localhost:11434"
    echo ""
    echo -e "${BLUE}🔧 開發命令：${NC}"
    echo "   - 進入容器: ./dev.sh exec rag-app bash"
    echo "   - 查看日誌: ./dev.sh logs -f"
    echo "   - 重啟服務: ./dev.sh restart"
    echo "   - 停止服務: ./dev.sh down"
    echo ""
    echo -e "${BLUE}📝 注意：${NC}"
    echo "   - 代碼變更會自動重新加載"
    echo "   - 可以在容器內直接使用 git 命令"
    echo "   - 所有開發操作都在容器內進行"
    echo "   - 支持完整的版本控制操作"
}

# 主邏輯
main() {
    # 如果沒有參數，顯示幫助
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 處理特殊命令
    case "$1" in
        "setup")
            setup
            exit 0
            ;;
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "exec")
            # 特殊處理 exec 命令
            shift  # 移除 "exec"
            if [ $# -eq 0 ]; then
                echo -e "${RED}❌ 請指定要執行的命令，例如: ./dev.sh exec rag-app bash${NC}"
                exit 1
            fi
            docker compose -f compose.dev.yml exec "$@"
            exit 0
            ;;
        *)
            # 檢查 Docker 是否運行（除了 help 和 setup 命令）
            if [[ "$1" != "help" && "$1" != "-h" && "$1" != "--help" && "$1" != "setup" ]]; then
                check_docker
            fi
            
            # 傳遞所有參數給 docker compose
            echo -e "${BLUE}🔧 執行命令: docker compose -f compose.dev.yml $*${NC}"
            docker compose -f compose.dev.yml "$@"
            ;;
    esac
}

# 執行主函數
main "$@"
