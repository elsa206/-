#!/usr/bin/env python3
"""
Azure AI 食物影像辨識 - API 腳本
用於處理來自 Node.js 服務器的食物辨識請求
"""

import sys
import json
import argparse
import requests
from food_recognition import FoodRecognition

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Azure AI 食物影像辨識 API')
    parser.add_argument('image_path', nargs='?', help='影像檔案路徑')
    parser.add_argument('--url', help='影像URL')
    
    args = parser.parse_args()
    
    try:
        # 初始化食物辨識器
        food_recognizer = FoodRecognition()
        
        if args.url:
            # 從URL處理影像
            response = requests.get(args.url)
            response.raise_for_status()
            image_data = response.content
            result = food_recognizer.analyze_image_from_bytes(image_data)
        elif args.image_path:
            # 從檔案路徑處理影像
            result = food_recognizer.analyze_image(args.image_path)
        else:
            print(json.dumps({
                'success': False,
                'error': '請提供影像檔案路徑或URL'
            }))
            sys.exit(1)
        
        # 輸出JSON結果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main() 