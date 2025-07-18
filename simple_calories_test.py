#!/usr/bin/env python3
"""
最簡單的食物熱量測試腳本
只提取食物名稱和熱量，無複雜功能
"""

import requests
import json
import csv
from datetime import datetime

def create_sample_calories_data():
    """創建範例熱量資料"""
    
    print("🍽️ 食物熱量資料生成器")
    print("=" * 40)
    print("📋 生成食物名稱和熱量資料")
    print("=" * 40)
    
    # 範例食物熱量資料
    sample_foods = [
        {"food_name": "大麥仁", "calories": 354},
        {"food_name": "大麥片", "calories": 340},
        {"food_name": "小米", "calories": 378},
        {"food_name": "小麥", "calories": 327},
        {"food_name": "小麥胚芽", "calories": 360},
        {"food_name": "低筋麵粉", "calories": 364},
        {"food_name": "中筋麵粉", "calories": 364},
        {"food_name": "高筋麵粉", "calories": 364},
        {"food_name": "白米", "calories": 130},
        {"food_name": "糙米", "calories": 111},
        {"food_name": "糯米", "calories": 130},
        {"food_name": "燕麥", "calories": 389},
        {"food_name": "玉米", "calories": 86},
        {"food_name": "馬鈴薯", "calories": 77},
        {"food_name": "地瓜", "calories": 86},
        {"food_name": "蘋果", "calories": 52},
        {"food_name": "香蕉", "calories": 89},
        {"food_name": "橘子", "calories": 47},
        {"food_name": "葡萄", "calories": 62},
        {"food_name": "草莓", "calories": 32},
        {"food_name": "西瓜", "calories": 30},
        {"food_name": "芒果", "calories": 60},
        {"food_name": "奇異果", "calories": 61},
        {"food_name": "鳳梨", "calories": 50},
        {"food_name": "高麗菜", "calories": 25},
        {"food_name": "空心菜", "calories": 20},
        {"food_name": "青江菜", "calories": 13},
        {"food_name": "菠菜", "calories": 23},
        {"food_name": "小白菜", "calories": 13},
        {"food_name": "胡蘿蔔", "calories": 41},
        {"food_name": "洋蔥", "calories": 40},
        {"food_name": "番茄", "calories": 18},
        {"food_name": "青椒", "calories": 20},
        {"food_name": "茄子", "calories": 24},
        {"food_name": "小黃瓜", "calories": 16},
        {"food_name": "冬瓜", "calories": 13},
        {"food_name": "苦瓜", "calories": 17},
        {"food_name": "絲瓜", "calories": 20},
        {"food_name": "南瓜", "calories": 26},
        {"food_name": "豬肉", "calories": 242},
        {"food_name": "牛肉", "calories": 250},
        {"food_name": "雞肉", "calories": 165},
        {"food_name": "鴨肉", "calories": 337},
        {"food_name": "羊肉", "calories": 294},
        {"food_name": "魚肉", "calories": 100},
        {"food_name": "蝦仁", "calories": 85},
        {"food_name": "蟹肉", "calories": 97},
        {"food_name": "蛤蜊", "calories": 86},
        {"food_name": "牡蠣", "calories": 69},
        {"food_name": "雞蛋", "calories": 78},
        {"food_name": "鴨蛋", "calories": 185},
        {"food_name": "鵝蛋", "calories": 185},
        {"food_name": "牛奶", "calories": 42},
        {"food_name": "優格", "calories": 59},
        {"food_name": "起司", "calories": 113},
        {"food_name": "奶油", "calories": 717},
        {"food_name": "豆漿", "calories": 31},
        {"food_name": "豆腐", "calories": 76},
        {"food_name": "豆干", "calories": 192},
        {"food_name": "豆花", "calories": 35},
        {"food_name": "花生", "calories": 567},
        {"food_name": "瓜子", "calories": 573},
        {"food_name": "核桃", "calories": 654},
        {"food_name": "杏仁", "calories": 579},
        {"food_name": "腰果", "calories": 553},
        {"food_name": "開心果", "calories": 560},
        {"food_name": "松子", "calories": 619},
        {"food_name": "芝麻", "calories": 573},
        {"food_name": "蓮子", "calories": 89},
        {"food_name": "紅豆", "calories": 329},
        {"food_name": "綠豆", "calories": 329},
        {"food_name": "黃豆", "calories": 446},
        {"food_name": "黑豆", "calories": 341},
        {"food_name": "花豆", "calories": 337},
        {"food_name": "菜豆", "calories": 31},
        {"food_name": "四季豆", "calories": 31},
        {"food_name": "豌豆", "calories": 84},
        {"food_name": "毛豆", "calories": 147},
        {"food_name": "玉米筍", "calories": 26},
        {"food_name": "竹筍", "calories": 23},
        {"food_name": "茭白筍", "calories": 25},
        {"food_name": "蘆筍", "calories": 20},
        {"food_name": "芹菜", "calories": 16},
        {"food_name": "韭菜", "calories": 32},
        {"food_name": "韭黃", "calories": 24},
        {"food_name": "蒜苗", "calories": 24},
        {"food_name": "蔥", "calories": 32},
        {"food_name": "薑", "calories": 80},
        {"food_name": "蒜頭", "calories": 149},
        {"food_name": "辣椒", "calories": 40},
        {"food_name": "九層塔", "calories": 22},
        {"food_name": "香菜", "calories": 23},
        {"food_name": "薄荷", "calories": 44},
        {"food_name": "迷迭香", "calories": 131},
        {"food_name": "百里香", "calories": 101},
        {"food_name": "羅勒", "calories": 22},
        {"food_name": "紫蘇", "calories": 37},
        {"food_name": "香茅", "calories": 99},
        {"food_name": "檸檬", "calories": 29},
        {"food_name": "萊姆", "calories": 30},
        {"food_name": "柳橙", "calories": 47},
        {"food_name": "葡萄柚", "calories": 42},
        {"food_name": "金桔", "calories": 71},
        {"food_name": "柚子", "calories": 38},
        {"food_name": "文旦", "calories": 38},
        {"food_name": "橘子", "calories": 47},
        {"food_name": "茂谷柑", "calories": 47},
        {"food_name": "椪柑", "calories": 47},
        {"food_name": "桶柑", "calories": 47},
        {"food_name": "海梨", "calories": 47},
        {"food_name": "柳丁", "calories": 47},
        {"food_name": "檸檬", "calories": 29},
        {"food_name": "萊姆", "calories": 30},
        {"food_name": "金桔", "calories": 71},
        {"food_name": "柚子", "calories": 38},
        {"food_name": "文旦", "calories": 38},
        {"food_name": "橘子", "calories": 47},
        {"food_name": "茂谷柑", "calories": 47},
        {"food_name": "椪柑", "calories": 47},
        {"food_name": "桶柑", "calories": 47},
        {"food_name": "海梨", "calories": 47},
        {"food_name": "柳丁", "calories": 47}
    ]
    
    # 儲存資料
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 儲存為 JSON
    json_filename = f"simple_food_calories_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(sample_foods, f, ensure_ascii=False, indent=2)
    
    # 儲存為 CSV
    csv_filename = f"simple_food_calories_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['food_name', 'calories'])
        writer.writeheader()
        writer.writerows(sample_foods)
    
    # 創建簡化的熱量資料庫
    calories_db = {}
    for food in sample_foods:
        food_name = food['food_name'].lower()
        calories = food['calories']
        calories_db[food_name] = {
            'calories': calories,
            'original_name': food['food_name']
        }
    
    db_filename = f"simple_calories_db_{timestamp}.json"
    with open(db_filename, 'w', encoding='utf-8') as f:
        json.dump(calories_db, f, ensure_ascii=False, indent=2)
    
    # 顯示結果
    print(f"✅ 成功生成 {len(sample_foods)} 種食物的熱量資料！")
    print("\n📊 前 20 種食物熱量:")
    for i, food in enumerate(sample_foods[:20], 1):
        print(f"  {i:2d}. {food['food_name']}: {food['calories']} 卡路里")
    
    print(f"\n💾 檔案已儲存:")
    print(f"   - {json_filename} (完整資料)")
    print(f"   - {csv_filename} (CSV 格式)")
    print(f"   - {db_filename} (熱量資料庫)")
    
    return sample_foods

