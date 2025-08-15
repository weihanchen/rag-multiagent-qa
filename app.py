import streamlit as st
import os
import tempfile
from pathlib import Path
import json
from typing import List, Dict, Any
import time

# 導入自定義模組
from config import Config
from agents.multi_agent_manager import MultiAgentManager

# 頁面配置
st.set_page_config(
    page_title="RAG 多代理文件問答系統",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主應用函數"""
    
    # 頁面標題
    st.markdown('<h1 class="main-header">🤖 RAG 多代理文件問答系統</h1>', unsafe_allow_html=True)
    
    # 側邊欄
    with st.sidebar:
        st.header("⚙️ 系統設置")
        
        # 檢查配置
        try:
            config = Config()
            config.validate()
            st.success("✅ 配置驗證通過")
            
            # 顯示配置信息
            st.subheader("📋 當前配置")
            st.write(f"**模型**: {config.OLLAMA_MODEL}")
            st.write(f"**向量存儲**: {config.VECTOR_STORE_TYPE}")
            st.write(f"**Chunk大小**: {config.CHUNK_SIZE}")
            st.write(f"**最大Token**: {config.MAX_TOKENS}")
            
        except Exception as e:
            st.error(f"❌ 配置錯誤: {str(e)}")
            st.info("請檢查 .env 文件中的 API 密鑰設置")
            return
        
        # 顯示系統狀態
        with st.expander("系統狀態", expanded=False):
            try:
                if 'agent_manager' in st.session_state:
                    manager = st.session_state.agent_manager
                else:
                    manager = MultiAgentManager()
                    st.session_state.agent_manager = manager
                
                status = manager.get_system_status()
                
                if "error" not in status:
                    config = status.get("config", {})
                    st.write(f"**模型提供者**: {config.get('model_provider', 'N/A')}")
                    st.write(f"**模型名稱**: {config.get('model_name', 'N/A')}")
                    st.write(f"**向量存儲**: {config.get('vector_store_type', 'N/A')}")
                    st.write(f"**Chunk大小**: {config.get('chunk_size', 'N/A')}")
                    st.write(f"**最大Token**: {config.get('max_tokens', 'N/A')}")
                    
                    agents = status.get("agents", {})
                    st.write("**代理狀態**:")
                    for agent_name, agent_status in agents.items():
                        st.write(f"   - {agent_name}: {agent_status}")
                    
                    vector_index = status.get("vector_index", {})
                    st.write(f"**向量索引**: {vector_index.get('status', 'N/A')}")
                    if vector_index.get("status") == "已初始化":
                        st.write(f"   - 文檔數量: {vector_index.get('document_count', 'N/A')}")
                        st.write(f"   - 存儲路徑: {vector_index.get('vector_store_path', 'N/A')}")
                    else:
                        st.error(f"獲取系統狀態失敗: {status['error']}")
                    
            except Exception as e:
                st.error(f"獲取系統狀態時發生錯誤: {str(e)}")
        
        # 重置按鈕
        if st.button("🔄 重置系統"):
            if 'agent_manager' in st.session_state:
                st.session_state.agent_manager.reset_system()
                st.success("系統已重置")
                st.rerun()
    
    # 主內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 文件上傳與處理")
        
        # 文件上傳
        uploaded_files = st.file_uploader(
            "選擇PDF、Markdown或文本文件",
            type=['pdf', 'md', 'txt'],
            accept_multiple_files=True,
            help="支持多個文件同時上傳"
        )
        
        if uploaded_files:
            st.success(f"已上傳 {len(uploaded_files)} 個文件")
            
            # 顯示文件信息
            for file in uploaded_files:
                st.write(f"**{file.name}** ({file.size} bytes)")
            
            # 處理文件按鈕
            if st.button("🚀 開始處理文件"):
                with st.spinner("正在處理文件..."):
                    # 保存上傳的文件到臨時目錄
                    temp_dir = tempfile.mkdtemp()
                    file_paths = []
                    
                    for file in uploaded_files:
                        temp_path = os.path.join(temp_dir, file.name)
                        with open(temp_path, 'wb') as f:
                            f.write(file.getvalue())
                        file_paths.append(temp_path)
                    
                    # 初始化代理管理器
                    if 'agent_manager' not in st.session_state:
                        st.session_state.agent_manager = MultiAgentManager()
                    
                    # 處理文件
                    result = st.session_state.agent_manager.process_documents(file_paths)
                    
                    if result.get("success", False):
                        st.success(f"✅ 文件處理完成！")
                        st.write(f"處理了 {result['documents_processed']} 個文檔")
                        st.write(f"創建了 {result['chunks_created']} 個chunks")
                        st.write("向量索引已準備就緒")
                        
                        # 清理臨時文件
                        import shutil
                        shutil.rmtree(temp_dir)
                        
                        st.session_state.files_processed = True
                    else:
                        error_msg = result.get('error', '未知錯誤')
                        st.error(f"❌ 文件處理失敗: {error_msg}")
    
    with col2:
        st.header("💬 智能問答")
        
        # 檢查是否已處理文件
        if not st.session_state.get('files_processed', False):
            st.info("👆 請先上傳並處理文件")
        else:
            # 問答界面
            question = st.text_input(
                "請輸入您的問題：",
                placeholder="例如：這份文檔的主要內容是什麼？",
                help="系統會基於上傳的文檔內容回答您的問題"
            )
            
            if st.button("🔍 提問") and question:
                with st.spinner("正在思考中..."):
                    # 使用代理管理器回答問題
                    answer = st.session_state.agent_manager.ask_question(question)
                    
                    if answer.get("success", False):
                        st.success("✅ 找到答案！")
                        
                        # 顯示答案
                        st.subheader("📝 答案")
                        st.write(answer["answer"])
                        
                        # 顯示源節點信息
                        if answer.get("source_nodes"):
                            st.subheader("📚 參考來源")
                            for i, source in enumerate(answer["source_nodes"]):
                                with st.expander(f"來源 {i+1}"):
                                    st.write(f"**內容**: {source['text']}")
                                    if source.get('metadata'):
                                        st.write(f"**元數據**: {source['metadata']}")
                                    if source.get('score'):
                                        st.write(f"**相關性分數**: {source.get('score', 0):.3f}")
                        
                        # 保存到對話歷史
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": answer,
                            "timestamp": time.time()
                        })
                        
                    else:
                        error_msg = answer.get('error', '未知錯誤')
                        st.error(f"❌ 回答失敗: {error_msg}")
            
            # 顯示對話歷史
            if 'chat_history' in st.session_state and st.session_state.chat_history:
                st.subheader("📜 對話歷史")
                for i, chat in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"對話 {len(st.session_state.chat_history) - i}"):
                        st.markdown(f"**問題**: {chat['question']}")
                        if isinstance(chat['answer'], dict) and 'answer' in chat['answer']:
                            st.markdown(f"**答案**: {chat['answer']['answer']}")
                        else:
                            st.markdown(f"**答案**: {str(chat['answer'])}")
                        st.caption(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(chat['timestamp']))}")
    
    # 底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🤖 基於 AutoGen + LlamaIndex 的智能文件問答系統</p>
        <p>支持 PDF、Markdown、文本格式 | 多代理協作 | 向量檢索</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
