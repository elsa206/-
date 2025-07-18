#!/bin/bash

echo "🍽️ USDA 食物熱量抓取器"
echo "================================"
echo ""
echo "請選擇要執行的程式："
echo ""
echo "1. 快速測試 (測試API連接)"
echo "2. 熱量查詢工具 (互動式查詢)"
echo "3. 簡化熱量提取器 (抓取熱量資料)"
echo "4. 完整抓取器 (完整功能)"
echo "5. 安裝依賴套件"
echo "6. 退出"
echo ""
read -p "請輸入選項 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 執行快速測試..."
        python3 quick_usda_test.py
        ;;
    2)
        echo ""
        echo "🔍 啟動熱量查詢工具..."
        python3 usda_calorie_lookup.py
        ;;
    3)
        echo ""
        echo "📊 執行簡化熱量提取器..."
        python3 simple_usda_calories.py
        ;;
    4)
        echo ""
        echo "🌟 執行完整抓取器..."
        python3 usda_food_scraper.py
        ;;
    5)
        echo ""
        echo "📦 安裝依賴套件..."
        pip3 install -r requirements.txt
        echo ""
        echo "✅ 安裝完成！"
        ;;
    6)
        echo ""
        echo "👋 再見！"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 無效的選項，請重新選擇"
        ;;
esac

echo ""
read -p "按 Enter 鍵繼續..." 