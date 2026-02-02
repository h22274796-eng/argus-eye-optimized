import streamlit as st
import requests
import os

st.set_page_config(page_title="Сравнение - Argus Eye", layout="wide")

# Автоматическое определение URL API
API_URL = os.environ.get("API_URL", "https://argus-eye-optimized.onrender.com")

st.title("🔄 Детекция изменений (Change Detection)")

col1, col2 = st.columns(2)
with col1:
    img1 = st.file_uploader("Снимок ДО", type=['jpg', 'jpeg', 'png'], key="u1")
with col2:
    img2 = st.file_uploader("Снимок ПОСЛЕ", type=['jpg', 'jpeg', 'png'], key="u2")

st.sidebar.header("Настройки алгоритма")
method = st.sidebar.selectbox("Метод анализа", ["absdiff", "opticalflow"])
sensitivity = st.sidebar.slider("Чувствительность", 1, 100, 30)

if img1 and img2:
    if st.button("🚀 Начать сравнение"):
        with st.spinner("Рассчитываем разницу между кадрами..."):
            try:
                files = {
                    "file1": (img1.name, img1.getvalue(), img1.type),
                    "file2": (img2.name, img2.getvalue(), img2.type)
                }
                data = {"method": method, "threshold": str(sensitivity)}
                
                # Запрос к эндпоинту сравнения
                res = requests.post(f"{API_URL}/api/v1/compare", files=files, data=data)
                
                if res.status_code == 200:
                    result = res.json()
                    if result.get("status") == "success":
                        metrics = result.get("result", {})
                        st.success(f"Анализ завершен! Найдено изменений: {metrics.get('changes', 0)}")
                        st.json(metrics)
                    else:
                        st.error(f"Ошибка алгоритма: {result.get('message')}")
                else:
                    st.error(f"Ошибка сервера: {res.status_code}")
            except Exception as e:
                st.error(f"Ошибка связи: {e}")
else:
    st.info("Пожалуйста, загрузите два изображения для проведения сравнительного анализа.")