"""
Azure AI 食物影像辨識 - Streamlit 網頁應用程式
提供使用者友好的介面來上傳和分析食物影像
"""

import streamlit as st
import os
import tempfile
from PIL import Image
import io
import base64
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# 導入自定義模組
from food_recognition import FoodRecognition

# 設定頁面配置
st.set_page_config(
    page_title="Azure AI 食物影像辨識",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .food-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .nutrition-card {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 0.5rem 0;
    }
    .recommendation-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 0.5rem 0;
    }
    .health-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 50%;
        width: 100px;
        height: 100px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主應用程式函數"""
    
    # 頁面標題
    st.markdown('<h1 class="main-header">🍽️ Azure AI 食物影像辨識</h1>', unsafe_allow_html=True)
    st.markdown("### 使用 Azure Computer Vision API 進行智慧食物分析")
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 檢查環境變數
        if not os.getenv('AZURE_VISION_ENDPOINT') or not os.getenv('AZURE_VISION_KEY'):
            st.error("⚠️ 請設定環境變數：")
            st.code("AZURE_VISION_ENDPOINT\nAZURE_VISION_KEY")
            st.info("請複製 config.env.example 為 .env 並填入您的 Azure API 金鑰")
            return
        
        st.success("✅ Azure API 設定完成")
        
        # 功能選項
        st.header("🔧 功能選項")
        analysis_type = st.selectbox(
            "選擇分析類型",
            ["基本分析", "詳細分析", "營養分析", "健康評分"]
        )
        
        confidence_threshold = st.slider(
            "信心度閾值",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="只顯示信心度超過此值的結果"
        )
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📸 上傳影像")
        
        # 檔案上傳
        uploaded_file = st.file_uploader(
            "選擇食物影像檔案",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="支援 PNG, JPG, JPEG, GIF, BMP 格式"
        )
        
        # 或輸入URL
        image_url = st.text_input(
            "或輸入影像URL",
            placeholder="https://example.com/food-image.jpg",
            help="輸入公開可訪問的影像URL"
        )
        
        # 分析按鈕
        analyze_button = st.button(
            "🔍 開始分析",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.header("📋 使用說明")
        st.markdown("""
        1. **上傳影像**：選擇本機食物影像檔案
        2. **或輸入URL**：提供公開的食物影像網址
        3. **選擇分析類型**：在側邊欄選擇所需的分析深度
        4. **開始分析**：點擊分析按鈕開始處理
        5. **查看結果**：系統將顯示詳細的食物分析報告
        """)
        
        st.info("💡 **提示**：為了獲得最佳結果，請確保影像清晰且食物在畫面中佔主要部分")
    
    # 處理分析請求
    if analyze_button and (uploaded_file or image_url):
        try:
            # 初始化食物辨識器
            food_recognizer = FoodRecognition()
            
            # 處理影像
            if uploaded_file:
                # 從上傳檔案處理
                image_data = uploaded_file.read()
                result = food_recognizer.analyze_image_from_bytes(image_data)
                
                # 顯示上傳的影像
                st.image(uploaded_file, caption="上傳的影像", use_column_width=True)
                
            elif image_url:
                # 從URL處理
                import requests
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = response.content
                result = food_recognizer.analyze_image_from_bytes(image_data)
                
                # 顯示URL影像
                st.image(image_url, caption="URL影像", use_column_width=True)
            
            # 顯示分析結果
            display_analysis_results(result, analysis_type, confidence_threshold)
            
        except Exception as e:
            st.error(f"❌ 分析過程中發生錯誤：{str(e)}")
            st.info("請檢查您的網路連線和API設定")
    
    # 範例影像
    elif not uploaded_file and not image_url:
        st.header("📖 範例影像")
        st.markdown("您可以嘗試以下類型的食物影像：")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🍎 水果類**")
            st.markdown("- 蘋果、香蕉、橘子")
            st.markdown("- 草莓、葡萄、西瓜")
        
        with col2:
            st.markdown("**🍖 蛋白質類**")
            st.markdown("- 雞肉、魚肉、牛肉")
            st.markdown("- 豬肉、蝦子、鮭魚")
        
        with col3:
            st.markdown("**🥗 蔬菜類**")
            st.markdown("- 沙拉、胡蘿蔔、花椰菜")
            st.markdown("- 番茄、生菜、洋蔥")

def display_analysis_results(result, analysis_type, confidence_threshold):
    """顯示分析結果"""
    
    st.header("📊 分析結果")
    
    # 基本資訊
    if result.get('description'):
        st.markdown(f"**📝 影像描述：** {result['description']}")
    
    # 檢測到的食物
    if result.get('foods_detected'):
        st.markdown('<h3 class="sub-header">🍽️ 檢測到的食物</h3>', unsafe_allow_html=True)
        
        # 過濾低信心度的結果
        filtered_foods = []
        for food in result['foods_detected']:
            confidence = result.get('confidence_scores', {}).get(food, 1.0)
            if confidence >= confidence_threshold:
                filtered_foods.append((food, confidence))
        
        if filtered_foods:
            for food, confidence in filtered_foods:
                confidence_percent = confidence * 100
                st.markdown(f"""
                <div class="food-card">
                    <strong>{food}</strong> 
                    <span style="color: #666;">(信心度: {confidence_percent:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"沒有信心度超過 {confidence_threshold*100:.0f}% 的食物被檢測到")
    
    # 詳細分析
    if analysis_type in ["詳細分析", "營養分析", "健康評分"]:
        display_nutrition_analysis(result)
    
    # 健康評分
    if analysis_type == "健康評分":
        display_health_score(result)
    
    # 建議
    if result.get('recommendations'):
        st.markdown('<h3 class="sub-header">💡 飲食建議</h3>', unsafe_allow_html=True)
        for recommendation in result['recommendations']:
            st.markdown(f"""
            <div class="recommendation-card">
                {recommendation}
            </div>
            """, unsafe_allow_html=True)
    
    # 原始標籤（用於除錯）
    if st.checkbox("顯示所有檢測到的標籤（除錯用）"):
        if result.get('tags'):
            st.markdown("**🏷️ 所有標籤：**")
            st.write(", ".join(result['tags']))

def display_nutrition_analysis(result):
    """顯示營養分析"""
    
    nutrition_info = result.get('nutrition_info', {})
    
    if nutrition_info:
        st.markdown('<h3 class="sub-header">🥗 營養分析</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("卡路里", f"{nutrition_info.get('total_calories', 0)} kcal")
        
        with col2:
            st.metric("蛋白質", f"{nutrition_info.get('protein', 0):.1f} g")
        
        with col3:
            st.metric("碳水化合物", f"{nutrition_info.get('carbohydrates', 0):.1f} g")
        
        with col4:
            st.metric("脂肪", f"{nutrition_info.get('fat', 0):.1f} g")
        
        with col5:
            st.metric("纖維", f"{nutrition_info.get('fiber', 0):.1f} g")
        
        # 營養素圓餅圖
        if nutrition_info.get('total_calories', 0) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['蛋白質', '碳水化合物', '脂肪'],
                values=[
                    nutrition_info.get('protein', 0) * 4,  # 蛋白質 4 kcal/g
                    nutrition_info.get('carbohydrates', 0) * 4,  # 碳水化合物 4 kcal/g
                    nutrition_info.get('fat', 0) * 9  # 脂肪 9 kcal/g
                ],
                hole=0.3
            )])
            fig.update_layout(title="營養素熱量分布")
            st.plotly_chart(fig, use_container_width=True)

def display_health_score(result):
    """顯示健康評分"""
    
    health_score = result.get('health_score', 0)
    
    st.markdown('<h3 class="sub-header">🏥 健康評分</h3>', unsafe_allow_html=True)
    
    # 根據分數決定顏色
    if health_score >= 80:
        color = "#28a745"  # 綠色
        level = "優秀"
    elif health_score >= 60:
        color = "#ffc107"  # 黃色
        level = "良好"
    elif health_score >= 40:
        color = "#fd7e14"  # 橙色
        level = "一般"
    else:
        color = "#dc3545"  # 紅色
        level = "需要改善"
    
    # 顯示評分
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="health-score" style="background-color: {color}; color: white;">
            {health_score}
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**健康等級：{level}**")
    
    # 進度條
    st.progress(health_score / 100)
    st.markdown(f"**評分說明：** {health_score}/100 分")

if __name__ == "__main__":
    main() 