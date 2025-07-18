#!/usr/bin/env python3
"""
增強版食物偵測模組
整合台灣FDA食品營養成分資料庫
"""

import os
import json
import requests
import numpy as np
import cv2
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io
import base64
from dotenv import load_dotenv
from datetime import datetime
import logging
import re

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFoodDetectionResult:
    """增強版食物偵測結果類別"""
    
    def __init__(self):
        self.foods_detected = []
        self.description = ""
        self.tags = []
        self.confidence_scores = {}
        self.nutrition_info = {}
        self.recommendations = []
        self.health_score = 0
        self.bounding_boxes = []
        self.timestamp = datetime.now()
        self.success = False
        self.error_message = ""
        self.fda_matches = []  # FDA資料庫匹配結果
        self.local_foods = []  # 本地食品匹配

class EnhancedFoodDetector:
    """增強版食物偵測器類別"""
    
    def __init__(self, fda_db_path: Optional[str] = None):
        """初始化增強版食物偵測器"""
        self.endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        self.key = os.getenv('AZURE_VISION_KEY')
        
        if not self.endpoint or not self.key:
            raise ValueError("請設定 AZURE_VISION_ENDPOINT 和 AZURE_VISION_KEY 環境變數")
        
        # 移除結尾的斜線
        self.endpoint = self.endpoint.rstrip('/')
        
        # 載入FDA營養資料庫
        self.fda_nutrition_db = {}
        if fda_db_path and os.path.exists(fda_db_path):
            self.load_fda_database(fda_db_path)
        
        # 本地營養資料庫 (原有)
        self.local_nutrition_db = {
            'apple': {'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3, 'fiber': 4, 'vitamins': ['C', 'K']},
            'banana': {'calories': 105, 'protein': 1.3, 'carbs': 27, 'fat': 0.4, 'fiber': 3, 'vitamins': ['B6', 'C']},
            'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fat': 0.3, 'fiber': 0.4, 'vitamins': ['B1', 'B3']},
            'chicken': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0, 'vitamins': ['B6', 'B12']},
            'salad': {'calories': 20, 'protein': 2, 'carbs': 4, 'fat': 0.2, 'fiber': 2, 'vitamins': ['A', 'C', 'K']},
            'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2, 'vitamins': ['B1', 'B2']},
            'soup': {'calories': 50, 'protein': 3, 'carbs': 8, 'fat': 1, 'fiber': 2, 'vitamins': ['A', 'C']},
            'bread': {'calories': 79, 'protein': 3, 'carbs': 15, 'fat': 1, 'fiber': 1, 'vitamins': ['B1', 'B2']},
            'fish': {'calories': 100, 'protein': 20, 'carbs': 0, 'fat': 2, 'fiber': 0, 'vitamins': ['D', 'B12']},
            'vegetable': {'calories': 25, 'protein': 2, 'carbs': 5, 'fat': 0.2, 'fiber': 3, 'vitamins': ['A', 'C']},
            'beef': {'calories': 250, 'protein': 26, 'carbs': 0, 'fat': 15, 'fiber': 0, 'vitamins': ['B12', 'B6']},
            'pork': {'calories': 242, 'protein': 27, 'carbs': 0, 'fat': 14, 'fiber': 0, 'vitamins': ['B1', 'B6']},
            'shrimp': {'calories': 85, 'protein': 18, 'carbs': 0, 'fat': 1, 'fiber': 0, 'vitamins': ['B12', 'D']},
            'salmon': {'calories': 208, 'protein': 25, 'carbs': 0, 'fat': 12, 'fiber': 0, 'vitamins': ['D', 'B12']},
            'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'vitamins': ['A', 'K']},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'vitamins': ['C', 'K']},
            'tomato': {'calories': 22, 'protein': 1.1, 'carbs': 5, 'fat': 0.2, 'fiber': 1.2, 'vitamins': ['C', 'K']},
            'lettuce': {'calories': 15, 'protein': 1.4, 'carbs': 3, 'fat': 0.1, 'fiber': 1.3, 'vitamins': ['A', 'K']},
            'onion': {'calories': 40, 'protein': 1.1, 'carbs': 9, 'fat': 0.1, 'fiber': 1.7, 'vitamins': ['C', 'B6']},
            'potato': {'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.2, 'vitamins': ['C', 'B6']},
            'corn': {'calories': 86, 'protein': 3.2, 'carbs': 19, 'fat': 1.2, 'fiber': 2.7, 'vitamins': ['B1', 'B5']},
            'egg': {'calories': 78, 'protein': 6.3, 'carbs': 0.6, 'fat': 5.3, 'fiber': 0, 'vitamins': ['D', 'B12']},
            'cheese': {'calories': 113, 'protein': 7, 'carbs': 0.4, 'fat': 9, 'fiber': 0, 'vitamins': ['A', 'B12']},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fat': 1, 'fiber': 0, 'vitamins': ['D', 'B12']},
            'coffee': {'calories': 2, 'protein': 0.3, 'carbs': 0, 'fat': 0, 'fiber': 0, 'vitamins': ['B3']},
            'tea': {'calories': 1, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0, 'vitamins': ['C']},
            'orange': {'calories': 62, 'protein': 1.2, 'carbs': 15, 'fat': 0.2, 'fiber': 3.1, 'vitamins': ['C', 'B9']},
            'grape': {'calories': 62, 'protein': 0.6, 'carbs': 16, 'fat': 0.2, 'fiber': 0.9, 'vitamins': ['C', 'K']},
            'strawberry': {'calories': 32, 'protein': 0.7, 'carbs': 8, 'fat': 0.3, 'fiber': 2, 'vitamins': ['C', 'B9']},
            'watermelon': {'calories': 30, 'protein': 0.6, 'carbs': 8, 'fat': 0.2, 'fiber': 0.4, 'vitamins': ['A', 'C']},
            'noodle': {'calories': 138, 'protein': 5, 'carbs': 25, 'fat': 2, 'fiber': 1, 'vitamins': ['B1', 'B2']},
            'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fat': 1, 'fiber': 1, 'vitamins': ['B1', 'B2']},
            'hamburger': {'calories': 295, 'protein': 12, 'carbs': 30, 'fat': 12, 'fiber': 2, 'vitamins': ['B12', 'B6']},
            'sandwich': {'calories': 250, 'protein': 15, 'carbs': 30, 'fat': 8, 'fiber': 3, 'vitamins': ['B1', 'B2']},
            'sushi': {'calories': 150, 'protein': 6, 'carbs': 30, 'fat': 0.5, 'fiber': 0.5, 'vitamins': ['B12', 'D']},
            'ramen': {'calories': 200, 'protein': 8, 'carbs': 35, 'fat': 3, 'fiber': 2, 'vitamins': ['B1', 'B2']},
            'curry': {'calories': 180, 'protein': 8, 'carbs': 25, 'fat': 6, 'fiber': 3, 'vitamins': ['A', 'C']},
            'steak': {'calories': 271, 'protein': 26, 'carbs': 0, 'fat': 18, 'fiber': 0, 'vitamins': ['B12', 'B6']},
            'seafood': {'calories': 100, 'protein': 20, 'carbs': 0, 'fat': 2, 'fiber': 0, 'vitamins': ['D', 'B12']},
            'dessert': {'calories': 300, 'protein': 4, 'carbs': 45, 'fat': 12, 'fiber': 1, 'vitamins': ['A']},
            'cake': {'calories': 257, 'protein': 3, 'carbs': 45, 'fat': 8, 'fiber': 1, 'vitamins': ['A']},
            'ice cream': {'calories': 207, 'protein': 3.5, 'carbs': 24, 'fat': 11, 'fiber': 0, 'vitamins': ['A']},
            'chocolate': {'calories': 546, 'protein': 4.9, 'carbs': 61, 'fat': 31, 'fiber': 7, 'vitamins': ['B2']}
        }
        
        # 食物關鍵字資料庫
        self.food_keywords = [
            'food', 'meal', 'dish', 'cuisine', 'restaurant', 'cooking',
            'apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon',
            'rice', 'noodle', 'bread', 'pizza', 'hamburger', 'sandwich',
            'chicken', 'beef', 'pork', 'fish', 'shrimp', 'salmon',
            'vegetable', 'carrot', 'broccoli', 'tomato', 'lettuce', 'onion',
            'soup', 'salad', 'dessert', 'cake', 'ice cream', 'chocolate',
            'drink', 'coffee', 'tea', 'juice', 'milk', 'water',
            'sushi', 'ramen', 'curry', 'pasta', 'steak', 'seafood',
            'egg', 'cheese', 'yogurt', 'butter', 'oil', 'sauce',
            'potato', 'corn', 'pepper', 'cucumber', 'spinach', 'kale',
            'mushroom', 'garlic', 'ginger', 'lemon', 'lime', 'mango',
            'peach', 'pear', 'cherry', 'blueberry', 'raspberry', 'blackberry'
        ]
        
        # 添加中文食物關鍵字
        self.chinese_food_keywords = [
            '米', '麵', '飯', '粥', '包子', '饅頭', '麵包', '餅乾',
            '肉', '魚', '蝦', '蟹', '蛋', '奶', '豆', '菜', '水果',
            '湯', '沙拉', '甜點', '蛋糕', '冰淇淋', '巧克力',
            '飲料', '咖啡', '茶', '果汁', '牛奶', '水',
            '壽司', '拉麵', '咖哩', '義大利麵', '牛排', '海鮮',
            '起司', '優格', '奶油', '油', '醬料',
            '馬鈴薯', '玉米', '辣椒', '小黃瓜', '菠菜', '羽衣甘藍',
            '香菇', '大蒜', '薑', '檸檬', '萊姆', '芒果',
            '桃子', '梨子', '櫻桃', '藍莓', '覆盆子', '黑莓',
            '蘋果', '香蕉', '橘子', '葡萄', '草莓', '西瓜',
            '胡蘿蔔', '花椰菜', '番茄', '生菜', '洋蔥',
            '雞肉', '牛肉', '豬肉', '魚肉', '蝦仁', '鮭魚'
        ]
        
        logger.info(f"增強版食物偵測器初始化完成，FDA資料庫包含 {len(self.fda_nutrition_db)} 種食品")
    
    def load_fda_database(self, db_path: str):
        """載入FDA營養資料庫"""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.fda_nutrition_db = json.load(f)
            
            logger.info(f"成功載入FDA營養資料庫: {len(self.fda_nutrition_db)} 種食品")
            
        except Exception as e:
            logger.error(f"載入FDA資料庫失敗: {e}")
    
    def detect_food_from_frame(self, frame: np.ndarray) -> EnhancedFoodDetectionResult:
        """從影像幀偵測食物"""
        result = EnhancedFoodDetectionResult()
        
        try:
            # 將 numpy array 轉換為 bytes
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                result.error_message = "影像編碼失敗"
                return result
            
            image_bytes = buffer.tobytes()
            
            # 分析影像
            analysis_result = self._analyze_image_data(image_bytes)
            
            # 處理結果
            result = self._process_analysis_result(analysis_result)
            result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"食物偵測失敗: {e}")
        
        return result
    
    def _analyze_image_data(self, image_data: bytes) -> Dict:
        """使用 Azure Computer Vision API 分析影像資料"""
        vision_url = f"{self.endpoint}/vision/v3.2/analyze"
        
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': self.key
        }
        
        params = {
            'visualFeatures': 'Categories,Description,Tags,Objects',
            'language': 'zh',
            'model-version': 'latest'
        }
        
        try:
            response = requests.post(vision_url, headers=headers, params=params, data=image_data)
            response.raise_for_status()
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"解析 API 回應失敗: {str(e)}")
    
    def _process_analysis_result(self, result: Dict) -> EnhancedFoodDetectionResult:
        """處理 Azure Computer Vision API 的分析結果"""
        detection_result = EnhancedFoodDetectionResult()
        
        # 提取描述
        if 'description' in result and 'captions' in result['description']:
            captions = result['description']['captions']
            if captions:
                detection_result.description = captions[0]['text']
        
        # 提取標籤
        if 'tags' in result and result['tags']:
            detection_result.tags = [tag['name'] for tag in result['tags'] if 'name' in tag]
            
            # 識別食物相關標籤
            food_tags = self._identify_food_tags(result['tags'])
            detection_result.foods_detected = food_tags
            
            # 計算信心分數
            for tag in result['tags']:
                if 'name' in tag:
                    detection_result.confidence_scores[tag['name']] = tag.get('confidence', 0)
        
        # 提取物件
        if 'objects' in result and result['objects']:
            objects = result['objects']
            for obj in objects:
                if obj.get('confidence', 0) > 0.7 and 'object' in obj:
                    detection_result.foods_detected.append(obj['object'])
                    
                    # 提取邊界框
                    if 'rectangle' in obj:
                        bbox = obj['rectangle']
                        detection_result.bounding_boxes.append({
                            'object': obj['object'],
                            'confidence': obj.get('confidence', 0),
                            'x': bbox.get('x', 0),
                            'y': bbox.get('y', 0),
                            'w': bbox.get('w', 0),
                            'h': bbox.get('h', 0)
                        })
        
        # 提取分類
        if 'categories' in result and result['categories']:
            categories = result['categories']
            for category in categories:
                if category.get('score', 0) > 0.5 and 'name' in category:
                    category_name = category['name']
                    if 'food' in category_name.lower() or 'meal' in category_name.lower():
                        detection_result.foods_detected.append(category_name)
        
        # 移除重複項目
        detection_result.foods_detected = list(set(detection_result.foods_detected))
        
        # 匹配FDA資料庫
        detection_result.fda_matches = self._match_fda_database(detection_result.foods_detected)
        
        # 匹配本地資料庫
        detection_result.local_foods = self._match_local_database(detection_result.foods_detected)
        
        # 生成營養資訊
        detection_result.nutrition_info = self._generate_enhanced_nutrition_info(
            detection_result.foods_detected,
            detection_result.fda_matches,
            detection_result.local_foods
        )
        
        # 生成飲食建議
        detection_result.recommendations = self._generate_enhanced_recommendations(
            detection_result.foods_detected,
            detection_result.fda_matches,
            detection_result.local_foods
        )
        
        # 計算健康評分
        detection_result.health_score = self._calculate_enhanced_health_score(detection_result.nutrition_info)
        
        detection_result.success = True
        return detection_result
    
    def _identify_food_tags(self, tags: List[Dict]) -> List[str]:
        """識別食物相關的標籤"""
        food_tags = []
        
        if not tags:
            return food_tags
            
        for tag in tags:
            if 'name' not in tag:
                continue
            tag_name = tag['name'].lower()
            
            # 檢查英文關鍵字
            if any(keyword in tag_name for keyword in self.food_keywords):
                food_tags.append(tag['name'])
            
            # 檢查中文關鍵字
            if any(keyword in tag['name'] for keyword in self.chinese_food_keywords):
                food_tags.append(tag['name'])
        
        return food_tags
    
    def _match_fda_database(self, foods: List[str]) -> List[Dict]:
        """匹配FDA資料庫"""
        matches = []
        
        for food in foods:
            food_lower = food.lower()
            
            # 直接匹配
            if food_lower in self.fda_nutrition_db:
                matches.append({
                    'food_name': food,
                    'fda_match': food_lower,
                    'nutrition': self.fda_nutrition_db[food_lower],
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                continue
            
            # 模糊匹配
            for fda_food, nutrition in self.fda_nutrition_db.items():
                # 檢查包含關係
                if food_lower in fda_food or fda_food in food_lower:
                    matches.append({
                        'food_name': food,
                        'fda_match': fda_food,
                        'nutrition': nutrition,
                        'match_type': 'partial',
                        'confidence': 0.8
                    })
                    break
        
        return matches
    
    def _match_local_database(self, foods: List[str]) -> List[Dict]:
        """匹配本地資料庫"""
        matches = []
        
        for food in foods:
            food_lower = food.lower()
            
            # 直接匹配
            if food_lower in self.local_nutrition_db:
                matches.append({
                    'food_name': food,
                    'local_match': food_lower,
                    'nutrition': self.local_nutrition_db[food_lower],
                    'match_type': 'exact',
                    'confidence': 1.0
                })
                continue
            
            # 模糊匹配
            for local_food, nutrition in self.local_nutrition_db.items():
                if food_lower in local_food or local_food in food_lower:
                    matches.append({
                        'food_name': food,
                        'local_match': local_food,
                        'nutrition': nutrition,
                        'match_type': 'partial',
                        'confidence': 0.8
                    })
                    break
        
        return matches
    
    def _generate_enhanced_nutrition_info(self, foods: List[str], fda_matches: List[Dict], local_matches: List[Dict]) -> Dict:
        """生成增強版營養資訊"""
        nutrition_info = {
            'total_calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0,
            'vitamins': [],
            'minerals': [],
            'sources': {
                'fda': len(fda_matches),
                'local': len(local_matches)
            }
        }
        
        # 處理FDA匹配結果
        for match in fda_matches:
            nutrition = match['nutrition']
            confidence = match['confidence']
            
            nutrition_info['total_calories'] += nutrition.get('calories', 0) * confidence
            nutrition_info['protein'] += nutrition.get('protein', 0) * confidence
            nutrition_info['carbohydrates'] += nutrition.get('carbs', 0) * confidence
            nutrition_info['fat'] += nutrition.get('fat', 0) * confidence
            nutrition_info['fiber'] += nutrition.get('fiber', 0) * confidence
            
            # 添加維生素和礦物質
            if 'vitamins' in nutrition:
                nutrition_info['vitamins'].extend(nutrition['vitamins'])
            if 'minerals' in nutrition:
                nutrition_info['minerals'].extend(nutrition['minerals'])
        
        # 處理本地匹配結果
        for match in local_matches:
            nutrition = match['nutrition']
            confidence = match['confidence']
            
            nutrition_info['total_calories'] += nutrition.get('calories', 0) * confidence
            nutrition_info['protein'] += nutrition.get('protein', 0) * confidence
            nutrition_info['carbohydrates'] += nutrition.get('carbs', 0) * confidence
            nutrition_info['fat'] += nutrition.get('fat', 0) * confidence
            nutrition_info['fiber'] += nutrition.get('fiber', 0) * confidence
            
            if 'vitamins' in nutrition:
                nutrition_info['vitamins'].extend(nutrition['vitamins'])
        
        # 移除重複的維生素和礦物質
        nutrition_info['vitamins'] = list(set(nutrition_info['vitamins']))
        nutrition_info['minerals'] = list(set(nutrition_info['minerals']))
        
        return nutrition_info
    
    def _generate_enhanced_recommendations(self, foods: List[str], fda_matches: List[Dict], local_matches: List[Dict]) -> List[str]:
        """生成增強版飲食建議"""
        recommendations = []
        
        # 分析食物類型
        foods_lower = ' '.join(foods).lower()
        has_protein = any(keyword in foods_lower for keyword in ['chicken', 'beef', 'fish', 'pork', 'meat', 'egg', 'cheese', '肉', '魚', '蛋'])
        has_vegetables = any(keyword in foods_lower for keyword in ['vegetable', 'salad', 'carrot', 'broccoli', 'tomato', 'lettuce', 'onion', '菜', '胡蘿蔔', '花椰菜', '番茄', '生菜', '洋蔥'])
        has_fruits = any(keyword in foods_lower for keyword in ['apple', 'banana', 'orange', 'grape', 'strawberry', 'watermelon', 'fruit', '蘋果', '香蕉', '橘子', '葡萄', '草莓', '西瓜'])
        has_grains = any(keyword in foods_lower for keyword in ['rice', 'bread', 'pasta', 'noodle', '米', '麵', '飯', '麵包'])
        has_dairy = any(keyword in foods_lower for keyword in ['milk', 'cheese', 'yogurt', '奶', '起司', '優格'])
        
        # 基本營養建議
        if not has_protein:
            recommendations.append("建議添加蛋白質來源，如雞肉、魚肉、蛋類或豆類")
        
        if not has_vegetables:
            recommendations.append("建議添加蔬菜以增加纖維和維生素攝取")
        
        if not has_fruits:
            recommendations.append("建議添加水果以補充維生素和礦物質")
        
        if not has_grains:
            recommendations.append("建議添加全穀類以提供能量和纖維")
        
        if not has_dairy:
            recommendations.append("建議添加乳製品以補充鈣質和蛋白質")
        
        # FDA資料庫特定建議
        if fda_matches:
            recommendations.append(f"✅ 已匹配到 {len(fda_matches)} 種台灣本地食品資料")
            
            # 檢查是否有台灣特色食品
            taiwan_foods = [match for match in fda_matches if any(keyword in match['fda_match'] for keyword in ['米', '麵', '豆', '茶'])]
            if taiwan_foods:
                recommendations.append("🍜 檢測到台灣特色食品，營養資訊更準確")
        
        # 本地資料庫建議
        if local_matches:
            recommendations.append(f"✅ 已匹配到 {len(local_matches)} 種國際食品資料")
        
        if len(foods) < 3:
            recommendations.append("建議增加食物種類以獲得均衡營養")
        
        # 檢查熱量
        nutrition = self._generate_enhanced_nutrition_info(foods, fda_matches, local_matches)
        if nutrition['total_calories'] < 200:
            recommendations.append("這餐的熱量較低，建議適量增加食物份量")
        elif nutrition['total_calories'] > 800:
            recommendations.append("這餐的熱量較高，建議適量減少食物份量")
        
        if not recommendations:
            recommendations.append("這是一頓營養均衡的餐點！")
        
        return recommendations
    
    def _calculate_enhanced_health_score(self, nutrition_info: Dict) -> int:
        """計算增強版健康評分"""
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
        
        # 維生素加分
        vitamins = nutrition_info.get('vitamins', [])
        if len(vitamins) >= 3:
            score += 5
        elif len(vitamins) >= 1:
            score += 2
        
        # 資料來源加分
        sources = nutrition_info.get('sources', {})
        if sources.get('fda', 0) > 0:
            score += 3  # FDA資料庫加分
        if sources.get('local', 0) > 0:
            score += 2  # 本地資料庫加分
        
        return max(0, min(100, score))
    
    def get_detailed_analysis(self, frame: np.ndarray) -> EnhancedFoodDetectionResult:
        """獲取詳細的食物分析報告"""
        basic_result = self.detect_food_from_frame(frame)
        
        if not basic_result.success:
            return basic_result
        
        # 添加額外的分析資訊
        detailed_result = basic_result
        detailed_result.timestamp = datetime.now()
        
        return detailed_result

# 測試函數
def test_enhanced_food_detection():
    """測試增強版食物偵測功能"""
    print("🧪 測試增強版食物偵測功能...")
    
    try:
        # 嘗試載入FDA資料庫
        fda_db_path = None
        for file in os.listdir('.'):
            if file.startswith('fda_nutrition_db_') and file.endswith('.json'):
                fda_db_path = file
                break
        
        detector = EnhancedFoodDetector(fda_db_path)
        print("✅ 增強版食物偵測器初始化成功")
        
        # 創建測試影像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 測試偵測
        result = detector.detect_food_from_frame(test_image)
        
        if result.success:
            print("✅ 增強版食物偵測成功")
            print(f"🍽️ 檢測到食物: {result.foods_detected}")
            print(f"📝 描述: {result.description}")
            print(f"🏥 健康評分: {result.health_score}")
            print(f"💡 建議: {result.recommendations}")
            print(f"🇹🇼 FDA匹配: {len(result.fda_matches)} 種")
            print(f"🌍 本地匹配: {len(result.local_foods)} 種")
        else:
            print(f"❌ 增強版食物偵測失敗: {result.error_message}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_enhanced_food_detection() 