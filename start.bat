@echo off
chcp 65001 >nul
echo 🍽️ USDA 食物熱量抓取器
echo ================================
echo.
echo 請選擇要執行的程式：
echo.
echo 1. 快速測試 (測試API連接)
echo 2. 熱量查詢工具 (互動式查詢)
echo 3. 簡化熱量提取器 (抓取熱量資料)
echo 4. 完整抓取器 (完整功能)
echo 5. 安裝依賴套件
echo 6. 退出
echo.
set /p choice=請輸入選項 (1-6): 

if "%choice%"=="1" (
    echo.
    echo 🚀 執行快速測試...
    python quick_usda_test.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo 🔍 啟動熱量查詢工具...
    python usda_calorie_lookup.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo 📊 執行簡化熱量提取器...
    python simple_usda_calories.py
    pause
) else if "%choice%"=="4" (
    echo.
    echo 🌟 執行完整抓取器...
    python usda_food_scraper.py
    pause
) else if "%choice%"=="5" (
    echo.
    echo 📦 安裝依賴套件...
    pip install -r requirements.txt
    echo.
    echo ✅ 安裝完成！
    pause
) else if "%choice%"=="6" (
    echo.
    echo 👋 再見！
    exit /b 0
) else (
    echo.
    echo ❌ 無效的選項，請重新選擇
    pause
    goto :eof
) 