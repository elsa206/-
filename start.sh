#!/bin/bash

# FDA 營養資料庫抓取與分析系統
# 台灣食品藥物管理署營養資料庫整合

echo ""
echo "========================================"
echo "  FDA 營養資料庫抓取與分析系統"
echo "  台灣食品藥物管理署營養資料庫整合"
echo "========================================"
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python3，請先安裝 Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "✅ Python 已安裝"
python3 --version

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 建立虛擬環境失敗"
        exit 1
    fi
    echo "✅ 虛擬環境建立完成"
fi

# 啟動虛擬環境
echo ""
echo "🔄 啟動虛擬環境..."
source venv/bin/activate

# 升級 pip
echo ""
echo "📦 升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo ""
echo "📦 安裝 Python 依賴套件..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依賴安裝失敗"
    exit 1
fi
echo "✅ 依賴安裝完成"

# 檢查環境變數檔案
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  未找到 .env 檔案，正在建立..."
    cp env.example .env
    echo "✅ .env 檔案已建立"
    echo ""
    echo "📝 請編輯 .env 檔案，設定您的 Azure API 金鑰"
    echo ""
    
    # 檢查是否有可用的編輯器
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v vi &> /dev/null; then
        vi .env
    else
        echo "請使用您喜歡的編輯器編輯 .env 檔案"
    fi
fi

# 建立必要目錄
mkdir -p output logs test_data

# 設定執行權限
chmod +x run_fda_scraper.py
chmod +x fda_nutrition_scraper.py

echo ""
echo "========================================"
echo "   環境設定完成！"
echo "========================================"
echo ""
echo "🚀 可用的命令:"
echo ""
echo "  1. 執行 FDA 資料抓取:"
echo "     python run_fda_scraper.py"
echo ""
echo "  2. 直接執行抓取器:"
echo "     python fda_nutrition_scraper.py"
echo ""
echo "  3. 測試增強版食物偵測:"
echo "     python -c \"from enhanced_food_detection import test_enhanced_food_detection; test_enhanced_food_detection()\""
echo ""
echo "  4. 查看使用說明:"
echo "     python run_fda_scraper.py --help"
echo ""

# 詢問是否立即執行
read -p "是否要立即執行 FDA 資料抓取？(y/N): " choice
if [[ $choice =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 開始執行 FDA 資料抓取..."
    python run_fda_scraper.py
else
    echo ""
    echo "💡 您可以稍後手動執行上述命令"
fi

echo ""
echo "按 Enter 鍵退出..."
read 