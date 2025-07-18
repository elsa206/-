#!/usr/bin/env python3
"""
WebEye 食物偵測應用程式
整合 WebEye 硬體控制和食物辨識功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
import threading
import time
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import logging

# 導入自定義模組
from webeye_camera import WebEyeCamera, CameraSettings, WebEyeController
from food_detection import FoodDetector, FoodDetectionResult

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebEyeFoodApp:
    """WebEye 食物偵測應用程式主類別"""
    
    def __init__(self, root):
        """初始化應用程式"""
        self.root = root
        self.root.title("WebEye 食物偵測系統")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化組件
        self.camera_controller = WebEyeController()
        self.food_detector = None
        self.current_frame = None
        self.is_streaming = False
        self.is_detecting = False
        self.detection_results = []
        
        # 設定UI
        self.setup_ui()
        
        # 初始化食物偵測器
        self.init_food_detector()
        
        # 初始化相機
        self.init_camera()
    
    def setup_ui(self):
        """設定使用者界面"""
        # 主標題
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🍽️ WebEye 食物偵測系統", 
            font=('Arial', 20, 'bold'), 
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # 主容器
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 左側控制面板
        self.setup_control_panel(main_container)
        
        # 右側顯示區域
        self.setup_display_panel(main_container)
        
        # 底部狀態欄
        self.setup_status_bar()
    
    def setup_control_panel(self, parent):
        """設定控制面板"""
        control_frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # 相機控制區域
        camera_frame = tk.LabelFrame(control_frame, text="📷 相機控制", font=('Arial', 12, 'bold'))
        camera_frame.pack(fill='x', padx=10, pady=10)
        
        # 相機設定
        tk.Label(camera_frame, text="解析度:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.resolution_var = tk.StringVar(value="1280x720")
        resolution_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.resolution_var,
            values=["640x480", "1280x720", "1920x1080"],
            state="readonly",
            width=15
        )
        resolution_combo.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(camera_frame, text="FPS:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(
            camera_frame, 
            textvariable=self.fps_var,
            values=["15", "30", "60"],
            state="readonly",
            width=15
        )
        fps_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # 相機按鈕
        button_frame = tk.Frame(camera_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_stream_btn = tk.Button(
            button_frame, 
            text="🎥 開始串流", 
            command=self.start_stream,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=12
        )
        self.start_stream_btn.pack(side='left', padx=5)
        
        self.stop_stream_btn = tk.Button(
            button_frame, 
            text="⏹️ 停止串流", 
            command=self.stop_stream,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=12,
            state='disabled'
        )
        self.stop_stream_btn.pack(side='left', padx=5)
        
        # 拍照按鈕
        self.capture_btn = tk.Button(
            camera_frame, 
            text="📸 拍照", 
            command=self.capture_photo,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.capture_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 食物偵測控制區域
        detection_frame = tk.LabelFrame(control_frame, text="🔍 食物偵測", font=('Arial', 12, 'bold'))
        detection_frame.pack(fill='x', padx=10, pady=10)
        
        self.detect_btn = tk.Button(
            detection_frame, 
            text="🔍 開始偵測", 
            command=self.start_detection,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.detect_btn.pack(pady=5)
        
        self.stop_detect_btn = tk.Button(
            detection_frame, 
            text="⏹️ 停止偵測", 
            command=self.stop_detection,
            bg='#e67e22',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15,
            state='disabled'
        )
        self.stop_detect_btn.pack(pady=5)
        
        # 檔案操作區域
        file_frame = tk.LabelFrame(control_frame, text="📁 檔案操作", font=('Arial', 12, 'bold'))
        file_frame.pack(fill='x', padx=10, pady=10)
        
        self.load_image_btn = tk.Button(
            file_frame, 
            text="📂 載入影像", 
            command=self.load_image,
            bg='#34495e',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.load_image_btn.pack(pady=5)
        
        self.save_result_btn = tk.Button(
            file_frame, 
            text="💾 儲存結果", 
            command=self.save_results,
            bg='#16a085',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.save_result_btn.pack(pady=5)
        
        # 設定區域
        settings_frame = tk.LabelFrame(control_frame, text="⚙️ 設定", font=('Arial', 12, 'bold'))
        settings_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(settings_frame, text="偵測間隔 (秒):").pack(anchor='w', padx=5)
        self.detection_interval = tk.StringVar(value="2.0")
        interval_entry = tk.Entry(settings_frame, textvariable=self.detection_interval, width=10)
        interval_entry.pack(pady=2)
        
        # 相機資訊顯示
        info_frame = tk.LabelFrame(control_frame, text="📊 相機資訊", font=('Arial', 12, 'bold'))
        info_frame.pack(fill='x', padx=10, pady=10)
        
        self.camera_info_text = tk.Text(info_frame, height=8, width=25, font=('Courier', 8))
        self.camera_info_text.pack(padx=5, pady=5)
    
    def setup_display_panel(self, parent):
        """設定顯示面板"""
        display_frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        display_frame.pack(side='right', fill='both', expand=True)
        
        # 影像顯示區域
        image_frame = tk.LabelFrame(display_frame, text="📹 即時影像", font=('Arial', 12, 'bold'))
        image_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(image_frame, bg='black', text="等待影像...")
        self.image_label.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 結果顯示區域
        result_frame = tk.LabelFrame(display_frame, text="📋 偵測結果", font=('Arial', 12, 'bold'))
        result_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 創建結果顯示的Notebook
        self.result_notebook = ttk.Notebook(result_frame)
        self.result_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 食物列表頁面
        self.food_frame = tk.Frame(self.result_notebook)
        self.result_notebook.add(self.food_frame, text="🍽️ 食物")
        
        self.food_listbox = tk.Listbox(self.food_frame, font=('Arial', 10))
        self.food_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 營養資訊頁面
        self.nutrition_frame = tk.Frame(self.result_notebook)
        self.result_notebook.add(self.nutrition_frame, text="🥗 營養")
        
        self.nutrition_text = tk.Text(self.nutrition_frame, font=('Arial', 10))
        self.nutrition_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 建議頁面
        self.recommendation_frame = tk.Frame(self.result_notebook)
        self.result_notebook.add(self.recommendation_frame, text="💡 建議")
        
        self.recommendation_text = tk.Text(self.recommendation_frame, font=('Arial', 10))
        self.recommendation_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 健康評分頁面
        self.health_frame = tk.Frame(self.result_notebook)
        self.result_notebook.add(self.health_frame, text="🏥 健康評分")
        
        self.health_score_label = tk.Label(
            self.health_frame, 
            text="等待偵測...", 
            font=('Arial', 24, 'bold'),
            fg='#2c3e50'
        )
        self.health_score_label.pack(expand=True)
    
    def setup_status_bar(self):
        """設定狀態欄"""
        self.status_bar = tk.Label(
            self.root, 
            text="就緒", 
            relief='sunken', 
            anchor='w',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def init_food_detector(self):
        """初始化食物偵測器"""
        try:
            self.food_detector = FoodDetector()
            self.update_status("食物偵測器初始化成功")
        except Exception as e:
            messagebox.showerror("錯誤", f"食物偵測器初始化失敗: {e}")
            self.update_status("食物偵測器初始化失敗")
    
    def init_camera(self):
        """初始化相機"""
        try:
            # 解析解析度設定
            resolution = tuple(map(int, self.resolution_var.get().split('x')))
            fps = int(self.fps_var.get())
            
            settings = CameraSettings(
                resolution=resolution,
                fps=fps,
                brightness=60,
                contrast=55,
                saturation=50
            )
            
            self.camera_controller.add_camera("main", 0, settings)
            self.camera_controller.set_active_camera("main")
            
            self.update_camera_info()
            self.update_status("相機初始化成功")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"相機初始化失敗: {e}")
            self.update_status("相機初始化失敗")
    
    def start_stream(self):
        """開始串流"""
        if self.is_streaming:
            return
        
        try:
            self.camera_controller.start_stream(callback=self.on_frame_received)
            self.is_streaming = True
            
            self.start_stream_btn.config(state='disabled')
            self.stop_stream_btn.config(state='normal')
            
            self.update_status("串流已開始")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"開始串流失敗: {e}")
            self.update_status("串流啟動失敗")
    
    def stop_stream(self):
        """停止串流"""
        if not self.is_streaming:
            return
        
        try:
            self.camera_controller.stop_stream()
            self.is_streaming = False
            
            self.start_stream_btn.config(state='normal')
            self.stop_stream_btn.config(state='disabled')
            
            self.update_status("串流已停止")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"停止串流失敗: {e}")
    
    def on_frame_received(self, frame):
        """接收到影像幀的回調函數"""
        self.current_frame = frame
        
        # 更新影像顯示
        self.update_image_display(frame)
        
        # 如果正在偵測，執行食物偵測
        if self.is_detecting:
            self.perform_detection(frame)
    
    def update_image_display(self, frame):
        """更新影像顯示"""
        try:
            # 調整影像大小
            height, width = frame.shape[:2]
            max_size = 400
            
            if width > max_size or height > max_size:
                scale = min(max_size / width, max_size / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # 轉換為PIL影像
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            pil_image = Image.fromarray(frame_rgb)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # 更新標籤
            self.image_label.configure(image=tk_image, text="")
            self.image_label.image = tk_image  # 保持參考
            
        except Exception as e:
            logger.error(f"更新影像顯示失敗: {e}")
    
    def capture_photo(self):
        """拍照"""
        if self.current_frame is None:
            messagebox.showwarning("警告", "沒有可用的影像")
            return
        
        try:
            # 生成檔案名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"webeye_photo_{timestamp}.jpg"
            
            # 儲存照片
            cv2.imwrite(filename, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))
            
            messagebox.showinfo("成功", f"照片已儲存: {filename}")
            self.update_status(f"照片已儲存: {filename}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"拍照失敗: {e}")
    
    def start_detection(self):
        """開始食物偵測"""
        if not self.food_detector:
            messagebox.showerror("錯誤", "食物偵測器未初始化")
            return
        
        if not self.is_streaming:
            messagebox.showwarning("警告", "請先開始串流")
            return
        
        self.is_detecting = True
        self.detect_btn.config(state='disabled')
        self.stop_detect_btn.config(state='normal')
        
        self.update_status("食物偵測已開始")
    
    def stop_detection(self):
        """停止食物偵測"""
        self.is_detecting = False
        self.detect_btn.config(state='normal')
        self.stop_detect_btn.config(state='disabled')
        
        self.update_status("食物偵測已停止")
    
    def perform_detection(self, frame):
        """執行食物偵測"""
        try:
            # 執行偵測
            result = self.food_detector.detect_food_from_frame(frame)
            
            if result.success:
                # 儲存結果
                self.detection_results.append(result)
                
                # 更新顯示
                self.update_detection_display(result)
                
                # 更新狀態
                self.update_status(f"偵測完成: {len(result.foods_detected)} 種食物")
            
        except Exception as e:
            logger.error(f"食物偵測失敗: {e}")
    
    def update_detection_display(self, result: FoodDetectionResult):
        """更新偵測結果顯示"""
        # 更新食物列表
        self.food_listbox.delete(0, tk.END)
        for food in result.foods_detected:
            self.food_listbox.insert(tk.END, f"🍽️ {food}")
        
        # 更新營養資訊
        self.nutrition_text.delete(1.0, tk.END)
        nutrition = result.nutrition_info
        nutrition_text = f"""營養資訊:
        
