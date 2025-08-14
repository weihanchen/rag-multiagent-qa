#!/usr/bin/env python3
"""
RAG 多代理文件問答系統 - 示例使用腳本

這個腳本展示了如何使用多代理系統進行文件處理和問答。
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from agents.multi_agent_manager import MultiAgentManager

def create_sample_document():
    """創建示例文檔"""
    sample_content = """
# 公司政策手冊

## 1. 員工行為準則

### 1.1 基本原則
- 誠實守信，遵守職業道德
- 尊重同事，維護團隊和諧
- 保護公司機密信息
- 積極學習，不斷提升專業能力

### 1.2 工作紀律
- 準時上下班，不遲到早退
- 認真完成工作任務
- 遵守公司規章制度
- 積極參與團隊活動

## 2. 薪資福利

### 2.1 基本工資
- 根據職位和經驗確定基本工資
- 每年進行薪資評估和調整
- 提供有競爭力的薪資待遇

### 2.2 獎金制度
- 年終獎金：根據公司業績和個人表現
- 項目獎金：完成重要項目後的額外獎勵
- 績效獎金：月度或季度績效考核獎勵

## 3. 培訓發展

### 3.1 入職培訓
- 公司文化介紹
- 崗位技能培訓
- 安全知識培訓
- 團隊協作培訓

### 3.2 在職培訓
- 定期技能提升課程
- 管理能力培訓
- 新技術學習
- 行業知識更新

## 4. 晉升機制

### 4.1 晉升條件
- 工作表現優秀
- 具備晉升職位所需能力
- 通過晉升考核
- 獲得主管推薦

### 4.2 晉升流程
1. 員工申請或主管推薦
2. 人力資源部門初審
3. 晉升考核和面試
4. 總經理審批
5. 正式任命和公告
"""
    
    # 創建示例文檔目錄
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    
    # 保存示例文檔
    sample_file = sample_dir / "company_policy.md"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"✅ 示例文檔已創建：{sample_file}")
    return str(sample_file)

def main():
    """主函數"""
    print("🚀 RAG 多代理文件問答系統 - 示例使用")
    print("=" * 50)
    
    try:
        # 驗證配置
        print("📋 驗證系統配置...")
        config = Config()
        config.validate()
        print("✅ 配置驗證通過")
        
        # 創建示例文檔
        print("\n📝 創建示例文檔...")
        sample_file = create_sample_document()
        
        # 初始化多代理管理器
        print("\n🤖 初始化多代理系統...")
        agent_manager = MultiAgentManager()
        print("✅ 多代理系統初始化完成")
        
        # 處理示例文檔
        print(f"\n📁 處理示例文檔：{sample_file}")
        result = agent_manager.process_documents([sample_file])
        
        if result["success"]:
            print("✅ 文檔處理成功！")
            print(f"   - 處理文檔數：{result['documents_processed']}")
            print(f"   - 創建chunks數：{result['chunks_created']}")
            print(f"   - 向量索引狀態：{'就緒' if result['vector_index_ready'] else '未就緒'}")
            
            # 測試問答功能
            print("\n💬 測試問答功能...")
            
            test_questions = [
                "公司的員工行為準則有哪些基本原則？",
                "薪資福利包括哪些內容？",
                "員工晉升需要滿足什麼條件？",
                "公司提供哪些培訓機會？"
            ]
            
            for i, question in enumerate(test_questions, 1):
                print(f"\n❓ 問題 {i}: {question}")
                answer = agent_manager.ask_question(question)
                
                if answer["success"]:
                    print(f"✅ 答案: {answer['answer'][:200]}...")
                    
                    # 顯示源節點信息
                    if answer.get("source_nodes"):
                        print(f"   📚 參考來源: {len(answer['source_nodes'])} 個")
                else:
                    print(f"❌ 回答失敗: {answer['error']}")
            
            # 顯示系統狀態
            print("\n📊 系統狀態:")
            status = agent_manager.get_system_status()
            print(f"   - OpenAI模型: {status['config']['openai_model']}")
            print(f"   - 向量存儲類型: {status['config']['vector_store_type']}")
            print(f"   - 向量索引狀態: {status['vector_index']['status']}")
            
            # 顯示代理對話歷史
            print("\n🤖 代理協作歷史:")
            history = agent_manager.get_agent_conversation_history()
            if history:
                print(f"   - 對話輪數: {len(history)}")
                for i, msg in enumerate(history[-3:], 1):  # 顯示最後3條
                    print(f"   - 輪次 {i}: {msg.get('name', 'Unknown')} - {msg.get('content', '')[:100]}...")
            else:
                print("   - 暫無對話歷史")
                
        else:
            print(f"❌ 文檔處理失敗: {result['error']}")
            
    except Exception as e:
        print(f"❌ 運行示例時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 示例運行完成！")
    print("\n💡 提示:")
    print("1. 檢查 .env 文件中的 OpenAI API 密鑰設置")
    print("2. 運行 'streamlit run app.py' 啟動Web界面")
    print("3. 上傳自己的文檔進行測試")

if __name__ == "__main__":
    main()
