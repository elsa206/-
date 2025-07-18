#!/usr/bin/env python3
"""
Azure AI 食物影像辨識 - 快速啟動腳本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """檢查環境需求"""
    print("🔍 檢查環境需求...")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 檢查環境變數
    if not os.getenv('AZURE_VISION_ENDPOINT') or not os.getenv('AZURE_VISION_KEY'):
        print("❌ 缺少 Azure API 設定")
        print("請設定以下環境變數:")
        print("  AZURE_VISION_ENDPOINT")
        print("  AZURE_VISION_KEY")
        print("\n請複製 config.env.example 為 .env 並填入您的 API 金鑰")
        return False
    
    print("✅ Azure API 設定完成")
    return True

def install_dependencies():
    """安裝依賴套件"""
    print("📦 安裝依賴套件...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依賴套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依賴套件安裝失敗")
        return False

def start_streamlit():
    """啟動 Streamlit 應用程式"""
    print("🚀 啟動 Streamlit 應用程式...")
    
    try:
        # 檢查 app.py 是否存在
        if not Path("app.py").exists():
            print("❌ 找不到 app.py 檔案")
            return False
        
        # 啟動 Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        return True
    except KeyboardInterrupt:
        print("\n👋 應用程式已停止")
        return True
    except Exception as e:
        print(f"❌ 啟動失敗: {str(e)}")
        return False

def main():
    """主函數"""
    print("🍽️ Azure AI 食物影像辨識 - 快速啟動")
    print("=" * 50)
    
    # 檢查環境
    if not check_requirements():
        return
    
    # 檢查是否需要安裝依賴
    try:
        import streamlit
        import plotly
        print("✅ 依賴套件已安裝")
    except ImportError:
        print("📦 檢測到缺少依賴套件")
        if not install_dependencies():
            return
    
    # 啟動應用程式
    print("\n🌐 應用程式將在瀏覽器中開啟")
    print("📱 如果沒有自動開啟，請手動訪問: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止應用程式")
    print("-" * 50)
    
    start_streamlit()

if __name__ == "__main__":
    main() 