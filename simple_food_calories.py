#!/usr/bin/env python3
"""
簡化版食物熱量提取器
只提取食物名稱和熱量資訊
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import os
from datetime import datetime
import logging
import re
from typing import List, Dict, Optional

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFoodCaloriesExtractor:
    """簡化版食物熱量提取器"""
    
    def __init__(self):
        """初始化提取器"""
        self.base_url = "https://consumer.fda.gov.tw/Food/TFND.aspx"
        self.session = requests.Session()
        
        # 設定請求標頭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_main_page(self) -> Optional[BeautifulSoup]:
        """獲取主頁面"""
        try:
            params = {'nodeID': '178'}
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"獲取主頁面失敗: {e}")
            return None
    
    def extract_viewstate(self, soup: BeautifulSoup) -> Dict[str, str]:
        """提取 ASP.NET 的 ViewState 參數"""
        viewstate_data = {}
        
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate:
            viewstate_data['__VIEWSTATE'] = viewstate.get('value', '')
        
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        if viewstategenerator:
            viewstate_data['__VIEWSTATEGENERATOR'] = viewstategenerator.get('value', '')
        
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        if eventvalidation:
            viewstate_data['__EVENTVALIDATION'] = eventvalidation.get('value', '')
        
        return viewstate_data
    
    def search_foods(self, category: str = '', keyword: str = '', page: int = 1) -> List[Dict]:
        """搜尋食品資料"""
        try:
            soup = self.get_main_page()
            if not soup:
                return []
            
            viewstate_data = self.extract_viewstate(soup)
            
            search_data = {
                '__VIEWSTATE': viewstate_data.get('__VIEWSTATE', ''),
                '__VIEWSTATEGENERATOR': viewstate_data.get('__VIEWSTATEGENERATOR', ''),
                '__EVENTVALIDATION': viewstate_data.get('__EVENTVALIDATION', ''),
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                'ctl00$ContentPlaceHolder1$DropDownList1': category,
                'ctl00$ContentPlaceHolder1$TextBox1': keyword,
                'ctl00$ContentPlaceHolder1$Button1': '查詢'
            }
            
            if page > 1:
                search_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$GridView1'
                search_data['__EVENTARGUMENT'] = f'Page${page}'
            
            response = self.session.post(self.base_url, data=search_data, params={'nodeID': '178'})
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.parse_search_results(soup)
            
        except Exception as e:
            logger.error(f"搜尋食品資料失敗: {e}")
            return []
    
    def parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """解析搜尋結果"""
        results = []
        
        try:
            table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})
            if not table:
                return results
            
            rows = table.find_all('tr')[1:]  # 跳過標題行
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    link_cell = cells[1].find('a')
                    detail_url = None
                    if link_cell:
                        detail_url = 'https://consumer.fda.gov.tw/Food/' + link_cell.get('href', '')
                    
                    food_data = {
                        'food_name': cells[1].get_text(strip=True),
                        'detail_url': detail_url
                    }
                    
                    results.append(food_data)
            
        except Exception as e:
            logger.error(f"解析搜尋結果失敗: {e}")
        
        return results
    
    def get_food_calories(self, detail_url: str) -> Optional[Dict]:
        """獲取食品熱量資訊"""
        try:
            response = self.session.get(detail_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.extract_calories(soup)
            
        except Exception as e:
            logger.error(f"獲取食品熱量失敗: {e}")
            return None
    
    def extract_calories(self, soup: BeautifulSoup) -> Optional[Dict]:
        """提取熱量資訊"""
        try:
            calories = None
            
            # 尋找所有表格
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # 尋找熱量相關欄位
                        if '熱量' in key and value:
                            # 提取數字
                            calories_match = re.search(r'(\d+(?:\.\d+)?)', value)
                            if calories_match:
                                calories = float(calories_match.group(1))
                                break
                
                if calories is not None:
                    break
            
            return {'calories': calories} if calories is not None else None
            
        except Exception as e:
            logger.error(f"提取熱量失敗: {e}")
            return None
    
    def scrape_food_calories(self, max_pages: int = 10, max_details: int = 50) -> List[Dict]:
        """抓取食物熱量資料"""
        all_foods = []
        
        try:
            logger.info("開始抓取食物基本資料...")
            
            # 逐頁抓取
            for page in range(1, max_pages + 1):
                logger.info(f"正在抓取第 {page} 頁...")
                
                foods = self.search_foods(page=page)
                if not foods:
                    logger.info(f"第 {page} 頁沒有資料，停止抓取")
                    break
                
                all_foods.extend(foods)
                time.sleep(1)  # 避免請求過於頻繁
            
            logger.info(f"總共抓取到 {len(all_foods)} 種食物")
            
            # 抓取熱量資訊
            logger.info(f"開始抓取 {min(len(all_foods), max_details)} 種食物的熱量資訊...")
            
            foods_with_calories = []
            for i, food in enumerate(all_foods[:max_details]):
                if food.get('detail_url'):
                    logger.info(f"正在抓取 {food['food_name']} 的熱量...")
                    
                    calories_info = self.get_food_calories(food['detail_url'])
                    if calories_info and calories_info['calories'] is not None:
                        food['calories'] = calories_info['calories']
                        foods_with_calories.append(food)
                    
                    time.sleep(2)  # 避免請求過於頻繁
            
            logger.info(f"成功抓取 {len(foods_with_calories)} 種食物的熱量資訊")
            return foods_with_calories
            
        except Exception as e:
            logger.error(f"抓取食物熱量資料失敗: {e}")
            return all_foods
    
    def save_to_json(self, data: List[Dict], filename: str):
        """儲存資料為 JSON 格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"資料已儲存至 {filename}")
            
        except Exception as e:
            logger.error(f"儲存 JSON 檔案失敗: {e}")
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """儲存資料為 CSV 格式"""
        try:
            if not data:
                return
            
            fieldnames = ['food_name', 'calories']
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"資料已儲存至 {filename}")
            
        except Exception as e:
            logger.error(f"儲存 CSV 檔案失敗: {e}")
    
    def create_calories_database(self, foods: List[Dict]) -> Dict:
        """創建熱量資料庫"""
        calories_db = {}
        
        try:
            for food in foods:
                food_name = food.get('food_name', '').lower()
                calories = food.get('calories')
                
                if food_name and calories is not None:
                    calories_db[food_name] = {
                        'calories': calories,
                        'original_name': food.get('food_name', ''),
                        'source': 'FDA_TW'
                    }
            
            logger.info(f"成功建立熱量資料庫，包含 {len(calories_db)} 種食物")
            return calories_db
            
        except Exception as e:
            logger.error(f"建立熱量資料庫失敗: {e}")
            return calories_db