卡路里: {nutrition.get('total_calories', 0)} kcal
蛋白質: {nutrition.get('protein', 0):.1f} g
碳水化合物: {nutrition.get('carbohydrates', 0):.1f} g
脂肪: {nutrition.get('fat', 0):.1f} g
纖維: {nutrition.get('fiber', 0):.1f} g
維生素: {', '.join(nutrition.get('vitamins', []))}
        """
        self.nutrition_text.insert(1.0, nutrition_text)
        
        # 更新建議
        self.recommendation_text.delete(1.0, tk.END)
        for i, rec in enumerate(result.recommendations, 1):
            self.recommendation_text.insert(tk.END, f"{i}. {rec}\n")
        
        # 更新健康評分
        score = result.health_score
        if score >= 80:
            color = '#27ae60'  # 綠色
            grade = "優秀"
        elif score >= 60:
            color = '#f39c12'  # 橙色
            grade = "良好"
        elif score >= 40:
            color = '#e67e22'  # 深橙色
            grade = "一般"
        else:
            color = '#e74c3c'  # 紅色
            grade = "需改善"
        
        self.health_score_label.config(
            text=f"{score}\n{grade}",
            fg=color
        )
    
    def load_image(self):
        """載入影像檔案"""
        filename = filedialog.askopenfilename(
            title="選擇影像檔案",
            filetypes=[
                ("影像檔案", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有檔案", "*.*")
            ]
        )
        
        if filename:
            try:
                # 讀取影像
                frame = cv2.imread(filename)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                self.current_frame = frame
                self.update_image_display(frame)
                
                # 自動執行偵測
                if self.food_detector:
                    result = self.food_detector.detect_food_from_frame(frame)
                    if result.success:
                        self.detection_results.append(result)
                        self.update_detection_display(result)
                        self.update_status(f"影像載入成功，偵測到 {len(result.foods_detected)} 種食物")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"載入影像失敗: {e}")
    
    def save_results(self):
        """儲存偵測結果"""
        if not self.detection_results:
            messagebox.showwarning("警告", "沒有可儲存的結果")
            return
        
        filename = filedialog.asksaveasfilename(
            title="儲存結果",
            defaultextension=".json",
            filetypes=[("JSON檔案", "*.json"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                # 準備儲存資料
                save_data = {
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
                    save_data['results'].append(result_data)
                
                # 儲存檔案
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"結果已儲存: {filename}")
                self.update_status(f"結果已儲存: {filename}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存結果失敗: {e}")
    
    def update_camera_info(self):
        """更新相機資訊"""
        try:
            camera = self.camera_controller.get_camera("main")
            if camera:
                info = camera.get_camera_info()
                
                info_text = f"""相機索引: {info.get('camera_index', 'N/A')}
解析度: {info.get('resolution', 'N/A')}
FPS: {info.get('fps', 'N/A'):.1f}
亮度: {info.get('brightness', 'N/A'):.1f}
對比度: {info.get('contrast', 'N/A'):.1f}
飽和度: {info.get('saturation', 'N/A'):.1f}
運行狀態: {'是' if info.get('is_running', False) else '否'}
錄影狀態: {'是' if info.get('is_recording', False) else '否'}
                """
                
                self.camera_info_text.delete(1.0, tk.END)
                self.camera_info_text.insert(1.0, info_text)
                
        except Exception as e:
            logger.error(f"更新相機資訊失敗: {e}")
    
    def update_status(self, message: str):
        """更新狀態欄"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def on_closing(self):
        """應用程式關閉時的清理工作"""
        try:
            self.stop_detection()
            self.stop_stream()
            self.camera_controller.release_all()
        except:
            pass
        self.root.destroy()

def main():
    """主函數"""
    root = tk.Tk()
    app = WebEyeFoodApp(root)
    
    # 設定關閉事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 啟動應用程式
    root.mainloop()

if __name__ == "__main__":
    main() 