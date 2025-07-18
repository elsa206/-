#!/usr/bin/env python3
"""
USDA FoodData Central 食物資料抓取器
專門用於抓取美國農業部食物資料庫中的食物名稱和熱量資訊
"""

import requests
import json
import time
import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
import pandas as pd
from tqdm import tqdm

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class USDAFoodItem:
    """USDA 食物項目資料結構"""
    fdc_id: str
    food_name: str
    energy_kcal: float
    category: str
    brand_owner: Optional[str] = None
    data_type: str = "Foundation"
    description: Optional[str] = None
    ingredients: Optional[str] = None
    serving_size: Optional[float] = None
    serving_unit: Optional[str] = None

class USDAScraper:
    """USDA FoodData Central 抓取器"""
    
    def __init__(self):
        """初始化抓取器"""
        self.base_url = "https://fdc.nal.usda.gov"
        self.api_base = "https://api.nal.usda.gov/fdc/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 設定請求參數
        self.request_delay = 1.0  # 請求間隔
        self.max_retries = 3
        self.timeout = 30
        
        # 資料儲存
        self.foods_data = []
        self.categories = set()
        
        # 常見食物分類
        self.food_categories = {
            'fruits': ['apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'peach', 'pear'],
            'vegetables': ['carrot', 'broccoli', 'tomato', 'lettuce', 'spinach', 'onion', 'potato', 'corn'],
            'grains': ['rice', 'bread', 'pasta', 'noodle', 'oat', 'wheat', 'corn', 'barley'],
            'proteins': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'shrimp', 'egg', 'tofu'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'ice cream'],
            'nuts': ['almond', 'peanut', 'walnut', 'cashew', 'pistachio'],
            'beverages': ['coffee', 'tea', 'juice', 'soda', 'water', 'milk'],
            'snacks': ['chips', 'crackers', 'popcorn', 'nuts', 'candy'],
            'desserts': ['cake', 'cookie', 'pie', 'ice cream', 'chocolate'],
            'condiments': ['sauce', 'dressing', 'mayonnaise', 'ketchup', 'mustard']
        }
    
    def search_foods(self, query: str, page_size: int = 50, page_number: int = 1) -> Optional[Dict]:
        """
        搜尋食物
        
        Args:
            query: 搜尋關鍵字
            page_size: 每頁結果數量
            page_number: 頁碼
            
        Returns:
            搜尋結果字典
        """
        try:
            url = f"{self.api_base}/foods/search"
            params = {
                'api_key': 'DEMO_KEY',  # 使用演示API金鑰
                'query': query,
                'pageSize': page_size,
                'pageNumber': page_number,
                'dataType': ['Foundation', 'SR Legacy', 'Survey (FNDDS)'],
                'sortBy': 'dataType.keyword',
                'sortOrder': 'asc'
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"搜尋食物失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析搜尋結果失敗: {e}")
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
                'nutrients': '203,204,205,208'  # 蛋白質、脂肪、碳水化合物、熱量
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"獲取食物詳細資訊失敗 (FDC ID: {fdc_id}): {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析食物詳細資訊失敗 (FDC ID: {fdc_id}): {e}")
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
            # 查找營養素資訊
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
    
    def categorize_food(self, food_name: str, description: str = "") -> str:
        """
        對食物進行分類
        
        Args:
            food_name: 食物名稱
            description: 食物描述
            
        Returns:
            食物分類
        """
        text = f"{food_name} {description}".lower()
        
        for category, keywords in self.food_categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return "other"
    
    def parse_food_item(self, food_data: Dict) -> Optional[USDAFoodItem]:
        """
        解析食物項目資料
        
        Args:
            food_data: 食物資料字典
            
        Returns:
            USDA食物項目物件
        """
        try:
            fdc_id = str(food_data.get('fdcId', ''))
            food_name = food_data.get('description', '').strip()
            brand_owner = food_data.get('brandOwner', '')
            data_type = food_data.get('dataType', 'Foundation')
            
            # 獲取詳細資訊以提取熱量
            food_details = self.get_food_details(fdc_id)
            energy_kcal = 0.0
            
            if food_details:
                energy_kcal = self.extract_energy_value(food_details) or 0.0
                
                # 更新描述
                description = food_details.get('description', food_name)
                ingredients = food_details.get('ingredients', '')
                
                # 提取份量資訊
                serving_size = None
                serving_unit = None
                if 'servingSize' in food_details:
                    serving_size = food_details['servingSize']
                if 'servingSizeUnit' in food_details:
                    serving_unit = food_details['servingSizeUnit']
            
            # 分類食物
            category = self.categorize_food(food_name, description or '')
            
            return USDAFoodItem(
                fdc_id=fdc_id,
                food_name=food_name,
                energy_kcal=energy_kcal,
                category=category,
                brand_owner=brand_owner,
                data_type=data_type,
                description=description,
                ingredients=ingredients,
                serving_size=serving_size,
                serving_unit=serving_unit
            )
            
        except Exception as e:
            logger.error(f"解析食物項目失敗: {e}")
            return None
    
    def scrape_category(self, category_name: str, keywords: List[str], max_items: int = 100) -> List[USDAFoodItem]:
        """
        抓取特定分類的食物
        
        Args:
            category_name: 分類名稱
            keywords: 搜尋關鍵字列表
            max_items: 最大項目數量
            
        Returns:
            食物項目列表
        """
        logger.info(f"開始抓取 {category_name} 分類...")
        
        category_foods = []
        
        for keyword in tqdm(keywords, desc=f"抓取 {category_name}"):
            try:
                # 搜尋食物
                search_result = self.search_foods(keyword, page_size=25, page_number=1)
                
                if not search_result or 'foods' not in search_result:
                    continue
                
                foods = search_result['foods']
                
                for food_data in foods[:10]:  # 每個關鍵字最多取10個結果
                    food_item = self.parse_food_item(food_data)
                    
                    if food_item and food_item.energy_kcal > 0:
                        food_item.category = category_name
                        category_foods.append(food_item)
                        
                        if len(category_foods) >= max_items:
                            break
                
                # 請求間隔
                time.sleep(self.request_delay)
                
                if len(category_foods) >= max_items:
                    break
                    
            except Exception as e:
                logger.error(f"抓取關鍵字 {keyword} 失敗: {e}")
                continue
        
        logger.info(f"{category_name} 分類抓取完成，共 {len(category_foods)} 個項目")
        return category_foods
    
    def scrape_all_categories(self, max_items_per_category: int = 50) -> List[USDAFoodItem]:
        """
        抓取所有分類的食物
        
        Args:
            max_items_per_category: 每個分類的最大項目數量
            
        Returns:
            所有食物項目列表
        """
        logger.info("開始抓取所有分類的食物資料...")
        
        all_foods = []
        
        for category_name, keywords in self.food_categories.items():
            try:
                category_foods = self.scrape_category(category_name, keywords, max_items_per_category)
                all_foods.extend(category_foods)
                
                # 分類間隔
                time.sleep(self.request_delay * 2)
                
            except Exception as e:
                logger.error(f"抓取分類 {category_name} 失敗: {e}")
                continue
        
        # 去重
        unique_foods = self.remove_duplicates(all_foods)
        
        logger.info(f"所有分類抓取完成，共 {len(unique_foods)} 個唯一項目")
        return unique_foods
    
    def remove_duplicates(self, foods: List[USDAFoodItem]) -> List[USDAFoodItem]:
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
            normalized_name = re.sub(r'[^\w\s]', '', food.food_name.lower()).strip()
            
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_foods.append(food)
        
        return unique_foods
    
    def save_to_csv(self, foods: List[USDAFoodItem], filename: str = "usda_foods.csv"):
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
                    'fdc_id': food.fdc_id,
                    'food_name': food.food_name,
                    'energy_kcal': food.energy_kcal,
                    'category': food.category,
                    'brand_owner': food.brand_owner or '',
                    'data_type': food.data_type,
                    'description': food.description or '',
                    'ingredients': food.ingredients or '',
                    'serving_size': food.serving_size or '',
                    'serving_unit': food.serving_unit or ''
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            
            logger.info(f"資料已儲存為 CSV: {filename}")
            
        except Exception as e:
            logger.error(f"儲存CSV失敗: {e}")
    
    def save_to_json(self, foods: List[USDAFoodItem], filename: str = "usda_foods.json"):
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
                    'scraped_at': datetime.now().isoformat(),
                    'total_items': len(foods)
                },
                'foods': []
            }
            
            for food in foods:
                food_dict = {
                    'fdc_id': food.fdc_id,
                    'food_name': food.food_name,
                    'energy_kcal': food.energy_kcal,
                    'category': food.category,
                    'brand_owner': food.brand_owner,
                    'data_type': food.data_type,
                    'description': food.description,
                    'ingredients': food.ingredients,
                    'serving_size': food.serving_size,
                    'serving_unit': food.serving_unit
                }
                data['foods'].append(food_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"資料已儲存為 JSON: {filename}")
            
        except Exception as e:
            logger.error(f"儲存JSON失敗: {e}")
    
    def get_statistics(self, foods: List[USDAFoodItem]) -> Dict:
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
    
    def search_food_by_name(self, food_name: str) -> Optional[USDAFoodItem]:
        """
        根據名稱搜尋食物
        
        Args:
            food_name: 食物名稱
            
        Returns:
            食物項目或None
        """
        try:
            search_result = self.search_foods(food_name, page_size=10, page_number=1)
            
            if not search_result or 'foods' not in search_result:
                return None
            
            foods = search_result['foods']
            
            for food_data in foods:
                food_item = self.parse_food_item(food_data)
                if food_item and food_item.energy_kcal > 0:
                    return food_item
            
            return None
            
        except Exception as e:
            logger.error(f"搜尋食物 {food_name} 失敗: {e}")
            return None

