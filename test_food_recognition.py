"""
Azure AI 食物影像辨識 - 測試檔案
用於驗證食物辨識功能的正確性
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch
from food_recognition import FoodRecognition

class TestFoodRecognition(unittest.TestCase):
    """食物辨識測試類別"""
    
    def setUp(self):
        """測試前設定"""
        # 模擬環境變數
        os.environ['AZURE_VISION_ENDPOINT'] = 'https://test.cognitiveservices.azure.com/'
        os.environ['AZURE_VISION_KEY'] = 'test-key'
        
        self.recognizer = FoodRecognition()
    
    def test_initialization(self):
        """測試初始化"""
        self.assertEqual(self.recognizer.endpoint, 'https://test.cognitiveservices.azure.com')
        self.assertEqual(self.recognizer.key, 'test-key')
    
    def test_missing_environment_variables(self):
        """測試缺少環境變數"""
        # 清除環境變數
        if 'AZURE_VISION_ENDPOINT' in os.environ:
            del os.environ['AZURE_VISION_ENDPOINT']
        if 'AZURE_VISION_KEY' in os.environ:
            del os.environ['AZURE_VISION_KEY']
        
        with self.assertRaises(ValueError):
            FoodRecognition()
    
    @patch('requests.post')
    def test_analyze_image_success(self, mock_post):
        """測試成功分析影像"""
        # 模擬 API 回應
        mock_response = Mock()
        mock_response.json.return_value = {
            'description': {
                'captions': [{'text': '一盤新鮮的水果沙拉'}]
            },
            'tags': [
                {'name': 'apple', 'confidence': 0.95},
                {'name': 'banana', 'confidence': 0.87},
                {'name': 'salad', 'confidence': 0.92},
                {'name': 'food', 'confidence': 0.98}
            ],
            'objects': [
                {'object': 'apple', 'confidence': 0.95},
                {'object': 'banana', 'confidence': 0.87}
            ],
            'categories': [
                {'name': 'food_meal', 'score': 0.85}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 創建測試影像檔案
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'fake image data')
            image_path = f.name
        
        try:
            result = self.recognizer.analyze_image(image_path)
            
            # 驗證結果
            self.assertTrue(result['success'])
            self.assertIn('apple', result['foods_detected'])
            self.assertIn('banana', result['foods_detected'])
            self.assertIn('salad', result['foods_detected'])
            self.assertEqual(result['description'], '一盤新鮮的水果沙拉')
            self.assertGreater(len(result['recommendations']), 0)
            
        finally:
            # 清理測試檔案
            os.unlink(image_path)
    
    @patch('requests.post')
    def test_analyze_image_api_error(self, mock_post):
        """測試 API 錯誤處理"""
        # 模擬 API 錯誤
        mock_post.side_effect = Exception("API Error")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b'fake image data')
            image_path = f.name
        
        try:
            with self.assertRaises(Exception):
                self.recognizer.analyze_image(image_path)
        finally:
            os.unlink(image_path)
    
    def test_identify_food_tags(self):
        """測試食物標籤識別"""
        tags = [
            {'name': 'apple', 'confidence': 0.95},
            {'name': 'car', 'confidence': 0.87},  # 非食物
            {'name': 'chicken', 'confidence': 0.92},
            {'name': 'building', 'confidence': 0.75}  # 非食物
        ]
        
        food_tags = self.recognizer._identify_food_tags(tags)
        
        self.assertIn('apple', food_tags)
        self.assertIn('chicken', food_tags)
        self.assertNotIn('car', food_tags)
        self.assertNotIn('building', food_tags)
    
    def test_generate_nutrition_info(self):
        """測試營養資訊生成"""
        foods = ['apple', 'chicken', 'rice']
        
        nutrition_info = self.recognizer._generate_nutrition_info(foods)
        
        self.assertGreater(nutrition_info['total_calories'], 0)
        self.assertGreater(nutrition_info['protein'], 0)
        self.assertGreater(nutrition_info['carbohydrates'], 0)
        self.assertGreaterEqual(nutrition_info['fat'], 0)
        self.assertGreaterEqual(nutrition_info['fiber'], 0)
    
    def test_generate_recommendations(self):
        """測試建議生成"""
        # 測試均衡飲食
        balanced_foods = ['chicken', 'salad', 'rice', 'apple']
        recommendations = self.recognizer._generate_recommendations(balanced_foods)
        self.assertIn("這是一頓營養均衡的餐點！", recommendations)
        
        # 測試缺少蛋白質
        no_protein_foods = ['apple', 'salad', 'rice']
        recommendations = self.recognizer._generate_recommendations(no_protein_foods)
        self.assertIn("建議添加蛋白質來源", recommendations)
        
        # 測試缺少蔬菜
        no_vegetables_foods = ['chicken', 'rice', 'apple']
        recommendations = self.recognizer._generate_recommendations(no_vegetables_foods)
        self.assertIn("建議添加蔬菜", recommendations)
    
    def test_calculate_health_score(self):
        """測試健康評分計算"""
        # 測試健康飲食
        healthy_nutrition = {
            'total_calories': 400,
            'protein': 25,
            'carbohydrates': 45,
            'fat': 15,
            'fiber': 8
        }
        score = self.recognizer._calculate_health_score(healthy_nutrition)
        self.assertGreaterEqual(score, 70)
        
        # 測試不健康飲食
        unhealthy_nutrition = {
            'total_calories': 1200,
            'protein': 5,
            'carbohydrates': 150,
            'fat': 50,
            'fiber': 2
        }
        score = self.recognizer._calculate_health_score(unhealthy_nutrition)
        self.assertLess(score, 50)
    
    def test_file_not_found(self):
        """測試檔案不存在錯誤"""
        with self.assertRaises(FileNotFoundError):
            self.recognizer.analyze_image("nonexistent_file.jpg")

class TestFoodRecognitionIntegration(unittest.TestCase):
    """整合測試類別"""
    
    @unittest.skip("需要真實的 Azure API 金鑰")
    def test_real_api_integration(self):
        """真實 API 整合測試（需要跳過）"""
        # 這個測試需要真實的 Azure API 金鑰
        # 在實際環境中可以使用真實的金鑰進行測試
        pass

if __name__ == '__main__':
    # 執行測試
    unittest.main(verbosity=2) 