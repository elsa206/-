"""
Azure AI 食物影像辨識程式
使用 Azure Computer Vision API 進行食物識別和分析
"""

import os
import json
import requests
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io
import base64
from dotenv import load_dotenv
from datetime import datetime

# 載入環境變數
load_dotenv()

class FoodRecognition:
    """Azure AI 食物影像辨識類別"""
    
    def __init__(self):
        """初始化 Azure Computer Vision 客戶端"""
        self.endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        self.key = os.getenv('AZURE_VISION_KEY')
        
        if not self.endpoint or not self.key:
            raise ValueError("請設定 AZURE_VISION_ENDPOINT 和 AZURE_VISION_KEY 環境變數")
        
        # 移除結尾的斜線
        self.endpoint = self.endpoint.rstrip('/')
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析影像中的食物
        
        Args:
            image_path: 影像檔案路徑
            
        Returns:
            包含分析結果的字典
        """
        try:
            # 讀取影像檔案
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            return self._analyze_image_data(image_data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到影像檔案: {image_path}")
        except Exception as e:
            raise Exception(f"分析影像時發生錯誤: {str(e)}")
    
    def analyze_image_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        從位元組資料分析影像
        
        Args:
            image_bytes: 影像位元組資料
            
        Returns:
            包含分析結果的字典
        """
        return self._analyze_image_data(image_bytes)
    
    def _analyze_image_data(self, image_data: bytes) -> Dict:
        """
        使用 Azure Computer Vision API 分析影像資料
        
        Args:
            image_data: 影像位元組資料
            
        Returns:
            分析結果字典
        """
        # 設定 API 端點
        vision_url = f"{self.endpoint}/vision/v3.2/analyze"
        
        # 設定請求標頭
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': self.key
        }
        
        # 設定分析參數
        params = {
            'visualFeatures': 'Categories,Description,Tags,Objects',
            'language': 'zh',
            'model-version': 'latest'
        }
        
        try:
            # 發送請求
            response = requests.post(vision_url, headers=headers, params=params, data=image_data)
            response.raise_for_status()
            
            # 解析回應
            result = response.json()
            
            # 處理結果
            return self._process_analysis_result(result)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"解析 API 回應失敗: {str(e)}")
    
    def _process_analysis_result(self, result: Dict) -> Dict:
        """
        處理 Azure Computer Vision API 的分析結果
        
        Args:
            result: API 回應結果
            
        Returns:
            處理後的食物分析結果
        """
        processed_result = {
            'success': True,
            'foods_detected': [],
            'description': '',
            'tags': [],
            'confidence_scores': {},
            'nutrition_info': {},
            'recommendations': []
        }
        
        # 提取描述
        if 'description' in result and 'captions' in result['description']:
            captions = result['description']['captions']
            if captions:
                processed_result['description'] = captions[0]['text']
        
        # 提取標籤
        if 'tags' in result and result['tags']:
            processed_result['tags'] = [tag['name'] for tag in result['tags'] if 'name' in tag]
            
            # 識別食物相關標籤
            food_tags = self._identify_food_tags(result['tags'])
            processed_result['foods_detected'] = food_tags
            
            # 計算信心分數
            for tag in result['tags']:
                if 'name' in tag:
                    processed_result['confidence_scores'][tag['name']] = tag.get('confidence', 0)
        
        # 提取物件
        if 'objects' in result and result['objects']:
            objects = result['objects']
            for obj in objects:
                if obj.get('confidence', 0) > 0.7 and 'object' in obj:  # 只保留高信心度的物件
                    processed_result['foods_detected'].append(obj['object'])
        
        # 提取分類
        if 'categories' in result and result['categories']:
            categories = result['categories']
            for category in categories:
                if category.get('score', 0) > 0.5 and 'name' in category:  # 只保留高信心度的分類
                    category_name = category['name']
                    if 'food' in category_name.lower() or 'meal' in category_name.lower():
                        processed_result['foods_detected'].append(category_name)
        
        # 移除重複項目
        processed_result['foods_detected'] = list(set(processed_result['foods_detected']))
        
        # 生成營養資訊建議
        processed_result['nutrition_info'] = self._generate_nutrition_info(processed_result['foods_detected'])
        
        # 生成飲食建議
        processed_result['recommendations'] = self._generate_recommendations(processed_result['foods_detected'])
        
        return processed_result
    
    def _identify_food_tags(self, tags: List[Dict]) -> List[str]:
        """
        識別食物相關的標籤
        
        Args:
            tags: API 回傳的標籤列表
            
        Returns:
            食物標籤列表
        """
        food_tags = []
        
        # 常見食物關鍵字
        food_keywords = [
            'food', 'meal', 'dish', 'cuisine', 'restaurant', 'cooking',
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon',
            'rice', 'noodle', 'bread', 'pizza', 'hamburger', 'sandwich',
            'chicken', 'beef', 'pork', 'fish', 'shrimp', 'salmon',
            'vegetable', 'carrot', 'broccoli', 'tomato', 'lettuce', 'onion',
            'soup', 'salad', 'dessert', 'cake', 'ice cream', 'chocolate',
            'drink', 'coffee', 'tea', 'juice', 'milk', 'water',
            'sushi', 'ramen', 'curry', 'pasta', 'steak', 'seafood'
        ]
        
        if not tags:
            return food_tags
            
        for tag in tags:
            if 'name' not in tag:
                continue
            tag_name = tag['name'].lower()
            if any(keyword in tag_name for keyword in food_keywords):
                food_tags.append(tag['name'])
        
        return food_tags
    
    def _generate_nutrition_info(self, foods: List[str]) -> Dict:
        """
        根據檢測到的食物生成營養資訊
        
        Args:
            foods: 檢測到的食物列表
            
        Returns:
            營養資訊字典
        """
        nutrition_info = {
            'total_calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0,
            'vitamins': [],
            'minerals': []
        }
        
        # 簡化的營養資料庫
        nutrition_db = {
            'apple': {'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3, 'fiber': 4},
            'banana': {'calories': 105, 'protein': 1.3, 'carbs': 27, 'fat': 0.4, 'fiber': 3},
            'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4},
            'chicken': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0},
            'salad': {'calories': 20, 'protein': 2, 'carbs': 4, 'fat': 0.2, 'fiber': 2},
            'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2},
            'soup': {'calories': 50, 'protein': 3, 'carbs': 8, 'fat': 1, 'fiber': 2},
            'bread': {'calories': 79, 'protein': 3, 'carbs': 15, 'fat': 1, 'fiber': 1},
            'fish': {'calories': 100, 'protein': 20, 'carbs': 0, 'fat': 2, 'fiber': 0},
            'vegetable': {'calories': 25, 'protein': 2, 'carbs': 5, 'fat': 0.2, 'fiber': 3}
        }
        
        for food in foods:
            food_lower = food.lower()
            for db_food, nutrition in nutrition_db.items():
                if db_food in food_lower:
                    nutrition_info['total_calories'] += nutrition['calories']
                    nutrition_info['protein'] += nutrition['protein']
                    nutrition_info['carbohydrates'] += nutrition['carbs']
                    nutrition_info['fat'] += nutrition['fat']
                    nutrition_info['fiber'] += nutrition['fiber']
                    break
        
        return nutrition_info
    
    def _generate_recommendations(self, foods: List[str]) -> List[str]:
        """
        根據檢測到的食物生成飲食建議
        
        Args:
            foods: 檢測到的食物列表
            
        Returns:
            建議列表
        """
        recommendations = []
        
        # 分析食物類型
        has_protein = any(keyword in ' '.join(foods).lower() for keyword in ['chicken', 'beef', 'fish', 'pork', 'meat'])
        has_vegetables = any(keyword in ' '.join(foods).lower() for keyword in ['vegetable', 'salad', 'carrot', 'broccoli'])
        has_fruits = any(keyword in ' '.join(foods).lower() for keyword in ['apple', 'banana', 'orange', 'fruit'])
        has_grains = any(keyword in ' '.join(foods).lower() for keyword in ['rice', 'bread', 'pasta', 'noodle'])
        
        if not has_protein:
            recommendations.append("建議添加蛋白質來源，如雞肉、魚肉或豆類")
        
        if not has_vegetables:
            recommendations.append("建議添加蔬菜以增加纖維和維生素攝取")
        
        if not has_fruits:
            recommendations.append("建議添加水果以補充維生素和礦物質")
        
        if not has_grains:
            recommendations.append("建議添加全穀類以提供能量和纖維")
        
        if len(foods) < 3:
            recommendations.append("建議增加食物種類以獲得均衡營養")
        
        if not recommendations:
            recommendations.append("這是一頓營養均衡的餐點！")
        
        return recommendations
    
    def get_detailed_analysis(self, image_path: str) -> Dict:
        """
        獲取詳細的食物分析報告
        
        Args:
            image_path: 影像檔案路徑
            
        Returns:
            詳細分析報告
        """
        basic_result = self.analyze_image(image_path)
        
        # 添加額外的分析資訊
        detailed_result = basic_result.copy()
        detailed_result['analysis_timestamp'] = str(datetime.now())
        detailed_result['image_path'] = image_path
        
        # 計算健康評分
        health_score = self._calculate_health_score(basic_result['nutrition_info'])
        detailed_result['health_score'] = health_score
        
        return detailed_result
    
    def _calculate_health_score(self, nutrition_info: Dict) -> int:
        """
        計算健康評分 (0-100)
        
        Args:
            nutrition_info: 營養資訊
            
        Returns:
            健康評分
        """
        score = 50  # 基礎分數
        
        calories = nutrition_info['total_calories']
        protein = nutrition_info['protein']
        carbs = nutrition_info['carbohydrates']
        fat = nutrition_info['fat']
        fiber = nutrition_info['fiber']
        
        # 根據營養素調整分數
        if 200 <= calories <= 800:
            score += 10
        elif calories < 200:
            score += 5
        else:
            score -= 10
        
        if protein >= 15:
            score += 10
        elif protein >= 10:
            score += 5
        
        if carbs <= 50:
            score += 10
        elif carbs <= 80:
            score += 5
        
        if fat <= 20:
            score += 10
        elif fat <= 30:
            score += 5
        
        if fiber >= 5:
            score += 10
        elif fiber >= 3:
            score += 5
        
        return max(0, min(100, score)) 