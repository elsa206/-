#!/usr/bin/env python3
"""
FDA 資料抓取執行腳本
用於抓取台灣食品藥物管理署的營養資料庫
"""

import os
import sys
import time
from datetime import datetime

def main():
    """主函數"""
    print("🍽️ 台灣FDA食品營養成分資料庫抓取器")
    print("=" * 60)
    print("📋 此工具將抓取台灣食品藥物管理署的營養資料庫")
    print("🌐 資料來源: https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178")
    print("=" * 60)
    
    # 檢查依賴
    try:
        import requests
        from bs4 import BeautifulSoup
        print("✅ 依賴套件檢查通過")
    except ImportError as e:
        print(f"❌ 缺少依賴套件: {e}")
        print("請執行: pip install beautifulsoup4 lxml requests")
        return
    
    # 檢查是否已有FDA資料庫
    existing_files = []
    for file in os.listdir('.'):
        if file.startswith('fda_nutrition_db_') and file.endswith('.json'):
            existing_files.append(file)
    
    if existing_files:
        print(f"📁 發現現有FDA資料庫檔案:")
        for file in existing_files:
            print(f"   - {file}")
        
        choice = input("\n是否要重新抓取資料？(y/N): ").lower()
        if choice != 'y':
            print("使用現有資料庫檔案")
            return
    
    # 執行抓取
    try:
        from fda_nutrition_scraper import FDANutritionScraper
        
        scraper = FDANutritionScraper()
        
        print("\n🚀 開始抓取資料...")
        print("⚠️  注意: 此過程可能需要較長時間，請耐心等待")
        print("📊 建議: 首次使用建議抓取少量資料進行測試")
        
        # 詢問抓取設定
        max_pages = input("請輸入要抓取的頁數 (建議 5-10): ")
        try:
            max_pages = int(max_pages)
        except ValueError:
            max_pages = 5
            print(f"使用預設值: {max_pages} 頁")
        
        max_details = input("請輸入要抓取詳細資訊的食品數量 (建議 20-50): ")
        try:
            max_details = int(max_details)
        except ValueError:
            max_details = 20
            print(f"使用預設值: {max_details} 種食品")
        
        print(f"\n📋 設定: 抓取 {max_pages} 頁基本資料，{max_details} 種詳細營養資訊")
        
        # 確認開始
        confirm = input("\n是否開始抓取？(Y/n): ").lower()
        if confirm == 'n':
            print("取消抓取")
            return
        
        # 開始抓取
        start_time = time.time()
        
        print("\n📋 步驟 1: 抓取食品基本資料...")
        foods = scraper.scrape_all_foods(max_pages=max_pages)
        
        if not foods:
            print("❌ 未抓取到任何基本資料")
            return
        
        print(f"✅ 成功抓取 {len(foods)} 筆基本資料")
        
        # 儲存基本資料
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        basic_json = f"fda_foods_basic_{timestamp}.json"
        basic_csv = f"fda_foods_basic_{timestamp}.csv"
        
        scraper.save_to_json(foods, basic_json)
        scraper.save_to_csv(foods, basic_csv)
        
        print(f"💾 基本資料已儲存: {basic_json}, {basic_csv}")
        
        # 抓取詳細資訊
        print(f"\n🔍 步驟 2: 抓取 {max_details} 種食品的詳細營養資訊...")
        print("⏱️  此步驟需要較長時間，請耐心等待...")
        
        detailed_foods = scraper.scrape_food_details(foods, max_details=max_details)
        
        if detailed_foods:
            # 儲存詳細資料
            detailed_json = f"fda_foods_detailed_{timestamp}.json"
            detailed_csv = f"fda_foods_detailed_{timestamp}.csv"
            
            scraper.save_to_json(detailed_foods, detailed_json)
            scraper.save_to_csv(detailed_foods, detailed_csv)
            
            print(f"💾 詳細資料已儲存: {detailed_json}, {detailed_csv}")
            
            # 轉換為營養資料庫格式
            print("\n🔄 步驟 3: 轉換為營養資料庫格式...")
            nutrition_db = scraper.convert_to_nutrition_db(detailed_foods)
            
            if nutrition_db:
                nutrition_json = f"fda_nutrition_db_{timestamp}.json"
                scraper.save_to_json(nutrition_json, nutrition_db)
                print(f"💾 營養資料庫已儲存: {nutrition_json}")
                print(f"✅ 成功建立營養資料庫，包含 {len(nutrition_db)} 種食品")
            
            # 計算執行時間
            elapsed_time = time.time() - start_time
            print(f"\n⏱️  總執行時間: {elapsed_time:.1f} 秒")
            
            print("\n🎉 資料抓取完成！")
            print("\n📁 生成的檔案:")
            print(f"   - {basic_json} (基本資料)")
            print(f"   - {basic_csv} (基本資料 CSV)")
            print(f"   - {detailed_json} (詳細資料)")
            print(f"   - {detailed_csv} (詳細資料 CSV)")
            if nutrition_db:
                print(f"   - {nutrition_json} (營養資料庫)")
            
            print("\n💡 使用建議:")
            print("   1. 將營養資料庫檔案複製到專案目錄")
            print("   2. 在 enhanced_food_detection.py 中指定資料庫路徑")
            print("   3. 重新啟動應用程式以使用新的營養資料")
            
        else:
            print("❌ 未抓取到詳細營養資訊")
    
    except KeyboardInterrupt:
        print("\n⏹️ 抓取被使用者中斷")
    except Exception as e:
        print(f"\n❌ 抓取過程中發生錯誤: {e}")
        print("請檢查網路連接和網站狀態")

def show_usage():
    """顯示使用說明"""
    print("""
📖 使用說明:

1. 基本使用:
   python run_fda_scraper.py

2. 注意事項:
   - 需要穩定的網路連接
   - 抓取過程可能需要較長時間
   - 建議先抓取少量資料進行測試
   - 請遵守網站的使用條款

3. 輸出檔案:
   - fda_foods_basic_*.json: 基本食品資料
   - fda_foods_detailed_*.json: 詳細營養資料
   - fda_nutrition_db_*.json: 營養資料庫 (用於WebEye系統)

4. 整合到WebEye系統:
   - 將 fda_nutrition_db_*.json 複製到專案目錄
   - 修改 enhanced_food_detection.py 中的資料庫路徑
   - 重新啟動應用程式

5. 故障排除:
   - 如果抓取失敗，請檢查網路連接
   - 如果網站結構改變，可能需要更新抓取器
   - 如果檔案損壞，請重新抓取
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
    else:
        main() 