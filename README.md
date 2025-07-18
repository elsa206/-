# 🍽️ Azure AI 食物影像辨識

使用 Azure Computer Vision API 進行智慧食物影像辨識和分析的 Python 應用程式。

## ✨ 功能特色

- **🔍 智慧食物辨識**：使用 Azure Computer Vision API 準確識別影像中的食物
- **🥗 營養分析**：自動計算卡路里、蛋白質、碳水化合物等營養資訊
- **🏥 健康評分**：根據營養成分計算健康評分 (0-100分)
- **💡 飲食建議**：提供個人化的飲食改善建議
- **📊 視覺化介面**：提供 Streamlit 網頁介面和命令列工具
- **🌐 多種輸入方式**：支援本機檔案上傳和 URL 影像分析

## 🚀 快速開始

### 1. 環境需求

- Python 3.8 或更高版本
- Azure Computer Vision API 金鑰
- 網路連線

### 2. 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd azure-food-recognition
   ```

2. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定環境變數**
   ```bash
   # 複製範例設定檔
   cp config.env.example .env
   
   # 編輯 .env 檔案，填入您的 Azure API 金鑰
   AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   AZURE_VISION_KEY=your-api-key-here
   ```

### 3. 取得 Azure API 金鑰

1. 登入 [Azure Portal](https://portal.azure.com)
2. 建立或選擇現有的 Computer Vision 資源
3. 在「金鑰和端點」頁面取得：
   - 端點 URL
   - 金鑰 1 或金鑰 2

## 📖 使用方法

### 網頁應用程式 (推薦)

啟動 Streamlit 應用程式：

```bash
streamlit run app.py
```

然後在瀏覽器中開啟 `http://localhost:8501`

**功能特色：**
- 🖱️ 拖放式檔案上傳
- 📊 互動式圖表顯示
- 🎨 美觀的使用者介面
- ⚙️ 即時參數調整

### 命令列工具

基本使用：
```bash
python cli.py image.jpg
```

詳細分析：
```bash
python cli.py image.jpg --detailed
```

輸出到 JSON 檔案：
```bash
python cli.py image.jpg --output result.json --format json
```

設定信心度閾值：
```bash
python cli.py image.jpg --confidence 0.8
```

### Python API

```python
from food_recognition import FoodRecognition

# 初始化辨識器
recognizer = FoodRecognition()

# 分析影像
result = recognizer.analyze_image("food.jpg")

# 獲取詳細分析
detailed_result = recognizer.get_detailed_analysis("food.jpg")

# 從位元組資料分析
with open("food.jpg", "rb") as f:
    image_data = f.read()
result = recognizer.analyze_image_from_bytes(image_data)
```

## 📊 輸出格式

### 基本分析結果

```json
{
  "success": true,
  "foods_detected": ["apple", "banana", "salad"],
  "description": "一盤新鮮的水果沙拉",
  "tags": ["food", "fruit", "healthy", "fresh"],
  "confidence_scores": {
    "apple": 0.95,
    "banana": 0.87,
    "salad": 0.92
  },
  "nutrition_info": {
    "total_calories": 220,
    "protein": 3.8,
    "carbohydrates": 52,
    "fat": 0.9,
    "fiber": 9
  },
  "recommendations": [
    "建議添加蛋白質來源，如雞肉、魚肉或豆類",
    "這是一頓營養均衡的餐點！"
  ]
}
```

### 詳細分析結果

包含額外資訊：
- `analysis_timestamp`: 分析時間戳
- `image_path`: 影像檔案路徑
- `health_score`: 健康評分 (0-100)

## 🎯 支援的食物類型

### 🍎 水果類
- 蘋果、香蕉、橘子、草莓
- 葡萄、西瓜、奇異果、鳳梨

### 🍖 蛋白質類
- 雞肉、魚肉、牛肉、豬肉
- 蝦子、鮭魚、鮪魚、蛋類

### 🥗 蔬菜類
- 沙拉、胡蘿蔔、花椰菜
- 番茄、生菜、洋蔥、青椒

### 🍞 穀物類
- 米飯、麵條、麵包、披薩
- 漢堡、三明治、義大利麵

### 🥤 飲品類
- 咖啡、茶、果汁、牛奶
- 水、汽水、酒精飲料

## ⚙️ 進階設定

### 環境變數

| 變數名稱 | 說明 | 範例 |
|---------|------|------|
| `AZURE_VISION_ENDPOINT` | Azure Computer Vision API 端點 | `https://your-resource.cognitiveservices.azure.com/` |
| `AZURE_VISION_KEY` | Azure Computer Vision API 金鑰 | `your-api-key-here` |

### 可選設定

```bash
# Azure OpenAI API (用於更詳細的食物分析)
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

## 🔧 自訂開發

### 擴展營養資料庫

編輯 `food_recognition.py` 中的 `nutrition_db` 字典：

```python
nutrition_db = {
    'your_food': {
        'calories': 100,
        'protein': 5,
        'carbs': 20,
        'fat': 2,
        'fiber': 3
    }
}
```

### 自訂食物關鍵字

修改 `_identify_food_tags` 方法中的 `food_keywords` 列表。

### 調整健康評分算法

修改 `_calculate_health_score` 方法中的評分邏輯。

## 🐛 疑難排解

### 常見問題

1. **API 金鑰錯誤**
   ```
   錯誤：請設定 AZURE_VISION_ENDPOINT 和 AZURE_VISION_KEY 環境變數
   ```
   **解決方案：** 檢查 `.env` 檔案中的 API 金鑰設定

2. **網路連線問題**
   ```
   錯誤：API 請求失敗
   ```
   **解決方案：** 檢查網路連線和防火牆設定

3. **影像格式不支援**
   ```
   錯誤：找不到影像檔案
   ```
   **解決方案：** 確保使用支援的影像格式 (PNG, JPG, JPEG, GIF, BMP)

4. **信心度過低**
   ```
   沒有信心度超過 70% 的食物被檢測到
   ```
   **解決方案：** 
   - 使用更清晰的影像
   - 降低信心度閾值
   - 確保食物在影像中佔主要部分

### 除錯模式

在網頁應用程式中勾選「顯示所有檢測到的標籤（除錯用）」來查看完整的 API 回應。

## 📈 效能優化

### 影像處理建議

- **解析度**：建議使用 1024x1024 像素以上的影像
- **格式**：優先使用 JPG 或 PNG 格式
- **檔案大小**：建議不超過 4MB
- **構圖**：確保食物在畫面中清晰可見

### API 使用最佳實踐

- 實作請求重試機制
- 使用適當的請求間隔
- 監控 API 使用量
- 實作快取機制

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設定

1. Fork 專案
2. 建立功能分支
3. 實作功能
4. 添加測試
5. 提交 Pull Request

### 程式碼風格

- 遵循 PEP 8 規範
- 添加適當的註解
- 使用類型提示
- 撰寫單元測試

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [Azure Computer Vision API](https://azure.microsoft.com/services/cognitive-services/computer-vision/)
- [Streamlit](https://streamlit.io/) - 網頁應用程式框架
- [Plotly](https://plotly.com/) - 互動式圖表庫

## 📞 支援

如有問題或建議，請：

1. 查看 [Issues](../../issues) 頁面
2. 建立新的 Issue
3. 聯繫開發團隊

---

**🍽️ 享受智慧食物辨識的樂趣！** 