import streamlit as st
import requests
import os

st.set_page_config(page_title="Argus Eye", layout="wide")

# ВАЖНО: Укажите адрес вашего бэкенда на Render
# Если запускаете локально, поменяйте на http://localhost:8000
API_URL = os.environ.get("API_URL", "https://argus-eye-optimized.onrender.com")

def check_api():
    try:
        r = requests.get(f"{API_URL}/api/v1/health", timeout=2)
        return r.status_code == 200
    except: return False

st.sidebar.title("👁️ Argus Eye")
is_online = check_api()

if is_online:
    st.sidebar.success("● API: Online")
else:
    st.sidebar.error("○ API: Offline")

menu = st.sidebar.selectbox("Меню", ["Загрузка", "История"])

st.title("Система анализа")

if menu == "Загрузка":
    st.header("📸 Загрузка снимков")
    file = st.file_uploader("Выберите фото", type=['jpg', 'jpeg', 'png'])
    
    if file and st.button("Начать анализ"):
        if is_online:
            with st.spinner("Работает нейросеть..."):
                try:
                    res = requests.post(f"{API_URL}/api/v1/detect", files={"file": file.getvalue()})
                    if res.status_code == 200:
                        data = res.json()
                        st.success("Анализ завершен!")
                        st.json(data)
                    else:
                        st.error(f"Ошибка сервера: {res.status_code}")
                except Exception as e:
                    st.error(f"Ошибка связи: {e}")
        else:
            st.warning("Бэкенд недоступен")

elif menu == "История":
    st.header("📜 История задач")
    if is_online:
        try:
            res = requests.get(f"{API_URL}/api/v1/tasks")
            if res.status_code == 200:
                st.table(res.json())
        except:
            st.error("Ошибка загрузки данных")