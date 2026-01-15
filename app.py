import streamlit as st
import googlemaps
import pandas as pd
from streamlit_js_eval import get_geolocation
from streamlit_folium import folium_static
import folium

# --- 頁面設定 ---
st.set_page_config(page_title="智選食光 - 餐廳搜尋器", layout="wide", page_icon="🍴")

# --- 自定義樣式 ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 初始化 Google Maps Client ---
# 優先從 Streamlit Secrets 讀取，若無則顯示輸入框
if "google_api_key" in st.secrets:
    api_key = st.secrets["google_api_key"]
else:
    api_key = st.sidebar.text_input("輸入 Google API Key", type="password")

if not api_key:
    st.warning("⚠️ 請在側邊欄輸入 Google Maps API Key 才能開始搜尋。")
    st.stop()

gmaps = googlemaps.Client(key=api_key)

# --- 側邊欄：搜尋條件 ---
with st.sidebar:
    st.title("🍔 搜尋條件")
    
    location_mode = st.radio("定位方式", ["瀏覽器 GPS 定位", "手動輸入地址"])
    
    if location_mode == "手動輸入地址":
        address = st.text_input("地點", "台北車站")
    else:
        loc = get_geolocation()
        address = None
    
    distance = st.select_slider("搜尋範圍 (m)", options=[100, 500, 1000, 5000], value=1000)
    
    col1, col2 = st.columns(2)
    with col1:
        meal_time = st.selectbox("用餐時段", ["不限", "早餐", "午餐", "晚餐", "消夜", "點心"])
    with col2:
        budget = st.select_slider("人均預算", options=["100", "300", "500", "1000"], value="500")
    
    cuisine = st.multiselect("菜色類型", ["中餐", "西餐", "日式", "韓式", "泰式", "義式", "燒肉", "火鍋", "咖啡廳"], default=["日式"])
    
    min_rating = st.slider("最低評分", 0.0, 5.0, 4.2, 0.1)
    
    search_btn = st.button("🔍 開始尋找美味")

# --- 核心邏輯 ---
def get_coords():
    if location_mode == "手動輸入地址":
        res = gmaps.geocode(address)
        if res:
            return res[0]['geometry']['location']['lat'], res[0]['geometry']['location']['lng']
    elif loc:
        return loc['coords']['latitude'], loc['coords']['longitude']
    return None, None

if search_btn:
    lat, lng = get_coords()
    
    if lat and lng:
        # 預算映射 (Google API 0-4)
        price_map = {"100": 1, "300": 2, "500": 3, "1000": 4}
        
        # 組合關鍵字
        query_keyword = f"{' '.join(cuisine)} {meal_time if meal_time != '不限' else ''}"
        
        with st.spinner('正在為您挑選最佳餐廳...'):
            places_result = gmaps.places_nearby(
                location=(lat, lng),
                radius=distance,
                keyword=query_keyword,
                type='restaurant',
                max_price=price_map[budget],
                language='zh-TW'
            )
            
            raw_results = places_result.get('results', [])
            
            # 評分過濾與資料清理
            final_list = []
            for p in raw_results:
                if p.get('rating', 0) >= min_rating:
                    final_list.append({
                        "name": p['name'],
                        "rating": p.get('rating', 'N/A'),
                        "address": p.get('vicinity'),
                        "price_level": p.get('price_level', 1),
                        "lat": p['geometry']['location']['lat'],
                        "lng": p['geometry']['location']['lng'],
                        "place_id": p['place_id']
                    })

            if final_list:
                df = pd.DataFrame(final_list)
                
                # --- 顯示結果 ---
                st.success(f"找到 {len(df)} 間符合條件的餐廳！")
                
                # 建立地圖
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], tooltip="你的位置", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
                
                for _, row in df.iterrows():
                    folium.Marker(
                        [row['lat'], row['lng']],
                        popup=f"<b>{row['name']}</b><br>評分: {row['rating']}<br>{row['address']}",
                        tooltip=row['name']
                    ).add_to(m)
                
                # 佈局：左側地圖，右側清單
                col_left, col_right = st.columns([2, 1])
                with col_left:
                    folium_static(m, width=800)
                
                with col_right:
                    for _, row in df.iterrows():
                        with st.expander(f"⭐ {row['rating']} | {row['name']}"):
                            st.write(f"📍 {row['address']}")
                            st.write(f"💰 價格等級: {'💵' * row['price_level']}")
                            st.markdown(f"[在 Google Map 查看](https://www.google.com/maps/search/?api=1&query=Google&query_place_id={row['place_id']})")
            else:
                st.error("此範圍內找不到符合條件的餐廳，請試著放寬預算或距離。")
    else:
        st.error("無法獲取位置資訊，請確認地址正確或已開啟瀏覽器定位。")
