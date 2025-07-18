#!/usr/bin/env python3
"""
USDA 簡化熱量提取器
專門提取美國農業部食物資料庫中的食物名稱和熱量資訊
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import pandas as pd
from tqdm import tqdm

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimpleUSDAFood:
    """簡化USDA食物資料結構"""
    food_name: str
    energy_kcal: float
    category: str
    fdc_id: str

class SimpleUSDACalorieExtractor:
    """簡化USDA熱量提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.api_base = "https://api.nal.usda.gov/fdc/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 設定請求參數
        self.request_delay = 1.0
        self.timeout = 30
        
        # 常見食物關鍵字
        self.food_keywords = [
            # 水果類
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 
            'peach', 'pear', 'mango', 'pineapple', 'watermelon', 'kiwi',
            
            # 蔬菜類
            'carrot', 'broccoli', 'tomato', 'lettuce', 'spinach', 'onion', 
            'potato', 'corn', 'cucumber', 'bell pepper', 'mushroom', 'garlic',
            
            # 穀物類
            'rice', 'bread', 'pasta', 'noodle', 'oat', 'wheat', 'barley', 
            'quinoa', 'cornmeal', 'flour', 'cereal', 'cracker',
            
            # 蛋白質類
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'egg', 
            'tofu', 'turkey', 'lamb', 'tuna', 'cod',
            
            # 乳製品類
            'milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream', 
            'cottage cheese', 'sour cream', 'whipping cream',
            
            # 堅果類
            'almond', 'peanut', 'walnut', 'cashew', 'pistachio', 'pecan', 
            'hazelnut', 'macadamia', 'pine nut', 'sunflower seed',
            
            # 飲料類
            'coffee', 'tea', 'juice', 'soda', 'water', 'milk', 'smoothie', 
            'energy drink', 'sports drink', 'hot chocolate',
            
            # 零食類
            'chips', 'popcorn', 'nuts', 'candy', 'chocolate', 'cookie', 
            'cracker', 'pretzel', 'trail mix', 'granola bar',
            
            # 甜點類
            'cake', 'pie', 'ice cream', 'chocolate', 'cookie', 'brownie', 
            'pudding', 'custard', 'cheesecake', 'donut',
            
            # 調味料類
            'sauce', 'dressing', 'mayonnaise', 'ketchup', 'mustard', 'soy sauce', 
            'hot sauce', 'vinegar', 'oil', 'butter'
        ]
        
        # 食物分類對應
        self.category_mapping = {
            'apple': 'fruits', 'banana': 'fruits', 'orange': 'fruits', 'grape': 'fruits',
            'strawberry': 'fruits', 'blueberry': 'fruits', 'peach': 'fruits', 'pear': 'fruits',
            'mango': 'fruits', 'pineapple': 'fruits', 'watermelon': 'fruits', 'kiwi': 'fruits',
            
            'carrot': 'vegetables', 'broccoli': 'vegetables', 'tomato': 'vegetables', 'lettuce': 'vegetables',
            'spinach': 'vegetables', 'onion': 'vegetables', 'potato': 'vegetables', 'corn': 'vegetables',
            'cucumber': 'vegetables', 'bell pepper': 'vegetables', 'mushroom': 'vegetables', 'garlic': 'vegetables',
            
            'rice': 'grains', 'bread': 'grains', 'pasta': 'grains', 'noodle': 'grains',
            'oat': 'grains', 'wheat': 'grains', 'barley': 'grains', 'quinoa': 'grains',
            'cornmeal': 'grains', 'flour': 'grains', 'cereal': 'grains', 'cracker': 'grains',
            
            'chicken': 'proteins', 'beef': 'proteins', 'pork': 'proteins', 'fish': 'proteins',
            'salmon': 'proteins', 'shrimp': 'proteins', 'egg': 'proteins', 'tofu': 'proteins',
            'turkey': 'proteins', 'lamb': 'proteins', 'tuna': 'proteins', 'cod': 'proteins',
            
            'milk': 'dairy', 'cheese': 'dairy', 'yogurt': 'dairy', 'butter': 'dairy',
            'cream': 'dairy', 'ice cream': 'dairy', 'cottage cheese': 'dairy', 'sour cream': 'dairy',
            
            'almond': 'nuts', 'peanut': 'nuts', 'walnut': 'nuts', 'cashew': 'nuts',
            'pistachio': 'nuts', 'pecan': 'nuts', 'hazelnut': 'nuts', 'macadamia': 'nuts',
            
            'coffee': 'beverages', 'tea': 'beverages', 'juice': 'beverages', 'soda': 'beverages',
            'water': 'beverages', 'smoothie': 'beverages', 'energy drink': 'beverages',
            
            'chips': 'snacks', 'popcorn': 'snacks', 'candy': 'snacks', 'cookie': 'snacks',
            'pretzel': 'snacks', 'trail mix': 'snacks', 'granola bar': 'snacks',
            
            'cake': 'desserts', 'pie': 'desserts', 'brownie': 'desserts', 'pudding': 'desserts',
            'custard': 'desserts', 'cheesecake': 'desserts', 'donut': 'desserts',
            
            'sauce': 'condiments', 'dressing': 'condiments', 'mayonnaise': 'condiments',
            'ketchup': 'condiments', 'mustard': 'condiments', 'soy sauce': 'condiments'
        }
    
    def search_foods(self, query: str, page_size: int = 25) -> Optional[Dict]:
        """
        搜尋食物
        
        Args:
            query: 搜尋關鍵字
            page_size: 每頁結果數量
            
        Returns:
            搜尋結果字典
        """
        try:
            url = f"{self.api_base}/foods/search"
            params = {
                'api_key': 'DEMO_KEY',
                'query': query,
                'pageSize': page_size,
                'pageNumber': 1,
                'dataType': ['Foundation', 'SR Legacy'],
                'sortBy': 'dataType.keyword',
                'sortOrder': 'asc'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"搜尋食物失敗 ({query}): {e}")
            return None
    
    def get_food_details(self, fdc_id: str) -> Optional[Dict]:
        """
        獲取食物詳細資訊
        
        Args:
            fdc_id: 食物ID
            
        Returns:
            食物詳細資訊字典
        """
        try:
            url = f"{self.api_base}/food/{fdc_id}"
            params = {
                'api_key': 'DEMO_KEY',
                'format': 'full',
                'nutrients': '208'  # 只獲取熱量資料
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"獲取食物詳細資訊失敗 (FDC ID: {fdc_id}): {e}")
            return None
    
    def extract_energy_value(self, food_details: Dict) -> Optional[float]:
        """
        從食物詳細資訊中提取熱量值
        
        Args:
            food_details: 食物詳細資訊
            
        Returns:
            熱量值 (kcal)
        """
        try:
            if 'foodNutrients' in food_details:
                for nutrient in food_details['foodNutrients']:
                    # 營養素ID 208 是能量 (kcal)
                    if nutrient.get('nutrient', {}).get('id') == 208:
                        return nutrient.get('amount', 0)
                    
                    # 也檢查營養素名稱
                    nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                    if 'energy' in nutrient_name or 'calories' in nutrient_name:
                        return nutrient.get('amount', 0)
            
            return None
            
        except Exception as e:
            logger.error(f"提取熱量值失敗: {e}")
            return None
    
    def categorize_food(self, food_name: str) -> str:
        """
        對食物進行分類
        
        Args:
            food_name: 食物名稱
            
        Returns:
            食物分類
        """
        food_name_lower = food_name.lower()
        
        for keyword, category in self.category_mapping.items():
            if keyword in food_name_lower:
                return category
        
        return "other"
    
    def extract_food_calories(self, keyword: str, max_results: int = 5) -> List[SimpleUSDAFood]:
        """
        提取特定關鍵字的食物熱量資料
        
        Args:
            keyword: 搜尋關鍵字
            max_results: 最大結果數量
            
        Returns:
            食物熱量資料列表
        """
        foods = []
        
        try:
            # 搜尋食物
            search_result = self.search_foods(keyword)
            
            if not search_result or 'foods' not in search_result:
                return foods
            
            # 處理搜尋結果
            for food_data in search_result['foods'][:max_results]:
                try:
                    fdc_id = str(food_data.get('fdcId', ''))
                    food_name = food_data.get('description', '').strip()
                    
                    if not food_name:
                        continue
                    
                    # 獲取詳細資訊以提取熱量
                    food_details = self.get_food_details(fdc_id)
                    energy_kcal = 0.0
                    
                    if food_details:
                        energy_kcal = self.extract_energy_value(food_details) or 0.0
                    
                    # 只保留有熱量資料的食物
                    if energy_kcal > 0:
                        category = self.categorize_food(food_name)
                        
                        food_item = SimpleUSDAFood(
                            food_name=food_name,
                            energy_kcal=energy_kcal,
                            category=category,
                            fdc_id=fdc_id
                        )
                        foods.append(food_item)
                
                except Exception as e:
                    logger.error(f"處理食物項目失敗: {e}")
                    continue
            
            # 請求間隔
            time.sleep(self.request_delay)
            
        except Exception as e:
            logger.error(f"提取關鍵字 {keyword} 失敗: {e}")
        
        return foods
    
    def extract_all_calories(self, max_results_per_keyword: int = 3) -> List[SimpleUSDAFood]:
        """
        提取所有關鍵字的食物熱量資料
        
        Args:
            max_results_per_keyword: 每個關鍵字的最大結果數量
            
        Returns:
            所有食物熱量資料列表
        """
        logger.info("開始提取USDA食物熱量資料...")
        
        all_foods = []
        
        for keyword in tqdm(self.food_keywords, desc="提取食物熱量"):
            try:
                foods = self.extract_food_calories(keyword, max_results_per_keyword)
                all_foods.extend(foods)
                
            except Exception as e:
                logger.error(f"提取關鍵字 {keyword} 失敗: {e}")
                continue
        
        # 去重
        unique_foods = self.remove_duplicates(all_foods)
        
        logger.info(f"提取完成，共 {len(unique_foods)} 個唯一食物項目")
        return unique_foods
    
    def remove_duplicates(self, foods: List[SimpleUSDAFood]) -> List[SimpleUSDAFood]:
        """
        移除重複的食物項目
        
        Args:
            foods: 食物項目列表
            
        Returns:
            去重後的食物項目列表
        """
        seen_names = set()
        unique_foods = []
        
        for food in foods:
            # 標準化食物名稱
            normalized_name = food.food_name.lower().strip()
            
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_foods.append(food)
        
        return unique_foods
    
    def search_food_by_name(self, food_name: str) -> Optional[SimpleUSDAFood]:
        """
        根據名稱搜尋食物熱量
        
        Args:
            food_name: 食物名稱
            
        Returns:
            食物熱量資料或None
        """
        try:
            foods = self.extract_food_calories(food_name, max_results=1)
            
            if foods:
                return foods[0]
            
            return None
            
        except Exception as e:
            logger.error(f"搜尋食物 {food_name} 失敗: {e}")
            return None
    
    def save_to_csv(self, foods: List[SimpleUSDAFood], filename: str = "usda_calories.csv"):
        """
        儲存為CSV檔案
        
        Args:
            foods: 食物項目列表
            filename: 檔案名稱
        """
        try:
            data = []
            for food in foods:
                data.append({
                    'food_name': food.food_name,
                    'energy_kcal': food.energy_kcal,
                    'category': food.category,
                    'fdc_id': food.fdc_id
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            
            logger.info(f"資料已儲存為 CSV: {filename}")
            
        except Exception as e:
            logger.error(f"儲存CSV失敗: {e}")
    
    def save_to_json(self, foods: List[SimpleUSDAFood], filename: str = "usda_calories.json"):
        """
        儲存為JSON檔案
        
        Args:
            foods: 食物項目列表
            filename: 檔案名稱
        """
        try:
            data = {
                'metadata': {
                    'source': 'USDA FoodData Central',
                    'url': 'https://fdc.nal.usda.gov/',
                    'extracted_at': datetime.now().isoformat(),
                    'total_foods': len(foods)
                },
                'foods': []
            }
            
            for food in foods:
                food_dict = {
                    'food_name': food.food_name,
                    'energy_kcal': food.energy_kcal,
                    'category': food.category,
                    'fdc_id': food.fdc_id
                }
                data['foods'].append(food_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"資料已儲存為 JSON: {filename}")
            
        except Exception as e:
            logger.error(f"儲存JSON失敗: {e}")
    
    def get_statistics(self, foods: List[SimpleUSDAFood]) -> Dict:
        """
        獲取統計資訊
        
        Args:
            foods: 食物項目列表
            
        Returns:
            統計資訊字典
        """
        if not foods:
            return {}
        
        # 分類統計
        category_counts = {}
        for food in foods:
            category_counts[food.category] = category_counts.get(food.category, 0) + 1
        
        # 熱量統計
        energies = [food.energy_kcal for food in foods if food.energy_kcal > 0]
        
        stats = {
            'total_foods': len(foods),
            'foods_with_energy': len(energies),
            'average_energy': sum(energies) / len(energies) if energies else 0,
            'min_energy': min(energies) if energies else 0,
            'max_energy': max(energies) if energies else 0,
            'category_distribution': category_counts
        }
        
        return stats
    
    def interactive_search(self):
        """互動式搜尋功能"""
        print("🔍 USDA 食物熱量搜尋器")
        print("輸入 'quit' 退出")
        print("-" * 40)
        
        while True:
            try:
                query = input("\n請輸入食物名稱: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("再見！")
                    break
                
                if not query:
                    print("請輸入有效的食物名稱")
                    continue
                
                print(f"搜尋中: {query}...")
                food = self.search_food_by_name(query)
                
                if food:
                    print(f"✅ 找到食物: {food.food_name}")
                    print(f"  熱量: {food.energy_kcal:.1f} kcal")
                    print(f"  分類: {food.category}")
                    print(f"  FDC ID: {food.fdc_id}")
                else:
                    print(f"❌ 未找到食物: {query}")
                
            except KeyboardInterrupt:
                print("\n再見！")
                break
            except Exception as e:
                print(f"搜尋失敗: {e}")

def main():
    """主函數"""
    print("🍽️ USDA 簡化熱量提取器")
    print("=" * 40)
    
    # 創建提取器
    extractor = SimpleUSDACalorieExtractor()
    
    try:
        # 提取所有食物熱量資料
        print("開始提取食物熱量資料...")
        foods = extractor.extract_all_calories(max_results_per_keyword=2)
        
        if not foods:
            print("❌ 未提取到任何食物資料")
            return
        
        # 顯示統計資訊
        stats = extractor.get_statistics(foods)
        print(f"\n📊 統計資訊:")
        print(f"  總食物數量: {stats['total_foods']}")
        print(f"  有熱量資料的食物: {stats['foods_with_energy']}")
        print(f"  平均熱量: {stats['average_energy']:.1f} kcal")
        print(f"  熱量範圍: {stats['min_energy']:.1f} - {stats['max_energy']:.1f} kcal")
        
        print(f"\n📂 分類分布:")
        for category, count in stats['category_distribution'].items():
            print(f"  {category}: {count} 個")
        
        # 儲存資料
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        csv_filename = f"usda_calories_{timestamp}.csv"
        json_filename = f"usda_calories_{timestamp}.json"
        
        extractor.save_to_csv(foods, csv_filename)
        extractor.save_to_json(foods, json_filename)
        
        print(f"\n✅ 提取完成！")
        print(f"  CSV檔案: {csv_filename}")
        print(f"  JSON檔案: {json_filename}")
        
        # 顯示前10個食物項目
        print(f"\n🍎 前10個食物項目:")
        for i, food in enumerate(foods[:10], 1):
            print(f"  {i}. {food.food_name} - {food.energy_kcal:.1f} kcal ({food.category})")
        
        # 詢問是否啟動互動式搜尋
        choice = input(f"\n是否啟動互動式搜尋？(y/n): ").lower().strip()
        if choice == 'y':
            extractor.interactive_search()
        
    except KeyboardInterrupt:
        print("\n⏹️ 提取被使用者中斷")
    except Exception as e:
        print(f"\n❌ 提取失敗: {e}")

if __name__ == "__main__":
    main() 