def main():
    """主函數"""
    print("🍽️ 簡化版食物熱量提取器")
    print("=" * 40)
    print("📋 只提取食物名稱和熱量資訊")
    print("=" * 40)
    
    extractor = SimpleFoodCaloriesExtractor()
    
    # 抓取資料
    print("📋 抓取食物熱量資料...")
    foods = extractor.scrape_food_calories(max_pages=5, max_details=20)  # 限制數量避免過度請求
    
    if foods:
        # 儲存資料
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 儲存完整資料
        extractor.save_to_json(foods, f"food_calories_{timestamp}.json")
        extractor.save_to_csv(foods, f"food_calories_{timestamp}.csv")
        
        # 創建熱量資料庫
        calories_db = extractor.create_calories_database(foods)
        if calories_db:
            extractor.save_to_json(calories_db, f"calories_database_{timestamp}.json")
        
        # 顯示結果
        print(f"\n✅ 成功提取 {len(foods)} 種食物的熱量資訊")
        print("\n📊 前 10 種食物熱量:")
        for i, food in enumerate(foods[:10]):
            calories = food.get('calories', 'N/A')
            print(f"  {i+1:2d}. {food['food_name']}: {calories} 卡路里")
        
        print(f"\n💾 檔案已儲存:")
        print(f"   - food_calories_{timestamp}.json")
        print(f"   - food_calories_{timestamp}.csv")
        print(f"   - calories_database_{timestamp}.json")
        
    else:
        print("❌ 未抓取到任何資料")

if __name__ == "__main__":
    main() 