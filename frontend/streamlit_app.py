import streamlit as st
import requests

# Настройки страницы
st.set_page_config(page_title="Argus Eye", layout="wide")

# Адрес API
API_URL = "http://127.0.0.1:8000"

def check_api():
    try:
        r = requests.get(f"{API_URL}/api/v1/health", timeout=1)
        return r.status_code == 200
    except:
        return False

# Сайдбар
st.sidebar.title("👁️ Argus Eye")
is_online = check_api()

if is_online:
    st.sidebar.success("● API: Online")
else:
    st.sidebar.error("○ API: Error")
    if st.sidebar.button("Обновить статус"):
        if hasattr(st, "rerun"): st.rerun()
        else: st.experimental_rerun()

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
        st.image(file, caption="Загруженное фото", width=500)
        
        if is_online:
            if st.button("🚀 Начать анализ"):
                with st.spinner("Нейросеть YOLO анализирует кадр..."):
                    try:
                        # ПРАВИЛЬНЫЙ ФОРМАТ ОТПРАВКИ ФАЙЛА
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
                                    st.write(f"📍 **{det['class']}** (уверенность: {det['conf']:.2f})")
                            else:
                                st.info("Объекты не обнаружены.")
                                
                            with st.expander("Посмотреть сырой ответ (JSON)"):
                                st.json(data)
                        else:
                            st.error(f"Ошибка сервера: {res.status_code}. Проверьте консоль бэкенда.")
                    except Exception as e:
                        st.error(f"Ошибка связи: {e}")
        else:
            st.warning("⚠️ API недоступен. Анализ невозможен.")

elif menu == "История":
    st.header("📜 История анализов")
    if is_online:
        try:
            res = requests.get(f"{API_URL}/api/v1/tasks")
            if res.status_code == 200:
                st.table(res.json())
        except:
            st.error("Не удалось загрузить историю.")