def main():
    """主函數"""
    print("🍽️ USDA FoodData Central 食物資料抓取器")
    print("=" * 50)
    
    # 創建抓取器
    scraper = USDAScraper()
    
    try:
        # 抓取所有分類的食物
        print("開始抓取食物資料...")
        foods = scraper.scrape_all_categories(max_items_per_category=30)
        
        if not foods:
            print("❌ 未抓取到任何食物資料")
            return
        
        # 顯示統計資訊
        stats = scraper.get_statistics(foods)
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
        
        csv_filename = f"usda_foods_{timestamp}.csv"
        json_filename = f"usda_foods_{timestamp}.json"
        
        scraper.save_to_csv(foods, csv_filename)
        scraper.save_to_json(foods, json_filename)
        
        print(f"\n✅ 抓取完成！")
        print(f"  CSV檔案: {csv_filename}")
        print(f"  JSON檔案: {json_filename}")
        
        # 顯示前10個食物項目
        print(f"\n🍎 前10個食物項目:")
        for i, food in enumerate(foods[:10], 1):
            print(f"  {i}. {food.food_name} - {food.energy_kcal:.1f} kcal ({food.category})")
        
    except KeyboardInterrupt:
        print("\n⏹️ 抓取被使用者中斷")
    except Exception as e:
        print(f"\n❌ 抓取失敗: {e}")

if __name__ == "__main__":
    main() 