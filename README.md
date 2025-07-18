# USDA 食物熱量抓取器

這個專案專門用於從美國農業部(USDA) FoodData Central網站抓取食物名稱和對應的熱量資訊。

## 🌟 功能特色

- **多種抓取模式**: 完整抓取器、簡化抓取器、快速測試版本
- **智能分類**: 自動將食物分類為水果、蔬菜、穀物、蛋白質等
- **資料格式**: 支援CSV和JSON格式輸出
- **互動式查詢**: 提供快速查詢工具
- **樣本資料**: 包含50種常見食物的熱量資料

## 📁 檔案結構

```
黑客松-子賽事4/
├── usda_food_scraper.py          # 完整USDA抓取器
├── simple_usda_calories.py       # 簡化熱量提取器
├── quick_usda_test.py           # 快速測試版本
├── usda_calorie_lookup.py       # 熱量查詢工具
├── sample_usda_foods.json       # 樣本食物資料
├── requirements.txt             # Python依賴套件
└── README.md                   # 說明文件
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 快速測試

```bash
python quick_usda_test.py
```

### 3. 使用查詢工具

```bash
python usda_calorie_lookup.py
```

### 4. 完整抓取

```bash
python usda_food_scraper.py
```

### 5. 簡化抓取

```bash
python simple_usda_calories.py
```

## 📖 使用說明

### 快速測試版本 (`quick_usda_test.py`)

用於測試USDA API連接和基本功能：

```bash
python quick_usda_test.py
```

**功能**:
- 測試API連接
- 測試6種常見食物
- 顯示測試結果和統計

### 熱量查詢工具 (`usda_calorie_lookup.py`)

提供互動式查詢介面：

```bash
python usda_calorie_lookup.py
```

**使用方式**:
- 直接輸入食物名稱搜尋
- 輸入 `category:分類名` 搜尋特定分類
- 輸入 `categories` 查看所有分類
- 輸入 `stats` 查看統計資訊
- 輸入 `help` 顯示幫助
- 輸入 `quit` 退出

**可用分類**:
- fruits (水果)
- vegetables (蔬菜)
- grains (穀物)
- proteins (蛋白質)
- dairy (乳製品)
- nuts (堅果)
- beverages (飲料)
- snacks (零食)
- desserts (甜點)
- condiments (調味料)

### 簡化熱量提取器 (`simple_usda_calories.py`)

專門提取食物名稱和熱量：

```bash
python simple_usda_calories.py
```

**功能**:
- 提取100+種常見食物的熱量
- 自動分類
- 去重處理
- 支援互動式搜尋
- 輸出CSV和JSON格式

### 完整抓取器 (`usda_food_scraper.py`)

功能最完整的版本：

```bash
python usda_food_scraper.py
```

**功能**:
- 抓取所有分類的食物
- 詳細營養資訊
- 品牌資訊
- 成分列表
- 份量資訊

## 📊 資料格式

### JSON格式

```json
{
  "metadata": {
    "source": "USDA FoodData Central",
    "url": "https://fdc.nal.usda.gov/",
    "extracted_at": "2024-12-19T10:00:00",
    "total_foods": 50
  },
  "foods": [
    {
      "food_name": "Apple, raw, with skin",
      "energy_kcal": 52.0,
      "category": "fruits",
      "fdc_id": "171688"
    }
  ]
}
```

### CSV格式

| food_name | energy_kcal | category | fdc_id |
|-----------|-------------|----------|--------|
| Apple, raw, with skin | 52.0 | fruits | 171688 |
| Banana, raw | 89.0 | fruits | 173944 |

## 🔧 技術細節

### API使用

- **基礎URL**: `https://api.nal.usda.gov/fdc/v1`
- **API金鑰**: 使用 `DEMO_KEY` (免費演示版本)
- **請求限制**: 每分鐘1000次請求
- **資料類型**: Foundation Foods, SR Legacy Foods

### 營養素ID

- **208**: 能量 (kcal)
- **203**: 蛋白質 (g)
- **204**: 總脂肪 (g)
- **205**: 碳水化合物 (g)

### 錯誤處理

- 網路連接錯誤
- API回應錯誤
- 資料解析錯誤
- 檔案讀寫錯誤

## 📈 統計資訊

樣本資料包含：
- **總食物數量**: 50個
- **分類數量**: 10個
- **平均熱量**: 約200 kcal
- **熱量範圍**: 0-884 kcal

## 🛠️ 自訂設定

### 修改搜尋關鍵字

在 `simple_usda_calories.py` 中修改 `food_keywords` 列表：

```python
self.food_keywords = [
    'apple', 'banana', 'chicken',  # 添加或修改關鍵字
    # ... 更多關鍵字
]
```

### 修改分類對應

在 `simple_usda_calories.py` 中修改 `category_mapping` 字典：

```python
self.category_mapping = {
    'apple': 'fruits',
    'chicken': 'proteins',
    # ... 更多對應
}
```

### 調整請求參數

```python
self.request_delay = 1.0  # 請求間隔 (秒)
self.timeout = 30         # 請求超時 (秒)
```

## ⚠️ 注意事項

1. **API限制**: 使用演示API金鑰有請求次數限制
2. **網路連接**: 需要穩定的網路連接
3. **資料準確性**: 資料來源於USDA官方資料庫
4. **使用規範**: 請遵守USDA的使用條款

## 🔗 相關連結

- [USDA FoodData Central](https://fdc.nal.usda.gov/)
- [USDA API文檔](https://fdc.nal.usda.gov/api-guide.html)
- [營養素資料庫](https://fdc.nal.usda.gov/fdc-app.html#/food-details/171688/nutrients)

## 📝 更新日誌

- **2024-12-19**: 初始版本發布
- 支援基本食物熱量抓取
- 提供多種使用模式
- 包含樣本資料和查詢工具

## 🤝 貢獻

歡迎提交問題報告和功能建議！

## 📄 授權

本專案僅供學習和研究使用。資料來源於USDA FoodData Central，請遵守相關使用條款。 