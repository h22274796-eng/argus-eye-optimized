import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Карта объектов - Argus Eye", layout="wide")

# Автоматическое определение URL API
API_URL = os.environ.get("API_URL", "https://argus-eye-optimized.onrender.com")

st.title("📍 Геолокация обнаруженных объектов")

try:
    res = requests.get(f"{API_URL}/api/v1/tasks", timeout=5)
    if res.status_code == 200:
        tasks = res.json()
        
        map_data = []
        for t in tasks:
            # Проверяем корректность координат
            lat = t.get('lat')
            lon = t.get('lon')
            if lat is not None and lon is not None:
                map_data.append({
                    'latitude': float(lat),
                    'longitude': float(lon),
                    'Task ID': t.get('task_id', 'N/A')[:8],
                    'Objects': t.get('detections_count', 0),
                    'Time': t.get('timestamp', '')
                })
        
        if map_data:
            df = pd.DataFrame(map_data)
            # Отображение встроенной карты Streamlit
            st.map(df)
            
            st.subheader("📋 Данные объектов")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("🔎 В базе данных пока нет снимков с GPS-координатами.")
            st.warning("Совет: Убедитесь, что загружаемые фото содержат EXIF-метаданные.")
            
    else:
        st.error(f"Сервер вернул ошибку: {res.status_code}")
except Exception as e:
    st.error(f"Не удалось подключиться к API: {e}")