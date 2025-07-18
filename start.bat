@echo off
chcp 65001 >nul
echo ========================================
echo    食物熱量提取器 - 簡化版本
echo ========================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Python，請先安裝 Python 3.7+
    pause
    exit /b 1
)

:: 檢查虛擬環境
if not exist "venv" (
    echo 創建虛擬環境...
    python -m venv venv
)

:: 啟動虛擬環境
echo 啟動虛擬環境...
call venv\Scripts\activate.bat

:: 安裝依賴套件
echo 安裝依賴套件...
pip install -r requirements.txt

:: 檢查環境變數檔案
if not exist ".env" (
    echo 複製環境變數檔案...
    copy env.example .env
    echo 請編輯 .env 檔案設定環境變數
)

echo.
echo ========================================
echo    選擇執行模式
echo ========================================
echo 1. 快速版本 (測試用，限制頁數)
echo 2. 完整版本 (提取所有資料)
echo 3. 執行測試
echo 4. 互動式搜尋
echo 5. 退出
echo.

set /p choice="請選擇 (1-5): "

if "%choice%"=="1" (
    echo 執行快速版本...
    python quick_calories.py
) else if "%choice%"=="2" (
    echo 執行完整版本...
    python simple_food_calories.py
) else if "%choice%"=="3" (
    echo 執行測試...
    python simple_calories_test.py
) else if "%choice%"=="4" (
    echo 啟動互動式搜尋...
    python -c "from simple_food_calories import SimpleCalorieExtractor; extractor = SimpleCalorieExtractor(); extractor.interactive_search()"
) else if "%choice%"=="5" (
    echo 退出程式
    exit /b 0
) else (
    echo 無效選擇
)

echo.
pause 