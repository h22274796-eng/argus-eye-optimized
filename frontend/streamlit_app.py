import streamlit as st
import requests

# Настройки страницы
st.set_page_config(page_title="Argus Eye", layout="wide")

# Исправленный адрес API: используем 127.0.0.1 и порт 8000
API_URL = "https://argus-eye-optimized.onrender.com"

def check_api():
    try:
        # Добавляем таймаут, чтобы интерфейс не зависал при поиске API
        r = requests.get(f"{API_URL}/api/v1/health", timeout=2)
        return r.status_code == 200
    except:
        return False

# Сайдбар
st.sidebar.title("👁️ Argus Eye")
is_online = check_api()

if is_online:
    st.sidebar.success("● API: Online")
else:
    st.sidebar.error("○ API: Offline")
    st.sidebar.info(f"Ожидаемый адрес: {API_URL}")
    if st.sidebar.button("Обновить статус"):
        st.rerun()

# Меню
menu = st.sidebar.selectbox("Меню", ["Загрузка", "История"])

st.title("Система анализа")

if menu == "Загрузка":
    st.header("📸 Загрузка снимков")
    
    file = st.file_uploader(
        label="Выберите изображение для анализа", 
        type=['jpg', 'jpeg', 'png']
    )
    
    if file:
        st.image(file, caption="Загруженное фото")
        
        if is_online:
            if st.button("🚀 Начать анализ"):
                with st.spinner("Нейросеть обрабатывает изображение..."):
                    try:
                        # Отправка файла на бэкенд
                        files = {"file": (file.name, file.getvalue(), file.type)}
                        res = requests.post(f"{API_URL}/api/v1/detect", files=files)
                        
                        if res.status_code == 200:
                            data = res.json()
                            st.success(f"Анализ завершен!")
                            
                            # Вывод результатов
                            detections = data.get('detections', [])
                            if detections:
                                st.subheader(f"Найдено объектов: {len(detections)}")
                                for det in detections:
                                    # В вашем API ключи 'class_name' и 'confidence' (согласно schemas.py)
                                    name = det.get('class_name', 'Unknown')
                                    conf = det.get('confidence', 0.0)
                                    st.write(f"📍 **{name}** (уверенность: {conf:.2f})")
                            else:
                                st.info("Объекты не обнаружены.")
                                
                            with st.expander("Посмотреть сырой ответ (JSON)"):
                                st.json(data)
                        else:
                            st.error(f"Ошибка сервера: {res.status_code}")
                    except Exception as e:
                        st.error(f"Ошибка связи: {e}")
        else:
            st.warning("⚠️ API недоступен. Запустите backend/app.py")

elif menu == "История":
    st.header("📜 История анализов")
    if is_online:
        try:
            res = requests.get(f"{API_URL}/api/v1/tasks")
            if res.status_code == 200:
                tasks = res.json()
                if tasks:
                    st.table(tasks)
                else:
                    st.info("История пуста.")
        except:
            st.error("Не удалось загрузить историю.")