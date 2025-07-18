# 🍽️ WebEye 食物偵測系統

一個專為 WebEye 硬體設計的智慧食物偵測和營養分析系統，整合 Azure Computer Vision API 進行高精度的食物識別。

## 🌟 功能特色

### 📷 硬體控制
- **WebEye 相機整合**: 專為 WebEye 硬體優化的相機控制
- **即時串流**: 支援高品質即時影像串流
- **多解析度支援**: 640x480, 1280x720, 1920x1080
- **可調參數**: 亮度、對比度、飽和度、曝光度

### 🔍 食物偵測
- **Azure AI 整合**: 使用 Azure Computer Vision API 進行精確識別
- **多語言支援**: 支援中文和英文食物識別
- **即時分析**: 快速的食物種類識別和分類
- **信心度評估**: 提供每個識別結果的信心分數

### 🥗 營養分析
- **營養資料庫**: 包含 50+ 種常見食物的詳細營養資訊
- **熱量計算**: 自動計算總卡路里
- **營養素分析**: 蛋白質、碳水化合物、脂肪、纖維
- **維生素識別**: 自動識別食物中的維生素種類

### 🏥 健康評估
- **健康評分系統**: 0-100 分的綜合健康評分
- **飲食建議**: 根據檢測結果提供個性化建議
- **營養均衡分析**: 評估飲食的營養均衡性
- **改善建議**: 針對不足的營養素提供改善建議

### 📊 資料視覺化
- **互動式圖表**: 使用 Plotly 創建美觀的資料視覺化
- **營養雷達圖**: 營養成分的雷達圖分析
- **健康評分圓餅圖**: 直觀的健康評分顯示
- **食物分布圖**: 檢測到的食物種類分布

## 🚀 快速開始

### 1. 環境需求

- Python 3.8+
- WebEye 硬體設備
- Azure Computer Vision API 金鑰
- 網路連接

### 2. 安裝依賴

```bash
# 克隆專案
git clone <repository-url>
cd 黑客松-子賽事1

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 3. 環境設定

```bash
# 複製環境變數範例檔案
cp env.example .env

# 編輯 .env 檔案，填入您的 Azure API 金鑰
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_VISION_KEY=your-azure-vision-key-here
```

### 4. 運行應用程式

#### 桌面應用程式 (Tkinter)
```bash
python webeye_food_app.py
```

#### Web 應用程式 (Streamlit)
```bash
streamlit run streamlit_app.py
```

## 📁 專案結構

```
黑客松-子賽事1/
├── webeye_camera.py          # WebEye 硬體控制模組
├── food_detection.py         # 食物偵測和營養分析模組
├── webeye_food_app.py        # Tkinter 桌面應用程式
├── streamlit_app.py          # Streamlit Web 應用程式
├── requirements.txt          # Python 依賴套件
├── env.example              # 環境變數範例
├── README.md                # 專案說明文件
└── test_webeye_camera.py    # 相機功能測試
```

## 🔧 核心模組說明

### WebEye 相機控制 (`webeye_camera.py`)

提供完整的 WebEye 硬體控制功能：

```python
from webeye_camera import WebEyeCamera, CameraSettings

# 創建相機設定
settings = CameraSettings(
    resolution=(1280, 720),
    fps=30,
    brightness=60,
    contrast=55,
    saturation=50
)

# 初始化相機
camera = WebEyeCamera(settings=settings)

# 拍照
frame = camera.capture_photo("photo.jpg")

# 開始串流
camera.start_stream(callback=process_frame)
```

### 食物偵測器 (`food_detection.py`)

整合 Azure AI 服務進行食物識別：

```python
from food_detection import FoodDetector

# 初始化偵測器
detector = FoodDetector()

# 偵測食物
result = detector.detect_food_from_frame(frame)