def search_food_calories(food_name, calories_db):
    """搜尋食物熱量"""
    food_lower = food_name.lower()
    if food_lower in calories_db:
        calories = calories_db[food_lower]['calories']
        original_name = calories_db[food_lower]['original_name']
        print(f"✅ {original_name}: {calories} 卡路里")
        return calories
    else:
        print(f"❌ 未找到 {food_name} 的熱量資訊")
        return None

def main():
    """主函數"""
    print("🍽️ 簡化版食物熱量查詢工具")
    print("=" * 40)
    
    # 生成範例資料
    foods = create_sample_calories_data()
    
    # 創建搜尋資料庫
    calories_db = {}
    for food in foods:
        food_name = food['food_name'].lower()
        calories_db[food_name] = {
            'calories': food['calories'],
            'original_name': food['food_name']
        }
    
    # 互動式搜尋
    print("\n🔍 開始搜尋食物熱量...")
    while True:
        print("\n請選擇操作:")
        print("1. 搜尋食物熱量")
        print("2. 顯示所有食物")
        print("3. 退出")
        
        choice = input("\n請輸入選項 (1-3): ").strip()
        
        if choice == '1':
            food_name = input("請輸入食物名稱: ").strip()
            if food_name:
                search_food_calories(food_name, calories_db)
            else:
                print("❌ 請輸入有效的食物名稱")
                
        elif choice == '2':
            print(f"\n📋 所有食物列表 (共 {len(foods)} 種):")
            for i, food in enumerate(foods, 1):
                print(f"  {i:3d}. {food['food_name']}: {food['calories']} 卡路里")
                
        elif choice == '3':
            print("👋 感謝使用！")
            break
            
        else:
            print("❌ 無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 