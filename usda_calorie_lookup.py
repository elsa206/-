#!/usr/bin/env python3
"""
USDA 熱量查詢工具
從樣本資料中快速查詢食物熱量資訊
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
import re

@dataclass
class FoodItem:
    """食物項目資料結構"""
    food_name: str
    energy_kcal: float
    category: str
    fdc_id: str

class USDACalorieLookup:
    """USDA熱量查詢工具"""
    
    def __init__(self, data_file: str = "sample_usda_foods.json"):
        """初始化查詢工具"""
        self.data_file = data_file
        self.foods_data = []
        self.load_data()
    
    def load_data(self):
        """載入食物資料"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.foods_data = data.get('foods', [])
                print(f"✅ 已載入 {len(self.foods_data)} 個食物項目")
            else:
                print(f"❌ 找不到資料檔案: {self.data_file}")
                self.create_sample_data()
        except Exception as e:
            print(f"❌ 載入資料失敗: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """創建樣本資料"""
        print("📝 創建樣本資料...")
        
        sample_foods = [
            {"food_name": "Apple, raw, with skin", "energy_kcal": 52.0, "category": "fruits", "fdc_id": "171688"},
            {"food_name": "Banana, raw", "energy_kcal": 89.0, "category": "fruits", "fdc_id": "173944"},
            {"food_name": "Chicken, breast, raw", "energy_kcal": 165.0, "category": "proteins", "fdc_id": "171477"},
            {"food_name": "Rice, white, raw", "energy_kcal": 365.0, "category": "grains", "fdc_id": "169702"},
            {"food_name": "Milk, whole", "energy_kcal": 61.0, "category": "dairy", "fdc_id": "171265"},
            {"food_name": "Bread, white", "energy_kcal": 266.0, "category": "grains", "fdc_id": "172684"},
            {"food_name": "Carrot, raw", "energy_kcal": 41.0, "category": "vegetables", "fdc_id": "170393"},
            {"food_name": "Broccoli, raw", "energy_kcal": 34.0, "category": "vegetables", "fdc_id": "170379"},
            {"food_name": "Salmon, raw", "energy_kcal": 208.0, "category": "proteins", "fdc_id": "173686"},
            {"food_name": "Cheese, cheddar", "energy_kcal": 403.0, "category": "dairy", "fdc_id": "173410"}
        ]
        
        self.foods_data = sample_foods
        print(f"✅ 已創建 {len(self.foods_data)} 個樣本食物項目")
    
    def search_food(self, query: str, max_results: int = 5) -> List[FoodItem]:
        """
        搜尋食物
        
        Args:
            query: 搜尋關鍵字
            max_results: 最大結果數量
            
        Returns:
            食物項目列表
        """
        query_lower = query.lower()
        results = []
        
        for food_data in self.foods_data:
            food_name_lower = food_data['food_name'].lower()
            
            # 檢查是否包含搜尋關鍵字
            if query_lower in food_name_lower:
                food_item = FoodItem(
                    food_name=food_data['food_name'],
                    energy_kcal=food_data['energy_kcal'],
                    category=food_data['category'],
                    fdc_id=food_data['fdc_id']
                )
                results.append(food_item)
                
                if len(results) >= max_results:
                    break
        
        return results
    
    def search_by_category(self, category: str) -> List[FoodItem]:
        """
        按分類搜尋食物
        
        Args:
            category: 食物分類
            
        Returns:
            食物項目列表
        """
        category_lower = category.lower()
        results = []
        
        for food_data in self.foods_data:
            if food_data['category'].lower() == category_lower:
                food_item = FoodItem(
                    food_name=food_data['food_name'],
                    energy_kcal=food_data['energy_kcal'],
                    category=food_data['category'],
                    fdc_id=food_data['fdc_id']
                )
                results.append(food_item)
        
        return results
    
    def get_categories(self) -> List[str]:
        """獲取所有分類"""
        categories = set()
        for food_data in self.foods_data:
            categories.add(food_data['category'])
        return sorted(list(categories))
    
    def get_food_by_name(self, food_name: str) -> Optional[FoodItem]:
        """
        根據名稱獲取食物
        
        Args:
            food_name: 食物名稱
            
        Returns:
            食物項目或None
        """
        food_name_lower = food_name.lower()
        
        for food_data in self.foods_data:
            if food_data['food_name'].lower() == food_name_lower:
                return FoodItem(
                    food_name=food_data['food_name'],
                    energy_kcal=food_data['energy_kcal'],
                    category=food_data['category'],
                    fdc_id=food_data['fdc_id']
                )
        
        return None
    
    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        if not self.foods_data:
            return {}
        
        # 分類統計
        category_counts = {}
        for food_data in self.foods_data:
            category = food_data['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 熱量統計
        energies = [food_data['energy_kcal'] for food_data in self.foods_data if food_data['energy_kcal'] > 0]
        
        stats = {
            'total_foods': len(self.foods_data),
            'foods_with_energy': len(energies),
            'average_energy': sum(energies) / len(energies) if energies else 0,
            'min_energy': min(energies) if energies else 0,
            'max_energy': max(energies) if energies else 0,
            'category_distribution': category_counts
        }
        
        return stats
    
    def display_food(self, food: FoodItem):
        """顯示食物資訊"""
        print(f"🍽️  {food.food_name}")
        print(f"   🔥 熱量: {food.energy_kcal:.1f} kcal")
        print(f"   📂 分類: {food.category}")
        print(f"   🆔 FDC ID: {food.fdc_id}")
    
    def display_search_results(self, results: List[FoodItem], query: str):
        """顯示搜尋結果"""
        if not results:
            print(f"❌ 未找到包含 '{query}' 的食物")
            return
        
        print(f"\n🔍 搜尋結果: '{query}' (找到 {len(results)} 個)")
        print("-" * 50)
        
        for i, food in enumerate(results, 1):
            print(f"{i}. ", end="")
            self.display_food(food)
            print()
    
    def interactive_search(self):
        """互動式搜尋"""
        print("🔍 USDA 食物熱量查詢器")
        print("輸入 'quit' 退出，'help' 查看幫助")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n請輸入搜尋關鍵字: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("再見！")
                    break
                
                if query.lower() == 'help':
                    self.show_help()
                    continue
                
                if query.lower() == 'stats':
                    self.show_statistics()
                    continue
                
                if query.lower() == 'categories':
                    self.show_categories()
                    continue
                
                if query.lower().startswith('category:'):
                    category = query[9:].strip()
                    results = self.search_by_category(category)
                    self.display_search_results(results, f"分類: {category}")
                    continue
                
                if not query:
                    print("請輸入有效的搜尋關鍵字")
                    continue
                
                # 執行搜尋
                results = self.search_food(query, max_results=10)
                self.display_search_results(results, query)
                
            except KeyboardInterrupt:
                print("\n再見！")
                break
            except Exception as e:
                print(f"搜尋失敗: {e}")
    
    def show_help(self):
        """顯示幫助資訊"""
        print("\n📖 使用說明:")
        print("  - 直接輸入食物名稱進行搜尋")
        print("  - 輸入 'category:分類名' 搜尋特定分類")
        print("  - 輸入 'categories' 查看所有分類")
        print("  - 輸入 'stats' 查看統計資訊")
        print("  - 輸入 'help' 顯示此幫助")
        print("  - 輸入 'quit' 退出程式")
        print("\n📂 可用分類:")
        categories = self.get_categories()
        for category in categories:
            print(f"    - {category}")
    
    def show_statistics(self):
        """顯示統計資訊"""
        stats = self.get_statistics()
        
        print("\n📊 資料統計:")
        print(f"  總食物數量: {stats['total_foods']}")
        print(f"  有熱量資料的食物: {stats['foods_with_energy']}")
        print(f"  平均熱量: {stats['average_energy']:.1f} kcal")
        print(f"  熱量範圍: {stats['min_energy']:.1f} - {stats['max_energy']:.1f} kcal")
        
        print(f"\n📂 分類分布:")
        for category, count in stats['category_distribution'].items():
            print(f"  {category}: {count} 個")
    
    def show_categories(self):
        """顯示所有分類"""
        categories = self.get_categories()
        
        print("\n📂 所有分類:")
        for i, category in enumerate(categories, 1):
            count = len(self.search_by_category(category))
            print(f"  {i}. {category} ({count} 個食物)")
    
    def quick_lookup(self, food_name: str) -> Optional[float]:
        """
        快速查詢食物熱量
        
        Args:
            food_name: 食物名稱
            
        Returns:
            熱量值或None
        """
        food = self.get_food_by_name(food_name)
        if food:
            return food.energy_kcal
        return None

def main():
    """主函數"""
    print("🍽️ USDA 熱量查詢工具")
    print("=" * 40)
    
    # 創建查詢工具
    lookup = USDACalorieLookup()
    
    # 顯示統計資訊
    lookup.show_statistics()
    
    # 啟動互動式搜尋
    lookup.interactive_search()

if __name__ == "__main__":
    main() 