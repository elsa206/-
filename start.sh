#!/bin/bash

echo "========================================"
echo "   食物熱量提取器 - 簡化版本"
echo "========================================"
echo

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "錯誤：未找到 Python3，請先安裝 Python 3.7+"
    exit 1
fi

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴套件
echo "安裝依賴套件..."
pip install -r requirements.txt

# 檢查環境變數檔案
if [ ! -f ".env" ]; then
    echo "複製環境變數檔案..."
    cp env.example .env
    echo "請編輯 .env 檔案設定環境變數"
fi

echo
echo "========================================"
echo "   選擇執行模式"
echo "========================================"
echo "1. 快速版本 (測試用，限制頁數)"
echo "2. 完整版本 (提取所有資料)"
echo "3. 執行測試"
echo "4. 互動式搜尋"
echo "5. 退出"
echo

read -p "請選擇 (1-5): " choice

case $choice in
    1)
        echo "執行快速版本..."
        python3 quick_calories.py
        ;;
    2)
        echo "執行完整版本..."
        python3 simple_food_calories.py
        ;;
    3)
        echo "執行測試..."
        python3 simple_calories_test.py
        ;;
    4)
        echo "啟動互動式搜尋..."
        python3 -c "from simple_food_calories import SimpleCalorieExtractor; extractor = SimpleCalorieExtractor(); extractor.interactive_search()"
        ;;
    5)
        echo "退出程式"
        exit 0
        ;;
    *)
        echo "無效選擇"
        ;;
esac

echo
read -p "按 Enter 鍵繼續..." 