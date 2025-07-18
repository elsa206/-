#!/usr/bin/env python3
"""
WebEye 硬體控制模組
專門用於控制 WebEye 硬體進行影像捕獲和處理
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Callable, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraMode(Enum):
    """相機模式"""
    PHOTO = "photo"
    VIDEO = "video"
    STREAM = "stream"

@dataclass
class CameraSettings:
    """相機設定"""
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    brightness: int = 50
    contrast: int = 50
    saturation: int = 50
    exposure: float = -1.0
    auto_focus: bool = True

class WebEyeCamera:
    """WebEye 硬體控制類別"""
    
    def __init__(self, camera_index: int = 0, settings: Optional[CameraSettings] = None):
        """
        初始化 WebEye 相機
        
        Args:
            camera_index: 相機索引 (通常是 0)
            settings: 相機設定
        """
        self.camera_index = camera_index
        self.settings = settings or CameraSettings()
        self.cap = None
        self.is_running = False
        self.is_recording = False
        self.current_mode = CameraMode.STREAM
        self.frame_callback = None
        self.recording_thread = None
        self.stream_thread = None
        
        # 初始化相機
        self._initialize_camera()
    
    def _initialize_camera(self):
        """初始化相機硬體"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"無法開啟相機 {self.camera_index}")
            
            # 設定相機參數
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.settings.fps)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.brightness / 100.0)
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.settings.contrast / 100.0)
            self.cap.set(cv2.CAP_PROP_SATURATION, self.settings.saturation / 100.0)
            
            if self.settings.exposure > 0:
                self.cap.set(cv2.CAP_PROP_EXPOSURE, self.settings.exposure)
            
            if self.settings.auto_focus:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            
            logger.info(f"WebEye 相機初始化成功: {self.settings.resolution[0]}x{self.settings.resolution[1]} @ {self.settings.fps}fps")
            
        except Exception as e:
            logger.error(f"相機初始化失敗: {e}")
            raise
    
    def capture_photo(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        拍攝照片
        
        Args:
            save_path: 儲存路徑 (可選)
            
        Returns:
            影像陣列或 None
        """
        if not self.cap or not self.cap.isOpened():
            logger.error("相機未初始化")
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("無法捕獲影像")
                return None
            
            # 影像預處理
            frame = self._preprocess_frame(frame)
            
            # 儲存影像
            if save_path:
                cv2.imwrite(save_path, frame)
                logger.info(f"照片已儲存: {save_path}")
            
            return frame
            
        except Exception as e:
            logger.error(f"拍攝照片失敗: {e}")
            return None
    
    def start_stream(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        """
        開始串流
        
        Args:
            callback: 影像回調函數
        """
        if self.is_running:
            logger.warning("串流已在運行中")
            return
        
        self.frame_callback = callback
        self.is_running = True
        self.current_mode = CameraMode.STREAM
        
        self.stream_thread = threading.Thread(target=self._stream_worker)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        
        logger.info("串流已開始")
    
    def stop_stream(self):
        """停止串流"""
        self.is_running = False
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)
        logger.info("串流已停止")
    
    def start_recording(self, output_path: str):
        """
        開始錄影
        
        Args:
            output_path: 輸出檔案路徑
        """
        if self.is_recording:
            logger.warning("錄影已在進行中")
            return
        
        self.is_recording = True
        self.current_mode = CameraMode.VIDEO
        
        self.recording_thread = threading.Thread(
            target=self._recording_worker, 
            args=(output_path,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        logger.info(f"錄影已開始: {output_path}")
    
    def stop_recording(self):
        """停止錄影"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        logger.info("錄影已停止")
    
    def _stream_worker(self):
        """串流工作執行緒"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("串流影像捕獲失敗")
                    break
                
                # 影像預處理
                frame = self._preprocess_frame(frame)
                
                # 執行回調
                if self.frame_callback:
                    self.frame_callback(frame)
                
                # 控制幀率
                time.sleep(1.0 / self.settings.fps)
                
            except Exception as e:
                logger.error(f"串流處理錯誤: {e}")
                break
    
    def _recording_worker(self, output_path: str):
        """錄影工作執行緒"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path, 
            fourcc, 
            self.settings.fps, 
            self.settings.resolution
        )
        
        try:
            while self.is_recording:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = self._preprocess_frame(frame)
                out.write(frame)
                
                time.sleep(1.0 / self.settings.fps)
                
        except Exception as e:
            logger.error(f"錄影處理錯誤: {e}")
        finally:
            out.release()
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        影像預處理
        
        Args:
            frame: 原始影像
            
        Returns:
            處理後的影像
        """
        # 調整大小
        if frame.shape[:2] != self.settings.resolution[::-1]:
            frame = cv2.resize(frame, self.settings.resolution)
        
        # 色彩空間轉換 (BGR to RGB)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame
    
    def set_camera_settings(self, settings: CameraSettings):
        """
        更新相機設定
        
        Args:
            settings: 新的相機設定
        """
        self.settings = settings
        
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, settings.fps)
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, settings.brightness / 100.0)
            self.cap.set(cv2.CAP_PROP_CONTRAST, settings.contrast / 100.0)
            self.cap.set(cv2.CAP_PROP_SATURATION, settings.saturation / 100.0)
            
            if settings.exposure > 0:
                self.cap.set(cv2.CAP_PROP_EXPOSURE, settings.exposure)
            
            if settings.auto_focus:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        logger.info("相機設定已更新")
    
    def get_camera_info(self) -> dict:
        """
        獲取相機資訊
        
        Returns:
            相機資訊字典
        """
        if not self.cap or not self.cap.isOpened():
            return {"error": "相機未初始化"}
        
        info = {
            "camera_index": self.camera_index,
            "resolution": (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS) * 100,
            "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST) * 100,
            "saturation": self.cap.get(cv2.CAP_PROP_SATURATION) * 100,
            "exposure": self.cap.get(cv2.CAP_PROP_EXPOSURE),
            "is_running": self.is_running,
            "is_recording": self.is_recording,
            "current_mode": self.current_mode.value
        }
        
        return info
    
    def release(self):
        """釋放相機資源"""
        self.stop_stream()
        self.stop_recording()
        
        if self.cap:
            self.cap.release()
        
        logger.info("相機資源已釋放")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

class WebEyeController:
    """WebEye 硬體控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.cameras = {}
        self.active_camera = None
    
    def add_camera(self, camera_id: str, camera_index: int = 0, settings: Optional[CameraSettings] = None):
        """
        添加相機
        
        Args:
            camera_id: 相機ID
            camera_index: 相機索引
            settings: 相機設定
        """
        try:
            camera = WebEyeCamera(camera_index, settings)
            self.cameras[camera_id] = camera
            logger.info(f"相機 {camera_id} 已添加")
        except Exception as e:
            logger.error(f"添加相機失敗: {e}")
    
    def get_camera(self, camera_id: str) -> Optional[WebEyeCamera]:
        """獲取相機"""
        return self.cameras.get(camera_id)
    
    def set_active_camera(self, camera_id: str):
        """設定活動相機"""
        if camera_id in self.cameras:
            self.active_camera = camera_id
            logger.info(f"活動相機已設定為: {camera_id}")
        else:
            logger.error(f"相機 {camera_id} 不存在")
    
    def capture_photo(self, camera_id: Optional[str] = None, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """拍攝照片"""
        camera_id = camera_id or self.active_camera
        if not camera_id or camera_id not in self.cameras:
            logger.error("未指定有效的相機")
            return None
        
        return self.cameras[camera_id].capture_photo(save_path)
    
    def start_stream(self, camera_id: Optional[str] = None, callback: Optional[Callable] = None):
        """開始串流"""
        camera_id = camera_id or self.active_camera
        if not camera_id or camera_id not in self.cameras:
            logger.error("未指定有效的相機")
            return
        
        self.cameras[camera_id].start_stream(callback)
    
    def stop_stream(self, camera_id: Optional[str] = None):
        """停止串流"""
        camera_id = camera_id or self.active_camera
        if camera_id and camera_id in self.cameras:
            self.cameras[camera_id].stop_stream()
    
    def release_all(self):
        """釋放所有相機資源"""
        for camera in self.cameras.values():
            camera.release()
        self.cameras.clear()
        self.active_camera = None
        logger.info("所有相機資源已釋放")

# 測試函數
def test_webeye_camera():
    """測試 WebEye 相機功能"""
    print("🧪 測試 WebEye 相機功能...")
    
    try:
        # 創建相機設定
        settings = CameraSettings(
            resolution=(1280, 720),
            fps=30,
            brightness=60,
            contrast=55,
            saturation=50
        )
        
        # 初始化相機
        with WebEyeCamera(settings=settings) as camera:
            print("✅ 相機初始化成功")
            
            # 獲取相機資訊
            info = camera.get_camera_info()
            print(f"📷 相機資訊: {info}")
            
            # 拍攝測試照片
            frame = camera.capture_photo("test_photo.jpg")
            if frame is not None:
                print("✅ 照片拍攝成功")
                print(f"📐 影像尺寸: {frame.shape}")
            else:
                print("❌ 照片拍攝失敗")
            
            # 測試串流 (5秒)
            print("🎥 開始測試串流 (5秒)...")
            frame_count = 0
            
            def stream_callback(frame):
                nonlocal frame_count
                frame_count += 1
                if frame_count % 30 == 0:  # 每秒顯示一次
                    print(f"📹 串流幀數: {frame_count}")
            
            camera.start_stream(callback=stream_callback)
            time.sleep(5)
            camera.stop_stream()
            print(f"✅ 串流測試完成，總幀數: {frame_count}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_webeye_camera() 