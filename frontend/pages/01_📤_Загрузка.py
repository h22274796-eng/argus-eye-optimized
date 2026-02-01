import streamlit as st
import requests

st.title("📤 Загрузка")
files = st.file_uploader("Снимки", accept_multiple_files=True)
if st.button("Обработать") and files:
    for f in files:
        res = requests.post("http://localhost:8000/api/v1/detect", files={"file": f.getvalue()})
        if res.status_code == 200:
            st.success(f"Файл {f.name} обработан.")