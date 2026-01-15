# 🍴 智選食光 - 餐廳搜尋器

這是一個基於 Streamlit 運行的 Web App，能根據使用者的定位、預算與口味推薦餐廳。

### 功能特點：
- 📍 **精準定位**：支援 GPS 自動定位或手動地址搜尋。
- 📏 **半徑篩選**：可設定 100m 至 5km 的搜尋範圍。
- 💰 **預算控制**：串接 Google 價格等級過濾。
- 🗺️ **地圖視覺化**：整合 Folium 互動式地圖，快速查看餐廳位置。

### 如何執行：
1. 取得 [Google Places API Key](https://console.cloud.google.com/)。
2. 安裝套件：`pip install -r requirements.txt`
3. 啟動 App：`streamlit run app.py`
