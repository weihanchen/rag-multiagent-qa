#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 本地模型測試腳本
用於驗證 Ollama 設置是否正確
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_ollama_connection():
    """測試 Ollama 連接"""
    print("🦙 測試 Ollama 連接...")
    
    try:
        import requests
        
        # 獲取 Ollama 配置
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2:7b")
        
        print(f"📍 連接地址: {base_url}")
        print(f"🤖 模型名稱: {model}")
        
        # 測試基本連接
        print("\n1️⃣ 測試基本連接...")
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            print("✅ 基本連接成功")
            
            # 獲取可用模型
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            print(f"📋 可用模型: {model_names}")
            
            # 檢查目標模型是否可用
            if model in model_names:
                print(f"✅ 目標模型 {model} 可用")
            else:
                print(f"⚠️  目標模型 {model} 不可用")
                print(f"💡 請使用 'ollama pull {model}' 下載模型")
                return False
            
        else:
            print(f"❌ 基本連接失敗: HTTP {response.status_code}")
            return False
        
        # 測試模型推理
        print("\n2️⃣ 測試模型推理...")
        test_prompt = "Hello, how are you?"
        
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": test_prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 模型推理成功")
            print(f"📝 測試提示: {test_prompt}")
            print(f"🤖 模型回應: {result.get('response', '')[:100]}...")
        else:
            print(f"❌ 模型推理失敗: HTTP {response.status_code}")
            print(f"錯誤詳情: {response.text}")
            return False
        
        # 測試嵌入功能
        print("\n3️⃣ 測試嵌入功能...")
        response = requests.post(
            f"{base_url}/api/embeddings",
            json={
                "model": model,
                "prompt": test_prompt
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print(f"✅ 嵌入功能正常，向量維度: {len(embedding)}")
        else:
            print(f"⚠️  嵌入功能測試失敗: HTTP {response.status_code}")
            print("💡 這可能影響向量搜索功能，但不會阻止基本使用")
        
        print("\n🎉 所有測試通過！Ollama 設置成功！")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 Ollama 服務")
        print("💡 請確保 Ollama 服務正在運行:")
        print("   ollama serve")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 連接超時")
        print("💡 請檢查 Ollama 服務狀態和網絡連接")
        return False
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        return False

def test_config_validation():
    """測試配置驗證"""
    print("\n⚙️  測試配置驗證...")
    
    try:
        from config import Config
        
        # 驗證配置
        Config.validate()
        print("✅ 配置驗證通過")
        
        # 測試 LLM 配置
        llm_config = Config.get_llm_config()
        print(f"🤖 LLM 配置: {llm_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置驗證失敗: {str(e)}")
        return False

def test_agent_initialization():
    """測試代理初始化"""
    print("\n🤖 測試代理初始化...")
    
    try:
        from agents.multi_agent_manager import MultiAgentManager
        
        # 初始化管理器
        manager = MultiAgentManager()
        print("✅ 多代理管理器初始化成功")
        
        # 測試連接
        result = manager.test_model_connection()
        print(f"🔗 連接測試結果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 代理初始化失敗: {str(e)}")
        return False

def main():
    """主函數"""
    print("🚀 Ollama 本地模型設置測試")
    print("=" * 50)
    
    # 運行測試
    tests = [
        test_ollama_connection,
        test_config_validation,
        test_agent_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test.__name__} 執行失敗: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 恭喜！Ollama 設置完全成功！")
        print("💡 現在可以開始使用本地模型進行問答了")
    else:
        print("⚠️  部分測試失敗，請檢查設置並重試")
        print("📚 參考 OLLAMA_SETUP.md 獲取詳細幫助")

if __name__ == "__main__":
    main()
