#!/bin/bash

# WebEye 食物偵測系統 - 啟動腳本 (Linux/Mac)

echo "========================================"
echo "   WebEye 食物偵測系統 - 啟動腳本"
echo "========================================"
echo

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python3，請先安裝 Python 3.8+"
    exit 1
fi

echo "✅ Python3 已安裝"
echo

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ 創建虛擬環境失敗"
        exit 1
    fi
fi

# 啟動虛擬環境
echo "🔄 啟動虛擬環境..."
source .venv/bin/activate

# 安裝依賴
echo "📦 檢查並安裝依賴套件..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 安裝依賴失敗"
    exit 1
fi

echo "✅ 依賴安裝完成"
echo

# 檢查環境變數檔案
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 檔案"
    echo "📝 請複製 env.example 為 .env 並設定您的 Azure API 金鑰"
    echo
    cp env.example .env
    echo "✅ 已創建 .env 檔案，請編輯並填入您的 API 金鑰"
    echo
fi

# 顯示選單
show_menu() {
    echo "請選擇要啟動的應用程式:"
    echo
    echo "1. 🖥️  桌面應用程式 (Tkinter)"
    echo "2. 🌐  Web 應用程式 (Streamlit)"
    echo "3. 🧪  運行測試"
    echo "4. ❌  退出"
    echo
}

# 主選單循環
while true; do
    show_menu
    read -p "請輸入選項 (1-4): " choice
    
    case $choice in
        1)
            echo
            echo "🖥️ 啟動桌面應用程式..."
            python webeye_food_app.py
            break
            ;;
        2)
            echo
            echo "🌐 啟動 Web 應用程式..."
            echo "📡 應用程式將在瀏覽器中開啟: http://localhost:8501"
            echo
            streamlit run streamlit_app.py
            break
            ;;
        3)
            echo
            echo "🧪 運行系統測試..."
            python test_webeye_camera.py
            echo
            read -p "按 Enter 鍵繼續..."
            ;;
        4)
            echo
            echo "👋 感謝使用 WebEye 食物偵測系統！"
            break
            ;;
        *)
            echo "❌ 無效選項，請重新選擇"
            ;;
    esac
done

echo
echo "按 Enter 鍵退出..."
read 