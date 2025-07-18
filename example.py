"""
Azure AI 食物影像辨識 - 使用範例
展示如何使用食物辨識功能進行影像分析
"""

import os
import json
from food_recognition import FoodRecognition

def basic_example():
    """基本使用範例"""
    print("🍽️ Azure AI 食物影像辨識 - 基本範例")
    print("=" * 50)
    
    try:
        # 初始化食物辨識器
        recognizer = FoodRecognition()
        
        # 分析影像（請替換為實際的影像路徑）
        image_path = "sample_food.jpg"  # 請替換為您的影像檔案
        
        if os.path.exists(image_path):
            print(f"📸 分析影像: {image_path}")
            result = recognizer.analyze_image(image_path)
            
            # 顯示結果
            print(f"\n✅ 分析成功！")
            print(f"📝 描述: {result.get('description', '無描述')}")
            
            if result.get('foods_detected'):
                print(f"\n🍽️ 檢測到的食物:")
                for i, food in enumerate(result['foods_detected'], 1):
                    confidence = result.get('confidence_scores', {}).get(food, 1.0)
                    print(f"  {i}. {food} (信心度: {confidence*100:.1f}%)")
            
            if result.get('recommendations'):
                print(f"\n💡 飲食建議:")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec}")
        else:
            print(f"❌ 找不到影像檔案: {image_path}")
            print("請將您的食物影像檔案命名為 'sample_food.jpg' 並放在同一目錄下")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def detailed_example():
    """詳細分析範例"""
    print("\n🍽️ Azure AI 食物影像辨識 - 詳細分析範例")
    print("=" * 50)
    
    try:
        recognizer = FoodRecognition()
        image_path = "sample_food.jpg"
        
        if os.path.exists(image_path):
            print(f"📸 進行詳細分析: {image_path}")
            result = recognizer.get_detailed_analysis(image_path)
            
            # 顯示詳細結果
            print(f"\n✅ 詳細分析完成！")
            print(f"📅 分析時間: {result.get('analysis_timestamp', '未知')}")
            print(f"🏥 健康評分: {result.get('health_score', 0)}/100")
            
            # 營養資訊
            nutrition = result.get('nutrition_info', {})
            if nutrition:
                print(f"\n🥗 營養分析:")
                print(f"  卡路里: {nutrition.get('total_calories', 0)} kcal")
                print(f"  蛋白質: {nutrition.get('protein', 0):.1f} g")
                print(f"  碳水化合物: {nutrition.get('carbohydrates', 0):.1f} g")
                print(f"  脂肪: {nutrition.get('fat', 0):.1f} g")
                print(f"  纖維: {nutrition.get('fiber', 0):.1f} g")
            
            # 健康評分等級
            health_score = result.get('health_score', 0)
            if health_score >= 80:
                level = "優秀"
            elif health_score >= 60:
                level = "良好"
            elif health_score >= 40:
                level = "一般"
            else:
                level = "需要改善"
            print(f"  健康等級: {level}")
        else:
            print(f"❌ 找不到影像檔案: {image_path}")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def batch_analysis_example():
    """批次分析範例"""
    print("\n🍽️ Azure AI 食物影像辨識 - 批次分析範例")
    print("=" * 50)
    
    try:
        recognizer = FoodRecognition()
        
        # 假設有多個影像檔案
        image_files = [
            "breakfast.jpg",
            "lunch.jpg", 
            "dinner.jpg"
        ]
        
        results = []
        
        for image_file in image_files:
            if os.path.exists(image_file):
                print(f"📸 分析: {image_file}")
                try:
                    result = recognizer.analyze_image(image_file)
                    result['filename'] = image_file
                    results.append(result)
                    print(f"  ✅ 成功 - 檢測到 {len(result.get('foods_detected', []))} 種食物")
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)}")
            else:
                print(f"  ⚠️ 跳過: {image_file} (檔案不存在)")
        
        # 顯示批次分析結果
        if results:
            print(f"\n📊 批次分析完成！共分析了 {len(results)} 個檔案")
            
            # 統計最常見的食物
            all_foods = []
            for result in results:
                all_foods.extend(result.get('foods_detected', []))
            
            if all_foods:
                from collections import Counter
                food_counts = Counter(all_foods)
                print(f"\n🏆 最常見的食物:")
                for food, count in food_counts.most_common(5):
                    print(f"  {food}: {count} 次")
        
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def nutrition_tracking_example():
    """營養追蹤範例"""
    print("\n🍽️ Azure AI 食物影像辨識 - 營養追蹤範例")
    print("=" * 50)
    
    try:
        recognizer = FoodRecognition()
        
        # 模擬一天的餐點
        daily_meals = {
            "早餐": "breakfast.jpg",
            "午餐": "lunch.jpg",
            "晚餐": "dinner.jpg"
        }
        
        daily_nutrition = {
            'total_calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0
        }
        
        meal_results = {}
        
        for meal_name, image_file in daily_meals.items():
            if os.path.exists(image_file):
                print(f"📸 分析{meal_name}: {image_file}")
                try:
                    result = recognizer.analyze_image(image_file)
                    meal_results[meal_name] = result
                    
                    # 累計營養資訊
                    nutrition = result.get('nutrition_info', {})
                    daily_nutrition['total_calories'] += nutrition.get('total_calories', 0)
                    daily_nutrition['protein'] += nutrition.get('protein', 0)
                    daily_nutrition['carbohydrates'] += nutrition.get('carbohydrates', 0)
                    daily_nutrition['fat'] += nutrition.get('fat', 0)
                    daily_nutrition['fiber'] += nutrition.get('fiber', 0)
                    
                    print(f"  ✅ 成功")
                except Exception as e:
                    print(f"  ❌ 失敗: {str(e)}")
            else:
                print(f"  ⚠️ 跳過: {image_file} (檔案不存在)")
        
        # 顯示每日營養總結
        print(f"\n📊 每日營養總結:")
        print(f"  總卡路里: {daily_nutrition['total_calories']} kcal")
        print(f"  總蛋白質: {daily_nutrition['protein']:.1f} g")
        print(f"  總碳水化合物: {daily_nutrition['carbohydrates']:.1f} g")
        print(f"  總脂肪: {daily_nutrition['fat']:.1f} g")
        print(f"  總纖維: {daily_nutrition['fiber']:.1f} g")
        
        # 營養建議
        print(f"\n💡 營養建議:")
        if daily_nutrition['total_calories'] < 1200:
            print("  ⚠️ 卡路里攝取不足，建議增加食量")
        elif daily_nutrition['total_calories'] > 2500:
            print("  ⚠️ 卡路里攝取過多，建議控制食量")
        else:
            print("  ✅ 卡路里攝取適中")
        
        if daily_nutrition['protein'] < 50:
            print("  ⚠️ 蛋白質攝取不足，建議增加蛋白質來源")
        else:
            print("  ✅ 蛋白質攝取充足")
        
        if daily_nutrition['fiber'] < 25:
            print("  ⚠️ 纖維攝取不足，建議增加蔬菜水果")
        else:
            print("  ✅ 纖維攝取充足")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def save_results_example():
    """儲存結果範例"""
    print("\n🍽️ Azure AI 食物影像辨識 - 儲存結果範例")
    print("=" * 50)
    
    try:
        recognizer = FoodRecognition()
        image_path = "sample_food.jpg"
        
        if os.path.exists(image_path):
            print(f"📸 分析影像並儲存結果: {image_path}")
            result = recognizer.get_detailed_analysis(image_path)
            
            # 儲存為 JSON 檔案
            output_file = "food_analysis_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 結果已儲存到: {output_file}")
            
            # 儲存為簡化的文字報告
            report_file = "food_analysis_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("食物影像分析報告\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"影像檔案: {image_path}\n")
                f.write(f"分析時間: {result.get('analysis_timestamp', '未知')}\n\n")
                
                f.write("檢測到的食物:\n")
                for food in result.get('foods_detected', []):
                    f.write(f"  - {food}\n")
                
                f.write(f"\n健康評分: {result.get('health_score', 0)}/100\n")
                
                f.write("\n營養資訊:\n")
                nutrition = result.get('nutrition_info', {})
                f.write(f"  卡路里: {nutrition.get('total_calories', 0)} kcal\n")
                f.write(f"  蛋白質: {nutrition.get('protein', 0):.1f} g\n")
                f.write(f"  碳水化合物: {nutrition.get('carbohydrates', 0):.1f} g\n")
                f.write(f"  脂肪: {nutrition.get('fat', 0):.1f} g\n")
                f.write(f"  纖維: {nutrition.get('fiber', 0):.1f} g\n")
                
                f.write("\n飲食建議:\n")
                for rec in result.get('recommendations', []):
                    f.write(f"  - {rec}\n")
            
            print(f"📄 文字報告已儲存到: {report_file}")
        else:
            print(f"❌ 找不到影像檔案: {image_path}")
    
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def main():
    """主函數"""
    print("🚀 Azure AI 食物影像辨識 - 使用範例")
    print("請確保您已設定 Azure API 金鑰並有測試影像檔案")
    print("=" * 60)
    
    # 檢查環境變數
    if not os.getenv('AZURE_VISION_ENDPOINT') or not os.getenv('AZURE_VISION_KEY'):
        print("❌ 請先設定環境變數:")
        print("  AZURE_VISION_ENDPOINT")
        print("  AZURE_VISION_KEY")
        print("\n請複製 config.env.example 為 .env 並填入您的 API 金鑰")
        return
    
    # 執行各種範例
    basic_example()
    detailed_example()
    batch_analysis_example()
    nutrition_tracking_example()
    save_results_example()
    
    print("\n🎉 所有範例執行完成！")
    print("💡 提示: 您可以修改這些範例來適應您的需求")

if __name__ == "__main__":
    main() 