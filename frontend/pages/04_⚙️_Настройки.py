import streamlit as st
import json
import os

def main():
    st.set_page_config(page_title="Настройки - Argus Eye")
    st.title("⚙️ Настройки системы")

    # Путь к файлу настроек
    config_path = "config.json"
    
    # Загружаем текущие настройки
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            current_config = json.load(f)
    else:
        current_config = {"use_openvino": True, "use_sahi": True, "threads": 4}

    # ФОРМА НАСТРОЕК
    with st.form("settings_form"):
        st.subheader("Оптимизация CPU")
        
        # Если st.toggle всё еще не работает после обновления, замени на st.checkbox
        use_ov = st.checkbox("Использовать Intel OpenVINO", value=current_config.get("use_openvino", True))
        use_sh = st.checkbox("Включить SAHI (для мелких объектов)", value=current_config.get("use_sahi", True))
        threads = st.slider("Количество потоков CPU", 1, 16, current_config.get("threads", 4))

        # ОБЯЗАТЕЛЬНАЯ КНОПКА (решает ошибку Missing Submit Button)
        submitted = st.form_submit_button("Сохранить настройки")
        
        if submitted:
            new_config = {
                "use_openvino": use_ov,
                "use_sahi": use_sh,
                "threads": threads
            }
            with open(config_path, "w") as f:
                json.dump(new_config, f)
            st.success("✅ Настройки сохранены и применены!")

if __name__ == "__main__":
    main()