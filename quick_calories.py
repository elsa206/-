#!/usr/bin/env python3
"""
快速食物熱量提取腳本
簡單易用的食物熱量查詢工具
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime
import re

def get_food_calories_simple():
    """簡單版本的食物熱量提取"""
    
    print("🍽️ 快速食物熱量提取器")
    print("=" * 40)
    print("📋 只提取食物名稱和熱量")
    print("=" * 40)
    
    # 基本設定
    base_url = "https://consumer.fda.gov.tw/Food/TFND.aspx"
    session = requests.Session()
    
    # 設定請求標頭
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    })
    
    all_foods = []
    
    try:
        print("📋 正在抓取食物資料...")
        
        # 獲取主頁面
        params = {'nodeID': '178'}
        response = session.get(base_url, params=params)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取 ViewState 參數
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        
        viewstate_value = viewstate.get('value', '') if viewstate else ''
        viewstategenerator_value = viewstategenerator.get('value', '') if viewstategenerator else ''
        eventvalidation_value = eventvalidation.get('value', '') if eventvalidation else ''
        
        # 搜尋所有食物（前5頁）
        for page in range(1, 6):
            print(f"  正在處理第 {page} 頁...")
            
            search_data = {
                '__VIEWSTATE': viewstate_value,
                '__VIEWSTATEGENERATOR': viewstategenerator_value,
                '__EVENTVALIDATION': eventvalidation_value,
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                'ctl00$ContentPlaceHolder1$DropDownList1': '',
                'ctl00$ContentPlaceHolder1$TextBox1': '',
                'ctl00$ContentPlaceHolder1$Button1': '查詢'
            }
            
            if page > 1:
                search_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$GridView1'
                search_data['__EVENTARGUMENT'] = f'Page${page}'
            
            response = session.post(base_url, data=search_data, params={'nodeID': '178'})
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析表格
            table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})
            if not table:
                break
            
            rows = table.find_all('tr')[1:]  # 跳過標題行
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    food_name = cells[1].get_text(strip=True)
                    link_cell = cells[1].find('a')
                    
                    if link_cell and food_name:
                        detail_url = 'https://consumer.fda.gov.tw/Food/' + link_cell.get('href', '')
                        all_foods.append({
                            'food_name': food_name,
                            'detail_url': detail_url
                        })
            
            time.sleep(1)  # 避免請求過於頻繁
        
        print(f"✅ 找到 {len(all_foods)} 種食物")
        
        # 提取熱量資訊（前20種）
        foods_with_calories = []
        print(f"🔥 正在提取前 20 種食物的熱量...")
        
        for i, food in enumerate(all_foods[:20]):
            food_name = food['food_name']
            detail_url = food['detail_url']
            
            print(f"  正在處理: {food_name}")
            
            try:
                response = session.get(detail_url)
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尋找熱量
                calories = None
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            
                            if '熱量' in key and value:
                                calories_match = re.search(r'(\d+(?:\.\d+)?)', value)
                                if calories_match:
                                    calories = float(calories_match.group(1))
                                    break
                    
                    if calories is not None:
                        break
                
                if calories is not None:
                    food['calories'] = calories
                    foods_with_calories.append(food)
                    print(f"    ✅ {food_name}: {calories} 卡路里")
                else:
                    print(f"    ❌ {food_name}: 未找到熱量資訊")
                
            except Exception as e:
                print(f"    ❌ {food_name}: 處理失敗 - {e}")
            
            time.sleep(2)  # 避免請求過於頻繁
        
        # 儲存結果
        if foods_with_calories:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 儲存為 JSON
            json_filename = f"food_calories_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(foods_with_calories, f, ensure_ascii=False, indent=2)
            
            # 儲存為 CSV
            csv_filename = f"food_calories_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['food_name', 'calories'])
                writer.writeheader()
                writer.writerows(foods_with_calories)
            
            # 創建簡化的熱量資料庫
            calories_db = {}
            for food in foods_with_calories:
                food_name = food['food_name'].lower()
                calories = food['calories']
                calories_db[food_name] = {
                    'calories': calories,
                    'original_name': food['food_name']
                }
            
            db_filename = f"calories_db_{timestamp}.json"
            with open(db_filename, 'w', encoding='utf-8') as f:
                json.dump(calories_db, f, ensure_ascii=False, indent=2)
            
            # 顯示結果
            print(f"\n🎉 成功提取 {len(foods_with_calories)} 種食物的熱量！")
            print("\n📊 食物熱量列表:")
            for i, food in enumerate(foods_with_calories, 1):
                print(f"  {i:2d}. {food['food_name']}: {food['calories']} 卡路里")
            
            print(f"\n💾 檔案已儲存:")
            print(f"   - {json_filename} (完整資料)")
            print(f"   - {csv_filename} (CSV 格式)")
            print(f"   - {db_filename} (熱量資料庫)")
            
            return foods_with_calories
        else:
            print("❌ 未成功提取任何熱量資訊")
            return []
            
    except Exception as e:
        print(f"❌ 抓取過程中發生錯誤: {e}")
        return []

def search_specific_food(food_name):
    """搜尋特定食物的熱量"""
    print(f"🔍 搜尋食物: {food_name}")
    
    # 這裡可以實作特定食物搜尋邏輯
    # 暫時返回模擬資料
    mock_calories = {
        'apple': 95,
        'banana': 105,
        'rice': 130,
        'chicken': 165,
        'beef': 250,
        'fish': 100,
        'bread': 79,
        'milk': 42,
        'egg': 78,
        'pork': 242
    }
    
    food_lower = food_name.lower()
    if food_lower in mock_calories:
        print(f"✅ {food_name}: {mock_calories[food_lower]} 卡路里")
        return mock_calories[food_lower]
    else:
        print(f"❌ 未找到 {food_name} 的熱量資訊")
        return None

def main():
    """主函數"""
    print("🍽️ 食物熱量查詢工具")
    print("=" * 40)
    
    while True:
        print("\n請選擇操作:")
        print("1. 抓取 FDA 食物熱量資料庫")
        print("2. 搜尋特定食物熱量")
        print("3. 退出")
        
        choice = input("\n請輸入選項 (1-3): ").strip()
        
        if choice == '1':
            print("\n" + "=" * 40)
            get_food_calories_simple()
            print("=" * 40)
            
        elif choice == '2':
            food_name = input("請輸入食物名稱: ").strip()
            if food_name:
                print("\n" + "=" * 40)
                search_specific_food(food_name)
                print("=" * 40)
            else:
                print("❌ 請輸入有效的食物名稱")
                
        elif choice == '3':
            print("👋 感謝使用！")
            break
            
        else:
            print("❌ 無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 