"""
Azure AI 食物影像辨識 - 命令列版本
提供簡單的命令列介面來分析食物影像
"""

import argparse
import json
import sys
from pathlib import Path
from food_recognition import FoodRecognition

def main():
    """主命令列函數"""
    parser = argparse.ArgumentParser(
        description="Azure AI 食物影像辨識工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python cli.py image.jpg                    # 基本分析
  python cli.py image.jpg --detailed         # 詳細分析
  python cli.py image.jpg --output result.json  # 輸出到JSON檔案
  python cli.py image.jpg --confidence 0.8   # 設定信心度閾值
        """
    )
    
    parser.add_argument(
        'image_path',
        help='影像檔案路徑'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='顯示詳細分析結果'
    )
    
    parser.add_argument(
        '--output',
        help='輸出結果到指定檔案 (JSON格式)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.7,
        help='信心度閾值 (預設: 0.7)'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='輸出格式 (預設: text)'
    )
    
    args = parser.parse_args()
    
    # 檢查檔案是否存在
    if not Path(args.image_path).exists():
        print(f"❌ 錯誤：找不到影像檔案 '{args.image_path}'")
        sys.exit(1)
    
    try:
        # 初始化食物辨識器
        print("🔍 初始化 Azure AI 食物辨識器...")
        food_recognizer = FoodRecognition()
        
        # 分析影像
        print(f"📸 分析影像: {args.image_path}")
        if args.detailed:
            result = food_recognizer.get_detailed_analysis(args.image_path)
        else:
            result = food_recognizer.analyze_image(args.image_path)
        
        # 顯示結果
        if args.format == 'json':
            display_json_result(result, args.output)
        else:
            display_text_result(result, args.confidence, args.detailed)
        
        # 輸出到檔案
        if args.output:
            save_result_to_file(result, args.output)
            print(f"💾 結果已儲存到: {args.output}")
        
    except Exception as e:
        print(f"❌ 錯誤：{str(e)}")
        sys.exit(1)

def display_text_result(result, confidence_threshold, detailed=False):
    """以文字格式顯示結果"""
    
    print("\n" + "="*50)
    print("🍽️ 食物影像分析結果")
    print("="*50)
    
    # 基本資訊
    if result.get('description'):
        print(f"\n📝 影像描述：{result['description']}")
    
    # 檢測到的食物
    if result.get('foods_detected'):
        print(f"\n🍽️ 檢測到的食物 (信心度 > {confidence_threshold*100:.0f}%)：")
        
        filtered_foods = []
        for food in result['foods_detected']:
            confidence = result.get('confidence_scores', {}).get(food, 1.0)
            if confidence >= confidence_threshold:
                filtered_foods.append((food, confidence))
        
        if filtered_foods:
            for i, (food, confidence) in enumerate(filtered_foods, 1):
                confidence_percent = confidence * 100
                print(f"  {i}. {food} (信心度: {confidence_percent:.1f}%)")
        else:
            print(f"  ⚠️ 沒有信心度超過 {confidence_threshold*100:.0f}% 的食物被檢測到")
    
    # 營養資訊
    if detailed and result.get('nutrition_info'):
        nutrition = result['nutrition_info']
        print(f"\n🥗 營養分析：")
        print(f"  卡路里: {nutrition.get('total_calories', 0)} kcal")
        print(f"  蛋白質: {nutrition.get('protein', 0):.1f} g")
        print(f"  碳水化合物: {nutrition.get('carbohydrates', 0):.1f} g")
        print(f"  脂肪: {nutrition.get('fat', 0):.1f} g")
        print(f"  纖維: {nutrition.get('fiber', 0):.1f} g")
    
    # 健康評分
    if detailed and result.get('health_score') is not None:
        health_score = result['health_score']
        print(f"\n🏥 健康評分：{health_score}/100")
        
        if health_score >= 80:
            level = "優秀"
        elif health_score >= 60:
            level = "良好"
        elif health_score >= 40:
            level = "一般"
        else:
            level = "需要改善"
        
        print(f"  健康等級：{level}")
    
    # 建議
    if result.get('recommendations'):
        print(f"\n💡 飲食建議：")
        for i, recommendation in enumerate(result['recommendations'], 1):
            print(f"  {i}. {recommendation}")
    
    # 所有標籤（用於除錯）
    if result.get('tags'):
        print(f"\n🏷️ 所有檢測到的標籤：")
        print(f"  {', '.join(result['tags'])}")
    
    print("\n" + "="*50)

def display_json_result(result, output_file=None):
    """以JSON格式顯示結果"""
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"💾 結果已儲存到: {output_file}")
    else:
        print(json_output)

def save_result_to_file(result, output_file):
    """儲存結果到檔案"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main() 