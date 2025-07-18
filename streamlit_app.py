#!/usr/bin/env python3
"""
WebEye 食物偵測 - Streamlit 應用程式
提供現代化的 Web 界面進行食物偵測和分析
"""

import streamlit as st
import cv2
import numpy as np
import time
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import logging

# 導入自定義模組
from webeye_camera import WebEyeCamera, CameraSettings, WebEyeController
from food_detection import FoodDetector, FoodDetectionResult

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定頁面配置
st.set_page_config(
    page_title="WebEye 食物偵測系統",
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
    .camera-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    .status-online {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-offline {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

class WebEyeStreamlitApp:
    """WebEye Streamlit 應用程式類別"""
    
    def __init__(self):
        """初始化應用程式"""
        self.camera_controller = None
        self.food_detector = None
        self.current_frame = None
        self.detection_results = []
        
        # 初始化組件
        self.init_components()
    
    def init_components(self):
        """初始化組件"""
        try:
            # 初始化相機控制器
            self.camera_controller = WebEyeController()
            
            # 初始化食物偵測器
            self.food_detector = FoodDetector()
            
            logger.info("組件初始化成功")
            
        except Exception as e:
            st.error(f"組件初始化失敗: {e}")
            logger.error(f"組件初始化失敗: {e}")
    
    def setup_camera(self, resolution_str: str, fps: int):
        """設定相機"""
        try:
            # 解析解析度
            width, height = map(int, resolution_str.split('x'))
            resolution = (width, height)
            
            settings = CameraSettings(
                resolution=resolution,
                fps=fps,
                brightness=60,
                contrast=55,
                saturation=50
            )
            
            # 添加相機
            self.camera_controller.add_camera("main", 0, settings)
            self.camera_controller.set_active_camera("main")
            
            return True
            
        except Exception as e:
            st.error(f"相機設定失敗: {e}")
            return False
    
    def capture_frame(self):
        """捕獲影像幀"""
        try:
            if not self.camera_controller:
                return None
            
            camera = self.camera_controller.get_camera("main")
            if not camera:
                return None
            
            frame = camera.capture_photo()
            return frame
            
        except Exception as e:
            st.error(f"影像捕獲失敗: {e}")
            return None
    
    def detect_food(self, frame):
        """偵測食物"""
        try:
            if not self.food_detector or frame is None:
                return None
            
            result = self.food_detector.detect_food_from_frame(frame)
            return result
            
        except Exception as e:
            st.error(f"食物偵測失敗: {e}")
            return None
    
    def display_nutrition_chart(self, nutrition_info):
        """顯示營養圖表"""
        if not nutrition_info:
            return
        
        # 準備資料
        nutrients = ['蛋白質', '碳水化合物', '脂肪', '纖維']
        values = [
            nutrition_info.get('protein', 0),
            nutrition_info.get('carbohydrates', 0),
            nutrition_info.get('fat', 0),
            nutrition_info.get('fiber', 0)
        ]
        
        # 創建雷達圖
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=nutrients,
            fill='toself',
            name='營養成分',
            line_color='#1f77b4'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )),
            showlegend=False,
            title="營養成分分析"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_health_score(self, score):
        """顯示健康評分"""
        if score is None:
            return
        
        # 根據分數決定顏色和等級
        if score >= 80:
            color = "#27ae60"
            grade = "優秀"
            emoji = "🏆"
        elif score >= 60:
            color = "#f39c12"
            grade = "良好"
            emoji = "👍"
        elif score >= 40:
            color = "#e67e22"
            grade = "一般"
            emoji = "😐"
        else:
            color = "#e74c3c"
            grade = "需改善"
            emoji = "⚠️"
        
        # 創建圓形圖表
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            values=[score, 100-score],
            hole=0.7,
            marker_colors=[color, '#f0f0f0'],
            showlegend=False,
            textinfo='none'
        ))
        
        fig.add_annotation(
            text=f"{emoji}<br>{score}<br>{grade}",
            x=0.5, y=0.5,
            xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=16, color=color)
        )
        
        fig.update_layout(
            title="健康評分",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """運行應用程式"""
        # 主標題
        st.markdown('<h1 class="main-header">🍽️ WebEye 食物偵測系統</h1>', unsafe_allow_html=True)
        st.markdown("### 使用 WebEye 硬體進行智慧食物分析和營養評估")
        
        # 側邊欄設定
        with st.sidebar:
            st.header("⚙️ 系統設定")
            
            # 相機設定
            st.subheader("📷 相機設定")
            resolution = st.selectbox(
                "解析度",
                ["640x480", "1280x720", "1920x1080"],
                index=1
            )
            
            fps = st.selectbox(
                "FPS",
                [15, 30, 60],
                index=1
            )
            
            # 相機控制
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎥 開始串流", type="primary"):
                    if self.setup_camera(resolution, fps):
                        st.success("相機已初始化")
                        st.session_state.camera_ready = True
                    else:
                        st.error("相機初始化失敗")
            
            with col2:
                if st.button("⏹️ 停止串流"):
                    if self.camera_controller:
                        self.camera_controller.release_all()
                    st.session_state.camera_ready = False
                    st.info("串流已停止")
            
            # 相機狀態
            if 'camera_ready' in st.session_state and st.session_state.camera_ready:
                st.markdown('<div class="camera-status status-online">📹 相機已連接</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="camera-status status-offline">📹 相機未連接</div>', unsafe_allow_html=True)
            
            # 偵測設定
            st.subheader("🔍 偵測設定")
            detection_interval = st.slider(
                "偵測間隔 (秒)",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                step=0.5
            )
            
            confidence_threshold = st.slider(
                "信心度閾值",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )
            
            # 檔案上傳
            st.subheader("📁 檔案操作")
            uploaded_file = st.file_uploader(
                "上傳影像檔案",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp']
            )
            
            if uploaded_file is not None:
                # 處理上傳的檔案
                image = Image.open(uploaded_file)
                frame = np.array(image)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                self.current_frame = frame
                st.session_state.uploaded_image = True
        
        # 主要內容區域
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📹 即時影像")
            
            # 影像顯示區域
            image_placeholder = st.empty()
            
            # 相機串流或上傳影像顯示
            if 'camera_ready' in st.session_state and st.session_state.camera_ready:
                # 相機串流模式
                if st.button("📸 拍照並偵測"):
                    frame = self.capture_frame()
                    if frame is not None:
                        self.current_frame = frame
                        
                        # 執行偵測
                        result = self.detect_food(frame)
                        if result and result.success:
                            self.detection_results.append(result)
                            st.session_state.last_result = result
                
                # 顯示當前影像
                if self.current_frame is not None:
                    # 轉換為RGB並顯示
                    frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                    image_placeholder.image(frame_rgb, caption="當前影像", use_column_width=True)
            
            elif 'uploaded_image' in st.session_state and st.session_state.uploaded_image:
                # 上傳影像模式
                if self.current_frame is not None:
                    frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                    image_placeholder.image(frame_rgb, caption="上傳的影像", use_column_width=True)
                    
                    # 自動執行偵測
                    if st.button("🔍 分析影像"):
                        result = self.detect_food(self.current_frame)
                        if result and result.success:
                            self.detection_results.append(result)
                            st.session_state.last_result = result
            
            else:
                image_placeholder.info("請連接相機或上傳影像檔案")
        
        with col2:
            st.header("📊 偵測結果")
            
            # 顯示最新的偵測結果
            if 'last_result' in st.session_state and st.session_state.last_result:
                result = st.session_state.last_result
                
                # 食物列表
                st.subheader("🍽️ 檢測到的食物")
                if result.foods_detected:
                    for food in result.foods_detected:
                        st.markdown(f'<div class="food-card">🍽️ {food}</div>', unsafe_allow_html=True)
                else:
                    st.info("未檢測到食物")
                
                # 營養資訊
                st.subheader("🥗 營養資訊")
                nutrition = result.nutrition_info
                if nutrition:
                    col_n1, col_n2 = st.columns(2)
                    
                    with col_n1:
                        st.metric("卡路里", f"{nutrition.get('total_calories', 0)} kcal")
                        st.metric("蛋白質", f"{nutrition.get('protein', 0):.1f} g")
                    
                    with col_n2:
                        st.metric("碳水化合物", f"{nutrition.get('carbohydrates', 0):.1f} g")
                        st.metric("脂肪", f"{nutrition.get('fat', 0):.1f} g")
                    
                    # 維生素資訊
                    vitamins = nutrition.get('vitamins', [])
                    if vitamins:
                        st.write(f"**維生素:** {', '.join(vitamins)}")
                
                # 健康評分
                st.subheader("🏥 健康評分")
                self.display_health_score(result.health_score)
                
                # 建議
                st.subheader("💡 飲食建議")
                if result.recommendations:
                    for i, rec in enumerate(result.recommendations, 1):
                        st.markdown(f'<div class="recommendation-card">{i}. {rec}</div>', unsafe_allow_html=True)
        
        # 底部圖表區域
        if 'last_result' in st.session_state and st.session_state.last_result:
            result = st.session_state.last_result
            
            st.header("📈 詳細分析")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                self.display_nutrition_chart(result.nutrition_info)
            
            with col_chart2:
                # 食物分布圖
                if result.foods_detected:
                    food_counts = {}
                    for food in result.foods_detected:
                        food_counts[food] = food_counts.get(food, 0) + 1
                    
                    fig = px.pie(
                        values=list(food_counts.values()),
                        names=list(food_counts.keys()),
                        title="食物分布"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # 歷史記錄
        if self.detection_results:
            st.header("📋 偵測歷史")
            
            # 創建歷史資料表格
            history_data = []
            for i, result in enumerate(self.detection_results[-10:], 1):  # 顯示最近10次
                history_data.append({
                    "序號": i,
                    "時間": result.timestamp.strftime("%H:%M:%S"),
                    "食物數量": len(result.foods_detected),
                    "健康評分": result.health_score,
                    "卡路里": result.nutrition_info.get('total_calories', 0)
                })
            
            if history_data:
                st.dataframe(history_data, use_container_width=True)
                
                # 下載按鈕
                if st.button("💾 下載結果"):
                    # 準備下載資料
                    download_data = {
                        'timestamp': datetime.now().isoformat(),
                        'results': []
                    }
                    
                    for result in self.detection_results:
                        result_data = {
                            'timestamp': result.timestamp.isoformat(),
                            'foods_detected': result.foods_detected,
                            'description': result.description,
                            'nutrition_info': result.nutrition_info,
                            'health_score': result.health_score,
                            'recommendations': result.recommendations
                        }
                        download_data['results'].append(result_data)
                    
                    # 轉換為JSON
                    json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
                    
                    # 提供下載
                    st.download_button(
                        label="📥 下載JSON檔案",
                        data=json_str,
                        file_name=f"webeye_food_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

def main():
    """主函數"""
    # 初始化應用程式
    app = WebEyeStreamlitApp()
    
    # 運行應用程式
    app.run()

if __name__ == "__main__":
    main() 