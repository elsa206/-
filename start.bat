@echo off
chcp 65001 >nul
echo ========================================
echo    WebEye 食物偵測系統 - 啟動腳本
echo ========================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python，請先安裝 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安裝
echo.

:: 檢查虛擬環境
if not exist ".venv" (
    echo 📦 創建虛擬環境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 創建虛擬環境失敗
        pause
        exit /b 1
    )
)

:: 啟動虛擬環境
echo 🔄 啟動虛擬環境...
call .venv\Scripts\activate.bat

:: 安裝依賴
echo 📦 檢查並安裝依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 安裝依賴失敗
    pause
    exit /b 1
)

echo ✅ 依賴安裝完成
echo.

:: 檢查環境變數檔案
if not exist ".env" (
    echo ⚠️ 警告: 未找到 .env 檔案
    echo 📝 請複製 env.example 為 .env 並設定您的 Azure API 金鑰
    echo.
    copy env.example .env
    echo ✅ 已創建 .env 檔案，請編輯並填入您的 API 金鑰
    echo.
)

:: 顯示選單
:menu
echo 請選擇要啟動的應用程式:
echo.
echo 1. 🖥️  桌面應用程式 (Tkinter)
echo 2. 🌐  Web 應用程式 (Streamlit)
echo 3. 🧪  運行測試
echo 4. ❌  退出
echo.
set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" goto desktop_app
if "%choice%"=="2" goto web_app
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto exit
echo ❌ 無效選項，請重新選擇
goto menu

:desktop_app
echo.
echo 🖥️ 啟動桌面應用程式...
python webeye_food_app.py
goto end

:web_app
echo.
echo 🌐 啟動 Web 應用程式...
echo 📡 應用程式將在瀏覽器中開啟: http://localhost:8501
echo.
streamlit run streamlit_app.py
goto end

:run_tests
echo.
echo 🧪 運行系統測試...
python test_webeye_camera.py
echo.
pause
goto menu

:exit
echo.
echo 👋 感謝使用 WebEye 食物偵測系統！
goto end

:end
echo.
echo 按任意鍵退出...
pause >nul 