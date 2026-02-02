import streamlit as st
import requests
import os

# Автоматическое определение URL API: берем из переменных окружения или используем локальный
API_URL = os.environ.get("API_URL", "https://argus-eye-optimized.onrender.com")

st.set_page_config(page_title="Загрузка - Argus Eye", layout="wide")

st.title("📤 Загрузка и анализ снимков")

files = st.file_uploader("Выберите снимки с БПЛА (поддерживаются JPG, PNG)", accept_multiple_files=True)

if st.button("🚀 Обработать все") and files:
    for f in files:
        with st.spinner(f"Обработка {f.name}..."):
            try:
                # Отправляем файл на бэкенд
                res = requests.post(
                    f"{API_URL}/api/v1/detect", 
                    files={"file": (f.name, f.getvalue(), f.type)}
                )
                
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"✅ Файл {f.name} успешно обработан.")
                    with st.expander(f"Результаты для {f.name}"):
                        st.write(f"Найдено объектов: {len(data.get('detections', []))}")
                        st.json(data)
                else:
                    st.error(f"❌ Ошибка при обработке {f.name}: Код {res.status_code}")
            except Exception as e:
                st.error(f"📡 Ошибка соединения с API: {e}")