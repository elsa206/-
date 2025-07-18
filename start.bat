@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   FDA 營養資料庫抓取與分析系統
echo   台灣食品藥物管理署營養資料庫整合
echo ========================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python，請先安裝 Python 3.8+
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安裝
python --version

:: 檢查虛擬環境
if not exist "venv" (
    echo.
    echo 📦 建立虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo ✅ 虛擬環境建立完成
)

:: 啟動虛擬環境
echo.
echo 🔄 啟動虛擬環境...
call venv\Scripts\activate.bat

:: 安裝依賴
echo.
echo 📦 安裝 Python 依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依賴安裝失敗
    pause
    exit /b 1
)
echo ✅ 依賴安裝完成

:: 檢查環境變數檔案
if not exist ".env" (
    echo.
    echo ⚠️  未找到 .env 檔案，正在建立...
    copy env.example .env
    echo ✅ .env 檔案已建立
    echo.
    echo 📝 請編輯 .env 檔案，設定您的 Azure API 金鑰
    echo.
    notepad .env
)

:: 建立必要目錄
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "test_data" mkdir test_data

echo.
echo ========================================
echo   環境設定完成！
echo ========================================
echo.
echo 🚀 可用的命令:
echo.
echo   1. 執行 FDA 資料抓取:
echo      python run_fda_scraper.py
echo.
echo   2. 直接執行抓取器:
echo      python fda_nutrition_scraper.py
echo.
echo   3. 測試增強版食物偵測:
echo      python -c "from enhanced_food_detection import test_enhanced_food_detection; test_enhanced_food_detection()"
echo.
echo   4. 查看使用說明:
echo      python run_fda_scraper.py --help
echo.

:: 詢問是否立即執行
set /p choice="是否要立即執行 FDA 資料抓取？(y/N): "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 開始執行 FDA 資料抓取...
    python run_fda_scraper.py
) else (
    echo.
    echo 💡 您可以稍後手動執行上述命令
)

echo.
echo 按任意鍵退出...
pause >nul 