# 獲取結果
print(f"檢測到食物: {result.foods_detected}")
print(f"健康評分: {result.health_score}")
print(f"營養資訊: {result.nutrition_info}")
```

## 🎯 使用指南

### 基本操作流程

1. **連接硬體**: 確保 WebEye 設備正確連接
2. **啟動應用程式**: 選擇桌面版或 Web 版應用程式
3. **設定相機**: 調整解析度、FPS 等參數
4. **開始串流**: 啟動相機串流功能
5. **執行偵測**: 點擊偵測按鈕進行食物分析
6. **查看結果**: 檢視食物列表、營養資訊和健康評分
7. **儲存結果**: 將分析結果儲存為 JSON 檔案

### 進階功能

#### 批量處理
```python
# 批量處理多張影像
for image_path in image_files:
    result = detector.detect_food_from_file(image_path)
    results.append(result)
```

#### 自定義營養資料庫
```python
# 添加自定義食物營養資訊
detector.nutrition_db['custom_food'] = {
    'calories': 150,
    'protein': 10,
    'carbs': 20,
    'fat': 5,
    'fiber': 3,
    'vitamins': ['C', 'B6']
}
```

#### 健康評分自定義
```python
# 自定義健康評分算法
def custom_health_score(nutrition_info):
    # 實現自定義評分邏輯
    pass
```

## 📊 API 參考

### FoodDetector 類別

#### 方法

- `detect_food_from_frame(frame)`: 從影像幀偵測食物
- `detect_food_from_file(image_path)`: 從檔案偵測食物
- `get_detailed_analysis(frame)`: 獲取詳細分析報告

#### 屬性

- `food_keywords`: 食物關鍵字列表
- `nutrition_db`: 營養資料庫

### WebEyeCamera 類別

#### 方法

- `capture_photo(save_path)`: 拍照
- `start_stream(callback)`: 開始串流
- `stop_stream()`: 停止串流
- `get_camera_info()`: 獲取相機資訊

#### 屬性

- `settings`: 相機設定
- `is_running`: 運行狀態

## 🛠️ 故障排除

### 常見問題

#### 1. 相機無法初始化
```
錯誤: 無法開啟相機
解決方案: 
- 檢查 WebEye 設備連接
- 確認相機驅動程式已安裝
- 嘗試不同的相機索引 (0, 1, 2...)
```

#### 2. Azure API 錯誤
```
錯誤: API 請求失敗
解決方案:
- 檢查 API 金鑰是否正確
- 確認網路連接正常
- 驗證 Azure 服務配額
```

#### 3. 依賴套件安裝失敗
```
錯誤: 套件安裝失敗
解決方案:
- 更新 pip: pip install --upgrade pip
- 使用虛擬環境
- 檢查 Python 版本相容性
```

### 效能優化

1. **降低解析度**: 使用較低解析度可提升處理速度
2. **調整 FPS**: 降低 FPS 可減少 CPU 使用率
3. **批次處理**: 批量處理多張影像可提升效率
4. **快取結果**: 快取已處理的結果避免重複計算

## 🔒 安全性考量

- **API 金鑰保護**: 不要將 API 金鑰提交到版本控制系統
- **資料隱私**: 本地處理影像資料，不上傳到外部服務
- **網路安全**: 使用 HTTPS 連接 Azure 服務
- **存取控制**: 限制應用程式的檔案存取權限

## 📈 效能基準

| 功能 | 處理時間 | 記憶體使用 |
|------|----------|------------|
| 影像捕獲 | < 100ms | 低 |
| 食物偵測 | 1-3s | 中等 |
| 營養分析 | < 100ms | 低 |
| 健康評分 | < 50ms | 低 |

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交變更
4. 發起 Pull Request

## 📄 授權

本專案採用 MIT 授權條款。

## 📞 支援

如有問題或建議，請：

- 提交 Issue
- 發送 Email
- 查看文件

## 🔄 更新日誌

### v1.0.0 (2024-01-01)
- 初始版本發布
- 基本食物偵測功能
- WebEye 硬體整合
- Azure AI 服務整合

### v1.1.0 (計劃中)
- 新增更多食物種類
- 改進營養分析算法
- 新增語音提示功能
- 支援多語言界面

---

**🍽️ 讓 WebEye 成為您的智慧營養師！** 