#!/usr/bin/env python3
"""
WebEye 相機功能測試
用於驗證 WebEye 硬體控制功能
"""

import cv2
import numpy as np
import time
import os
from datetime import datetime

# 導入自定義模組
from webeye_camera import WebEyeCamera, CameraSettings, WebEyeController

def test_camera_initialization():
    """測試相機初始化"""
    print("🧪 測試相機初始化...")
    
    try:
        # 測試不同的相機索引
        for camera_index in range(3):
            print(f"  嘗試相機索引: {camera_index}")
            
            try:
                settings = CameraSettings(
                    resolution=(640, 480),
                    fps=30,
                    brightness=50,
                    contrast=50,
                    saturation=50
                )
                
                camera = WebEyeCamera(camera_index, settings)
                print(f"  ✅ 相機 {camera_index} 初始化成功")
                
                # 獲取相機資訊
                info = camera.get_camera_info()
                print(f"  📊 相機資訊: {info}")
                
                # 釋放相機
                camera.release()
                break
                
            except Exception as e:
                print(f"  ❌ 相機 {camera_index} 初始化失敗: {e}")
                continue
        
        print("✅ 相機初始化測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 相機初始化測試失敗: {e}")
        return False

def test_photo_capture():
    """測試拍照功能"""
    print("🧪 測試拍照功能...")
    
    try:
        settings = CameraSettings(
            resolution=(1280, 720),
            fps=30,
            brightness=60,
            contrast=55,
            saturation=50
        )
        
        with WebEyeCamera(settings=settings) as camera:
            print("  📸 拍攝測試照片...")
            
            # 拍攝照片
            frame = camera.capture_photo("test_photo.jpg")
            
            if frame is not None:
                print(f"  ✅ 照片拍攝成功，尺寸: {frame.shape}")
                
                # 檢查檔案是否存在
                if os.path.exists("test_photo.jpg"):
                    file_size = os.path.getsize("test_photo.jpg")
                    print(f"  📁 檔案已儲存，大小: {file_size} bytes")
                else:
                    print("  ⚠️ 檔案未儲存")
                
                return True
            else:
                print("  ❌ 照片拍攝失敗")
                return False
                
    except Exception as e:
        print(f"❌ 拍照測試失敗: {e}")
        return False

def test_stream_functionality():
    """測試串流功能"""
    print("🧪 測試串流功能...")
    
    try:
        settings = CameraSettings(
            resolution=(640, 480),
            fps=15,
            brightness=50,
            contrast=50,
            saturation=50
        )
        
        with WebEyeCamera(settings=settings) as camera:
            print("  🎥 開始串流測試 (5秒)...")
            
            frame_count = 0
            start_time = time.time()
            
            def stream_callback(frame):
                nonlocal frame_count
                frame_count += 1
                
                # 每秒顯示一次進度
                if frame_count % 15 == 0:
                    elapsed = time.time() - start_time
                    print(f"  📹 已接收 {frame_count} 幀，耗時 {elapsed:.1f} 秒")
            
            # 開始串流
            camera.start_stream(callback=stream_callback)
            
            # 等待5秒
            time.sleep(5)
            
            # 停止串流
            camera.stop_stream()
            
            elapsed_time = time.time() - start_time
            fps_actual = frame_count / elapsed_time if elapsed_time > 0 else 0
            
            print(f"  ✅ 串流測試完成")
            print(f"  📊 總幀數: {frame_count}")
            print(f"  ⏱️ 總時間: {elapsed_time:.1f} 秒")
            print(f"  🎯 實際 FPS: {fps_actual:.1f}")
            
            return True
            
    except Exception as e:
        print(f"❌ 串流測試失敗: {e}")
        return False

def test_camera_settings():
    """測試相機設定"""
    print("🧪 測試相機設定...")
    
    try:
        settings = CameraSettings(
            resolution=(1280, 720),
            fps=30,
            brightness=70,
            contrast=60,
            saturation=55
        )
        
        with WebEyeCamera(settings=settings) as camera:
            print("  ⚙️ 測試相機設定...")
            
            # 獲取初始設定
            initial_info = camera.get_camera_info()
            print(f"  📊 初始設定: {initial_info}")
            
            # 測試新設定
            new_settings = CameraSettings(
                resolution=(640, 480),
                fps=15,
                brightness=40,
                contrast=45,
                saturation=40
            )
            
            camera.set_camera_settings(new_settings)
            
            # 獲取新設定
            new_info = camera.get_camera_info()
            print(f"  📊 新設定: {new_info}")
            
            print("  ✅ 相機設定測試完成")
            return True
            
    except Exception as e:
        print(f"❌ 相機設定測試失敗: {e}")
        return False

