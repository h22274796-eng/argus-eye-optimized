import streamlit as st
import requests

st.set_page_config(page_title="Сравнение", layout="wide")
API_URL = "http://127.0.0.1:8000/api/v1/compare"

st.title("🔄 Детекция изменений")

col1, col2 = st.columns(2)
with col1:
    img1 = st.file_uploader("Снимок ДО", type=['jpg', 'png'], key="u1")
with col2:
    img2 = st.file_uploader("Снимок ПОСЛЕ", type=['jpg', 'png'], key="u2")

st.sidebar.header("Настройки")
method = st.sidebar.selectbox("Метод анализа", ["opticalflow", "absdiff"])
sensitivity = st.sidebar.slider("Чувствительность", 1, 100, 30)

if img1 and img2:
    if st.button("🚀 Начать сравнение"):
        with st.spinner("Рассчитываем разницу..."):
            try:
                files = {
                    "file1": (img1.name, img1.getvalue(), img1.type),
                    "file2": (img2.name, img2.getvalue(), img2.type)
                }
                payload = {"method": method, "threshold": str(sensitivity)}
                
                res = requests.post(API_URL, files=files, data=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    if data["status"] == "success":
                        st.success(f"Анализ завершен! Изменено пикселей: {data['result']['changes']}")
                        st.json(data["result"])
                    else:
                        st.error(f"Ошибка алгоритма: {data.get('message')}")
                else:
                    st.error(f"Ошибка сервера: {res.status_code}")
            except Exception as e:
                st.error(f"Не удалось отправить запрос: {e}")
else:
    st.info("Загрузите два изображения для сравнения.")