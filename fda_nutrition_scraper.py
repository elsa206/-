#!/usr/bin/env python3
"""
台灣食品藥物管理署 - 食品營養成分資料庫抓取器
抓取 https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178 的營養資料
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional
import re

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FDANutritionScraper:
    """FDA 營養資料庫抓取器"""
    
    def __init__(self):
        """初始化抓取器"""
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
        
        # 食品分類對應
        self.food_categories = {
            '穀物類': 'A',
            '澱粉類': 'B', 
            '堅果及種子類': 'C',
            '水果類': 'D',
            '蔬菜類': 'E',
            '藻類': 'F',
            '菇類': 'G',
            '豆類': 'H',
            '肉類': 'I',
            '魚貝類': 'J',
            '蛋類': 'K',
            '乳品類': 'L',
            '油脂類': 'M',
            '糖類': 'N',
            '嗜好性飲料類': 'O',
            '調味料及香辛料類': 'P',
            '糕餅點心類': 'Q',
            '加工調理食品類': 'R'
        }
    
    def get_main_page(self) -> Optional[BeautifulSoup]:
        """獲取主頁面"""
        try:
            params = {'nodeID': '178'}
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # 設定編碼
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"獲取主頁面失敗: {e}")
            return None
    
    def extract_viewstate(self, soup: BeautifulSoup) -> Dict[str, str]:
        """提取 ASP.NET 的 ViewState 參數"""
        viewstate_data = {}
        
        # 提取 __VIEWSTATE
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate:
            viewstate_data['__VIEWSTATE'] = viewstate.get('value', '')
        
        # 提取 __VIEWSTATEGENERATOR
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        if viewstategenerator:
            viewstate_data['__VIEWSTATEGENERATOR'] = viewstategenerator.get('value', '')
        
        # 提取 __EVENTVALIDATION
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        if eventvalidation:
            viewstate_data['__EVENTVALIDATION'] = eventvalidation.get('value', '')
        
        return viewstate_data
    
    def search_foods(self, category: str = '', keyword: str = '', page: int = 1) -> List[Dict]:
        """搜尋食品資料"""
        try:
            # 獲取主頁面
            soup = self.get_main_page()
            if not soup:
                return []
            
            # 提取 ViewState 參數
            viewstate_data = self.extract_viewstate(soup)
            
            # 準備搜尋參數
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
            
            # 如果是分頁，設定分頁參數
            if page > 1:
                search_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$GridView1'
                search_data['__EVENTARGUMENT'] = f'Page${page}'
            
            # 發送搜尋請求
            response = self.session.post(self.base_url, data=search_data, params={'nodeID': '178'})
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # 解析結果
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.parse_search_results(soup)
            
        except Exception as e:
            logger.error(f"搜尋食品資料失敗: {e}")
            return []
    
    def parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """解析搜尋結果"""
        results = []
        
        try:
            # 找到結果表格
            table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_GridView1'})
            if not table:
                return results
            
            # 解析表格行
            rows = table.find_all('tr')[1:]  # 跳過標題行
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    # 提取連結
                    link_cell = cells[1].find('a')
                    detail_url = None
                    if link_cell:
                        detail_url = 'https://consumer.fda.gov.tw/Food/' + link_cell.get('href', '')
                    
                    food_data = {
                        '整合編號': cells[0].get_text(strip=True),
                        '樣品名稱': cells[1].get_text(strip=True),
                        '俗名': cells[2].get_text(strip=True),
                        '樣品英文名稱': cells[3].get_text(strip=True),
                        '內容物描述': cells[4].get_text(strip=True),
                        '詳細頁面URL': detail_url
                    }
                    
                    results.append(food_data)
            
        except Exception as e:
            logger.error(f"解析搜尋結果失敗: {e}")
        
        return results
    
    def get_food_detail(self, detail_url: str) -> Optional[Dict]:
        """獲取食品詳細營養資訊"""
        try:
            response = self.session.get(detail_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.parse_food_detail(soup)
            
        except Exception as e:
            logger.error(f"獲取食品詳細資訊失敗: {e}")
            return None
    
    def parse_food_detail(self, soup: BeautifulSoup) -> Optional[Dict]:
        """解析食品詳細資訊"""
        try:
            detail_data = {}
            
            # 找到詳細資訊表格
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        if key and value:
                            detail_data[key] = value
            
            # 提取營養成分
            nutrition_data = self.extract_nutrition_data(soup)
            detail_data['營養成分'] = nutrition_data
            
            return detail_data
            
        except Exception as e:
            logger.error(f"解析食品詳細資訊失敗: {e}")
            return None
    
    def extract_nutrition_data(self, soup: BeautifulSoup) -> Dict:
        """提取營養成分資料"""
        nutrition = {}
        
        try:
            # 尋找營養成分表格
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        nutrient_name = cells[0].get_text(strip=True)
                        nutrient_value = cells[1].get_text(strip=True)
                        
                        # 清理資料
                        if nutrient_name and nutrient_value:
                            # 移除單位和特殊字符
                            clean_value = re.sub(r'[^\d.]', '', nutrient_value)
                            if clean_value:
                                try:
                                    nutrition[nutrient_name] = float(clean_value)
                                except ValueError:
                                    nutrition[nutrient_name] = nutrient_value
            
        except Exception as e:
            logger.error(f"提取營養成分失敗: {e}")
        
        return nutrition
    
    def scrape_all_foods(self, max_pages: int = 50) -> List[Dict]:
        """抓取所有食品資料"""
        all_foods = []
        
        try:
            logger.info("開始抓取所有食品資料...")
            
            # 逐頁抓取
            for page in range(1, max_pages + 1):
                logger.info(f"正在抓取第 {page} 頁...")
                
                foods = self.search_foods(page=page)
                if not foods:
                    logger.info(f"第 {page} 頁沒有資料，停止抓取")
                    break
                
                all_foods.extend(foods)
                
                # 避免請求過於頻繁
                time.sleep(1)
            
            logger.info(f"總共抓取到 {len(all_foods)} 筆食品資料")
            return all_foods
            
        except Exception as e:
            logger.error(f"抓取所有食品資料失敗: {e}")
            return all_foods
    
    def scrape_food_details(self, foods: List[Dict], max_details: int = 100) -> List[Dict]:
        """抓取食品詳細資訊"""
        detailed_foods = []
        
        try:
            logger.info(f"開始抓取 {min(len(foods), max_details)} 筆食品詳細資訊...")
            
            for i, food in enumerate(foods[:max_details]):
                if food.get('詳細頁面URL'):
                    logger.info(f"正在抓取 {food['樣品名稱']} 的詳細資訊...")
                    
                    detail = self.get_food_detail(food['詳細頁面URL'])
                    if detail:
                        food['詳細資訊'] = detail
                        detailed_foods.append(food)
                    
                    # 避免請求過於頻繁
                    time.sleep(2)
            
            logger.info(f"成功抓取 {len(detailed_foods)} 筆詳細資訊")
            return detailed_foods
            
        except Exception as e:
            logger.error(f"抓取食品詳細資訊失敗: {e}")
            return detailed_foods
    
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
            
            # 取得所有欄位
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"資料已儲存至 {filename}")
            
        except Exception as e:
            logger.error(f"儲存 CSV 檔案失敗: {e}")
    
    def convert_to_nutrition_db(self, foods: List[Dict]) -> Dict:
        """轉換為營養資料庫格式"""
        nutrition_db = {}
        
        try:
            for food in foods:
                food_name = food.get('樣品名稱', '').lower()
                if not food_name:
                    continue
                
                # 提取營養資訊
                nutrition = food.get('詳細資訊', {}).get('營養成分', {})
                
                if nutrition:
                    # 轉換為標準格式
                    nutrition_db[food_name] = {
                        'calories': nutrition.get('熱量', 0),
                        'protein': nutrition.get('粗蛋白', 0),
                        'carbs': nutrition.get('碳水化合物', 0),
                        'fat': nutrition.get('粗脂肪', 0),
                        'fiber': nutrition.get('膳食纖維', 0),
                        'vitamins': self.extract_vitamins(nutrition),
                        'minerals': self.extract_minerals(nutrition),
                        'source': 'FDA_TW',
                        'original_name': food.get('樣品名稱', ''),
                        'category': food.get('分類', '')
                    }
            
            logger.info(f"成功轉換 {len(nutrition_db)} 筆營養資料")
            return nutrition_db
            
        except Exception as e:
            logger.error(f"轉換營養資料庫失敗: {e}")
            return nutrition_db
    
    def extract_vitamins(self, nutrition: Dict) -> List[str]:
        """提取維生素資訊"""
        vitamins = []
        vitamin_keywords = ['維生素A', '維生素B', '維生素C', '維生素D', '維生素E', '維生素K']
        
        for key in nutrition.keys():
            for vitamin in vitamin_keywords:
                if vitamin in key:
                    vitamins.append(vitamin)
                    break
        
        return list(set(vitamins))
    
    def extract_minerals(self, nutrition: Dict) -> List[str]:
        """提取礦物質資訊"""
        minerals = []
        mineral_keywords = ['鈣', '鐵', '鎂', '鋅', '鉀', '鈉', '磷']
        
        for key in nutrition.keys():
            for mineral in mineral_keywords:
                if mineral in key:
                    minerals.append(mineral)
                    break
        
        return list(set(minerals))

def main():
    """主函數"""
    print("🍽️ 台灣FDA食品營養成分資料庫抓取器")
    print("=" * 50)
    
    scraper = FDANutritionScraper()
    
    # 抓取基本資料
    print("📋 抓取食品基本資料...")
    foods = scraper.scrape_all_foods(max_pages=10)  # 限制頁數避免過度請求
    
    if foods:
        # 儲存基本資料
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scraper.save_to_json(foods, f"fda_foods_basic_{timestamp}.json")
        scraper.save_to_csv(foods, f"fda_foods_basic_{timestamp}.csv")
        
        # 抓取詳細資訊
        print("🔍 抓取食品詳細營養資訊...")
        detailed_foods = scraper.scrape_food_details(foods, max_details=50)  # 限制數量
        
        if detailed_foods:
            # 儲存詳細資料
            scraper.save_to_json(detailed_foods, f"fda_foods_detailed_{timestamp}.json")
            scraper.save_to_csv(detailed_foods, f"fda_foods_detailed_{timestamp}.csv")
            
            # 轉換為營養資料庫格式
            print("🔄 轉換為營養資料庫格式...")
            nutrition_db = scraper.convert_to_nutrition_db(detailed_foods)
            
            if nutrition_db:
                scraper.save_to_json(nutrition_db, f"fda_nutrition_db_{timestamp}.json")
                print(f"✅ 成功建立營養資料庫，包含 {len(nutrition_db)} 種食品")
        
        print("🎉 資料抓取完成！")
    else:
        print("❌ 未抓取到任何資料")

if __name__ == "__main__":
    main() 