def test_camera_controller():
    """測試相機控制器"""
    print("🧪 測試相機控制器...")
    
    try:
        controller = WebEyeController()
        
        # 添加相機
        settings = CameraSettings(
            resolution=(640, 480),
            fps=30
        )
        
        controller.add_camera("test_camera", 0, settings)
        print("  ✅ 相機添加成功")
        
        # 設定活動相機
        controller.set_active_camera("test_camera")
        print("  ✅ 活動相機設定成功")
        
        # 測試拍照
        frame = controller.capture_photo()
        if frame is not None:
            print(f"  ✅ 控制器拍照成功，尺寸: {frame.shape}")
        else:
            print("  ❌ 控制器拍照失敗")
        
        # 釋放資源
        controller.release_all()
        print("  ✅ 控制器資源釋放成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 相機控制器測試失敗: {e}")
        return False

def test_error_handling():
    """測試錯誤處理"""
    print("🧪 測試錯誤處理...")
    
    try:
        # 測試無效的相機索引
        try:
            camera = WebEyeCamera(999)  # 無效索引
            print("  ❌ 應該拋出異常但沒有")
            return False
        except Exception as e:
            print(f"  ✅ 正確處理無效相機索引: {e}")
        
        # 測試無效的解析度
        try:
            settings = CameraSettings(resolution=(0, 0))
            camera = WebEyeCamera(0, settings)
            print("  ❌ 應該拋出異常但沒有")
            return False
        except Exception as e:
            print(f"  ✅ 正確處理無效解析度: {e}")
        
        print("  ✅ 錯誤處理測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 錯誤處理測試失敗: {e}")
        return False

def test_performance():
    """測試效能"""
    print("🧪 測試效能...")
    
    try:
        settings = CameraSettings(
            resolution=(1280, 720),
            fps=30
        )
        
        with WebEyeCamera(settings=settings) as camera:
            # 測試拍照效能
            start_time = time.time()
            frame = camera.capture_photo()
            photo_time = time.time() - start_time
            
            print(f"  📸 拍照耗時: {photo_time:.3f} 秒")
            
            if frame is not None:
                # 測試影像處理效能
                start_time = time.time()
                
                # 模擬一些影像處理操作
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                
                process_time = time.time() - start_time
                print(f"  🔄 影像處理耗時: {process_time:.3f} 秒")
                
                # 測試記憶體使用
                frame_size = frame.nbytes
                print(f"  💾 影像記憶體使用: {frame_size / 1024 / 1024:.2f} MB")
            
            print("  ✅ 效能測試完成")
            return True
            
    except Exception as e:
        print(f"❌ 效能測試失敗: {e}")
        return False

def run_all_tests():
    """運行所有測試"""
    print("🚀 開始 WebEye 相機功能測試")
    print("=" * 50)
    
    tests = [
        ("相機初始化", test_camera_initialization),
        ("拍照功能", test_photo_capture),
        ("串流功能", test_stream_functionality),
        ("相機設定", test_camera_settings),
        ("相機控制器", test_camera_controller),
        ("錯誤處理", test_error_handling),
        ("效能測試", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試執行失敗: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果摘要
    print("\n" + "=" * 50)
    print("📊 測試結果摘要")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試都通過了！")
    else:
        print("⚠️ 部分測試失敗，請檢查硬體連接和設定")
    
    return passed == total

def cleanup_test_files():
    """清理測試檔案"""
    test_files = ["test_photo.jpg"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 已清理測試檔案: {file}")
            except Exception as e:
                print(f"⚠️ 清理檔案失敗 {file}: {e}")

if __name__ == "__main__":
    try:
        # 運行所有測試
        success = run_all_tests()
        
        # 清理測試檔案
        cleanup_test_files()
        
        # 退出碼
        exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️ 測試被使用者中斷")
        cleanup_test_files()
        exit(1)
    except Exception as e:
        print(f"\n💥 測試執行時發生未預期錯誤: {e}")
        cleanup_test_files()
        exit(1) 