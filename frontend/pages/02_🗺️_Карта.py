import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Карта объектов", layout="wide")

API_URL = "http://127.0.0.1:8000"

st.title("📍 Геолокация обнаруженных объектов")

try:
    res = requests.get(f"{API_URL}/api/v1/tasks", timeout=3)
    if res.status_code == 200:
        tasks = res.json()
        
        # Фильтруем только те записи, где есть координаты
        map_data = []
        for t in tasks:
            # Проверяем наличие ключей 'lat' и 'lon' и что они не пустые
            if t.get('lat') and t.get('lon'):
                map_data.append({
                    'lat': float(t['lat']),
                    'lon': float(t['lon']),
                    'name': f"Task {t.get('task_id', 'Unknown')[:8]}"
                })
        
        if map_data:
            df = pd.DataFrame(map_data)
            st.map(df)
            st.table(df)
        else:
            st.info("В базе данных пока нет снимков с GPS-координатами.")
            st.warning("Для отображения на карте загружайте фото, содержащие EXIF-данные о местоположении.")
            
    else:
        st.error("Ошибка при получении данных с сервера.")
except Exception as e:
    st.error(f"Не удалось подключиться к API: {e}")