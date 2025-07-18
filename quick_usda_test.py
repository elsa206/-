#!/usr/bin/env python3
"""
USDA 快速測試版本
用於快速測試USDA API連接和基本功能
"""

import requests
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class QuickUSDAFood:
    """快速USDA食物資料結構"""
    food_name: str
    energy_kcal: float
    category: str

class QuickUSDATester:
    """快速USDA測試器"""
    
    def __init__(self):
        """初始化測試器"""
        self.api_base = "https://api.nal.usda.gov/fdc/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 測試用的食物關鍵字
        self.test_keywords = [
            'apple', 'banana', 'chicken', 'rice', 'milk', 'bread'
        ]
    
    def test_api_connection(self) -> bool:
        """測試API連接"""
        try:
            print("🔗 測試USDA API連接...")
            
            url = f"{self.api_base}/foods/search"
            params = {
                'api_key': 'DEMO_KEY',
                'query': 'apple',
                'pageSize': 1,
                'pageNumber': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'foods' in data and len(data['foods']) > 0:
                print("✅ API連接成功！")
                return True
            else:
                print("❌ API回應格式異常")
                return False
                
        except Exception as e:
            print(f"❌ API連接失敗: {e}")
            return False
    
    def test_food_search(self, keyword: str) -> Optional[Dict]:
        """測試食物搜尋"""
        try:
            url = f"{self.api_base}/foods/search"
            params = {
                'api_key': 'DEMO_KEY',
                'query': keyword,
                'pageSize': 5,
                'pageNumber': 1,
                'dataType': ['Foundation', 'SR Legacy']
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ 搜尋失敗 ({keyword}): {e}")
            return None
    
    def test_food_details(self, fdc_id: str) -> Optional[Dict]:
        """測試食物詳細資訊獲取"""
        try:
            url = f"{self.api_base}/food/{fdc_id}"
            params = {
                'api_key': 'DEMO_KEY',
                'format': 'full',
                'nutrients': '208'  # 熱量
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ 獲取詳細資訊失敗 (FDC ID: {fdc_id}): {e}")
            return None
    
    def extract_energy(self, food_details: Dict) -> Optional[float]:
        """提取熱量值"""
        try:
            if 'foodNutrients' in food_details:
                for nutrient in food_details['foodNutrients']:
                    # 檢查營養素ID
                    if nutrient.get('nutrient', {}).get('id') == 208:
                        return nutrient.get('amount', 0)
                    
                    # 也檢查營養素名稱
                    nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                    if 'energy' in nutrient_name or 'calories' in nutrient_name:
                        return nutrient.get('amount', 0)
            
            # 如果沒有找到，嘗試其他可能的營養素ID
            if 'foodNutrients' in food_details:
                for nutrient in food_details['foodNutrients']:
                    nutrient_id = nutrient.get('nutrient', {}).get('id')
                    if nutrient_id in [1008, 1009, 1010]:  # 其他可能的能量ID
                        return nutrient.get('amount', 0)
            
            return None
            
        except Exception as e:
            print(f"❌ 提取熱量失敗: {e}")
            return None
    
    def test_single_food(self, keyword: str) -> Optional[QuickUSDAFood]:
        """測試單個食物的完整流程"""
        try:
            print(f"\n🍎 測試食物: {keyword}")
            
            # 1. 搜尋食物
            search_result = self.test_food_search(keyword)
            if not search_result or 'foods' not in search_result:
                print(f"  ❌ 搜尋失敗")
                return None
            
            foods = search_result['foods']
            if not foods:
                print(f"  ❌ 未找到食物")
                return None
            
            # 2. 獲取第一個結果的詳細資訊
            first_food = foods[0]
            fdc_id = str(first_food.get('fdcId', ''))
            food_name = first_food.get('description', '').strip()
            
            print(f"  📝 食物名稱: {food_name}")
            print(f"  🆔 FDC ID: {fdc_id}")
            
            # 3. 獲取詳細資訊
            food_details = self.test_food_details(fdc_id)
            if not food_details:
                print(f"  ❌ 獲取詳細資訊失敗")
                return None
            
            # 4. 提取熱量
            energy_kcal = self.extract_energy(food_details)
            if energy_kcal is None:
                print(f"  ❌ 提取熱量失敗")
                return None
            
            print(f"  🔥 熱量: {energy_kcal:.1f} kcal")
            
            # 5. 分類
            category = self.categorize_food(food_name)
            print(f"  📂 分類: {category}")
            
            return QuickUSDAFood(
                food_name=food_name,
                energy_kcal=energy_kcal,
                category=category
            )
            
        except Exception as e:
            print(f"  ❌ 測試失敗: {e}")
            return None
    
    def categorize_food(self, food_name: str) -> str:
        """簡單的食物分類"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['apple', 'banana', 'orange', 'grape']):
            return 'fruits'
        elif any(word in food_name_lower for word in ['chicken', 'beef', 'pork', 'fish']):
            return 'proteins'
        elif any(word in food_name_lower for word in ['rice', 'bread', 'pasta']):
            return 'grains'
        elif any(word in food_name_lower for word in ['milk', 'cheese', 'yogurt']):
            return 'dairy'
        else:
            return 'other'
    
    def run_quick_test(self):
        """執行快速測試"""
        print("🚀 USDA 快速測試")
        print("=" * 40)
        
        # 1. 測試API連接
        if not self.test_api_connection():
            print("❌ API連接失敗，無法繼續測試")
            return
        
        # 2. 測試多個食物
        test_results = []
        
        for keyword in self.test_keywords:
            food = self.test_single_food(keyword)
            if food:
                test_results.append(food)
            
            # 請求間隔
            time.sleep(1)
        
        # 3. 顯示測試結果
        print(f"\n📊 測試結果:")
        print(f"  成功測試: {len(test_results)}/{len(self.test_keywords)} 個食物")
        
        if test_results:
            print(f"\n🍽️ 測試成功的食物:")
            for i, food in enumerate(test_results, 1):
                print(f"  {i}. {food.food_name} - {food.energy_kcal:.1f} kcal ({food.category})")
            
            # 計算統計
            total_energy = sum(food.energy_kcal for food in test_results)
            avg_energy = total_energy / len(test_results)
            
            print(f"\n📈 統計資訊:")
            print(f"  平均熱量: {avg_energy:.1f} kcal")
            print(f"  總熱量: {total_energy:.1f} kcal")
        
        print(f"\n✅ 快速測試完成！")

def main():
    """主函數"""
    tester = QuickUSDATester()
    tester.run_quick_test()

if __name__ == "__main__":
    main() 