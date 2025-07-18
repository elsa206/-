# 食物熱量提取器 - 簡化版本

這是一個專門用於從台灣 FDA 食品營養資料庫提取食物名稱和熱量資訊的簡化工具。

## 功能特色

- 🍎 **專注熱量提取**：只提取食物名稱和熱量資訊
- ⚡ **快速版本**：提供快速測試版本，限制頁數
- 📊 **多種輸出格式**：CSV、JSON、Excel 格式
- 🔍 **搜尋功能**：支援食物名稱搜尋
- 📈 **統計分析**：熱量分布統計
- 🧪 **完整測試**：包含單元測試和整合測試

## 檔案說明

### 主要程式檔案

- `simple_food_calories.py` - 完整版本的食物熱量提取器
- `quick_calories.py` - 快速版本（限制頁數，適合測試）
- `simple_calories_test.py` - 測試檔案

### 配置檔案

- `requirements.txt` - Python 依賴套件
- `env.example` - 環境變數範例
- `start.bat` / `start.sh` - 啟動腳本

## 快速開始

### 1. 環境設定

```bash
# 複製環境變數檔案
copy env.example .env

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 執行快速版本

```bash
# Windows
python quick_calories.py

# Linux/Mac
python3 quick_calories.py
```

### 3. 執行完整版本

```bash
# Windows
python simple_food_calories.py

# Linux/Mac
python3 simple_food_calories.py
```

### 4. 執行測試

```bash
# 執行所有測試
python -m pytest simple_calories_test.py -v

# 執行特定測試
python simple_calories_test.py
```

## 使用方式

### 快速版本 (quick_calories.py)

適合測試和快速驗證：

```python
from quick_calories import QuickCalorieExtractor

# 創建提取器
extractor = QuickCalorieExtractor()

# 提取前5頁資料
data = extractor.extract_calories(limit_pages=5)

# 搜尋特定食物
results = extractor.search_food("蘋果")
print(f"蘋果熱量: {results['calories']} kcal")
```

### 完整版本 (simple_food_calories.py)

功能完整的提取器：

```python
from simple_food_calories import SimpleCalorieExtractor

# 創建提取器
extractor = SimpleCalorieExtractor()

# 提取所有資料
data = extractor.extract_all_calories()

# 儲存為不同格式
extractor.save_to_csv("food_calories.csv")
extractor.save_to_json("food_calories.json")
extractor.save_to_excel("food_calories.xlsx")

# 搜尋和統計
stats = extractor.get_calorie_statistics()
print(f"平均熱量: {stats['average_calories']} kcal")
```

## 輸出格式

### CSV 格式
```csv
食物名稱,熱量(kcal),分類
蘋果,52,水果類
白米飯,116,穀類
雞胸肉,165,肉類
```

### JSON 格式
```json
{
  "foods": [
    {
      "name": "蘋果",
      "calories": 52,
      "category": "水果類"
    }
  ],
  "statistics": {
    "total_foods": 1000,
    "average_calories": 120.5
  }
}
```

## 功能特色

### 🔍 搜尋功能
- 精確搜尋：完全匹配食物名稱
- 模糊搜尋：部分匹配食物名稱
- 分類搜尋：按食物分類搜尋

### 📊 統計分析
- 熱量分布統計
- 分類統計
- 熱量範圍分析

### 💾 資料管理
- 自動去重
- 資料驗證
- 錯誤處理

## 測試

### 執行測試
```bash
# 執行所有測試
python simple_calories_test.py

# 使用 pytest
python -m pytest simple_calories_test.py -v
```

### 測試覆蓋範圍
- 資料提取測試
- 搜尋功能測試
- 檔案輸出測試
- 錯誤處理測試

## 注意事項

1. **網路連線**：需要穩定的網路連線來訪問 FDA 網站
2. **請求頻率**：預設延遲 1 秒，避免對伺服器造成負擔
3. **資料更新**：FDA 網站資料可能定期更新
4. **使用限制**：請遵守網站的使用條款

## 疑難排解

### 常見問題

**Q: 網路連線錯誤**
A: 檢查網路連線，確認可以訪問 FDA 網站

**Q: 資料提取失敗**
A: 檢查環境變數設定，確認 URL 正確

**Q: 記憶體不足**
A: 使用快速版本或增加記憶體限制

### 錯誤代碼

- `ConnectionError`: 網路連線問題
- `TimeoutError`: 請求超時
- `ValueError`: 資料格式錯誤
- `FileNotFoundError`: 檔案路徑錯誤

## 授權

本專案僅供學習和研究使用，請遵守相關網站的使用條款。

## 聯絡資訊

如有問題或建議，請聯繫開發團隊。 