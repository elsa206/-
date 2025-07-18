#!/usr/bin/env python3
"""
FDA 營養資料庫系統測試腳本
測試 FDA 資料抓取和增強版食物偵測功能
"""

import os
import sys
import json
import tempfile
import numpy as np
from datetime import datetime

def test_imports():
    """測試模組導入"""
    print("🧪 測試模組導入...")
    
    try:
        import requests
        print("✅ requests 模組導入成功")
    except ImportError as e:
        print(f"❌ requests 模組導入失敗: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup 模組導入成功")
    except ImportError as e:
        print(f"❌ BeautifulSoup 模組導入失敗: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv 模組導入成功")
    except ImportError as e:
        print(f"❌ python-dotenv 模組導入失敗: {e}")
        return False
    
    return True

def test_fda_scraper():
    """測試 FDA 抓取器"""
    print("\n🧪 測試 FDA 抓取器...")
    
    try:
        from fda_nutrition_scraper import FDANutritionScraper
        
        scraper = FDANutritionScraper()
        print("✅ FDA 抓取器初始化成功")
        
        # 測試主頁面獲取
        soup = scraper.get_main_page()
        if soup:
            print("✅ 主頁面獲取成功")
        else:
            print("❌ 主頁面獲取失敗")
            return False
        
        # 測試 ViewState 提取
        viewstate_data = scraper.extract_viewstate(soup)
        if viewstate_data:
            print("✅ ViewState 提取成功")
        else:
            print("❌ ViewState 提取失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FDA 抓取器測試失敗: {e}")
        return False

def test_enhanced_food_detection():
    """測試增強版食物偵測"""
    print("\n🧪 測試增強版食物偵測...")
    
    try:
        from enhanced_food_detection import EnhancedFoodDetector
        
        # 測試初始化（不載入 FDA 資料庫）
        detector = EnhancedFoodDetector()
        print("✅ 增強版食物偵測器初始化成功")
        
        # 測試本地營養資料庫
        if detector.local_nutrition_db:
            print(f"✅ 本地營養資料庫載入成功 ({len(detector.local_nutrition_db)} 種食品)")
        else:
            print("❌ 本地營養資料庫載入失敗")
            return False
        
        # 測試食物關鍵字
        if detector.food_keywords:
            print(f"✅ 食物關鍵字載入成功 ({len(detector.food_keywords)} 個關鍵字)")
        else:
            print("❌ 食物關鍵字載入失敗")
            return False
        
        # 測試中文食物關鍵字
        if detector.chinese_food_keywords:
            print(f"✅ 中文食物關鍵字載入成功 ({len(detector.chinese_food_keywords)} 個關鍵字)")
        else:
            print("❌ 中文食物關鍵字載入失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 增強版食物偵測測試失敗: {e}")
        return False

def test_environment_variables():
    """測試環境變數"""
    print("\n🧪 測試環境變數...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # 檢查必要的環境變數
        azure_endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        azure_key = os.getenv('AZURE_VISION_KEY')
        
        if azure_endpoint and azure_endpoint != 'https://your-resource.cognitiveservices.azure.com/':
            print("✅ Azure Vision 端點設定正確")
        else:
            print("⚠️  Azure Vision 端點未設定或使用預設值")
        
        if azure_key and azure_key != 'your-azure-vision-key-here':
            print("✅ Azure Vision 金鑰設定正確")
        else:
            print("⚠️  Azure Vision 金鑰未設定或使用預設值")
        
        return True
        
    except Exception as e:
        print(f"❌ 環境變數測試失敗: {e}")
        return False

def test_data_structures():
    """測試資料結構"""
    print("\n🧪 測試資料結構...")
    
    try:
        # 測試營養資料庫格式
        test_nutrition_db = {
            "test_food": {
                "calories": 100,
                "protein": 5,
                "carbs": 20,
                "fat": 2,
                "fiber": 3,
                "vitamins": ["C", "B6"],
                "minerals": ["鈣", "鐵"],
                "source": "TEST",
                "original_name": "測試食品",
                "category": "測試類"
            }
        }
        
        # 測試 JSON 序列化
        json_str = json.dumps(test_nutrition_db, ensure_ascii=False, indent=2)
        parsed_db = json.loads(json_str)
        
        if parsed_db == test_nutrition_db:
            print("✅ 營養資料庫 JSON 序列化測試通過")
        else:
            print("❌ 營養資料庫 JSON 序列化測試失敗")
            return False
        
        # 測試檢測結果結構
        from enhanced_food_detection import EnhancedFoodDetectionResult
        
        result = EnhancedFoodDetectionResult()
        result.foods_detected = ["apple", "banana"]
        result.description = "測試描述"
        result.health_score = 85
        result.success = True
        
        if hasattr(result, 'foods_detected') and hasattr(result, 'health_score'):
            print("✅ 檢測結果結構測試通過")
        else:
            print("❌ 檢測結果結構測試失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 資料結構測試失敗: {e}")
        return False

def test_file_operations():
    """測試檔案操作"""
    print("\n🧪 測試檔案操作...")
    
    try:
        # 測試 JSON 檔案讀寫
        test_data = {
            "test": "data",
            "timestamp": datetime.now().isoformat()
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        # 讀取檔案
        with open(temp_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if loaded_data == test_data:
            print("✅ JSON 檔案讀寫測試通過")
        else:
            print("❌ JSON 檔案讀寫測試失敗")
            return False
        
        # 清理測試檔案
        os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 檔案操作測試失敗: {e}")
        return False

def test_network_connectivity():
    """測試網路連接"""
    print("\n🧪 測試網路連接...")
    
    try:
        import requests
        
        # 測試基本網路連接
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ 基本網路連接測試通過")
        else:
            print("❌ 基本網路連接測試失敗")
            return False
        
        # 測試 FDA 網站連接
        try:
            response = requests.get("https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178", timeout=10)
            if response.status_code == 200:
                print("✅ FDA 網站連接測試通過")
            else:
                print(f"⚠️  FDA 網站連接測試失敗 (狀態碼: {response.status_code})")
        except Exception as e:
            print(f"⚠️  FDA 網站連接測試失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 網路連接測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🍽️ FDA 營養資料庫系統測試")
    print("=" * 50)
    
    tests = [
        ("模組導入", test_imports),
        ("FDA 抓取器", test_fda_scraper),
        ("增強版食物偵測", test_enhanced_food_detection),
        ("環境變數", test_environment_variables),
        ("資料結構", test_data_structures),
        ("檔案操作", test_file_operations),
        ("網路連接", test_network_connectivity)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試發生錯誤: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統準備就緒")
        print("\n💡 下一步:")
        print("   1. 設定 Azure API 金鑰")
        print("   2. 執行 FDA 資料抓取: python run_fda_scraper.py")
        print("   3. 測試食物偵測功能")
    else:
        print("⚠️  部分測試失敗，請檢查錯誤訊息")
        print("\n🔧 故障排除:")
        print("   1. 安裝缺少的依賴: pip install -r requirements.txt")
        print("   2. 檢查環境變數設定")
        print("   3. 確認網路連接")

if __name__ == "__main__":
    main() 