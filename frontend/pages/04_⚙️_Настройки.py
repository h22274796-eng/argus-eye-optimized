import streamlit as st
import json
import os

def main():
    st.set_page_config(page_title="Настройки - Argus Eye")
    st.title("⚙️ Настройки системы")

    config_path = "config.json"
    
    # Загружаем текущие настройки или ставим дефолтные
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                current_config = json.load(f)
        except:
            current_config = {}
    else:
        current_config = {"use_openvino": True, "use_sahi": True, "threads": 4}

    with st.form("settings_form"):
        st.subheader("Оптимизация производительности")
        
        use_ov = st.checkbox("Использовать Intel OpenVINO (ускорение CPU)", 
                             value=current_config.get("use_openvino", True))
        
        use_sh = st.checkbox("Включить режим SAHI (детекция мелких объектов)", 
                             value=current_config.get("use_sahi", True))
        
        threads = st.slider("Количество потоков CPU", 1, 16, 
                            value=current_config.get("threads", 4))

        st.divider()
        st.subheader("Сетевые настройки")
        api_url = st.text_input("Адрес бэкенда (API URL)", 
                                value=os.environ.get("API_URL", "https://argus-eye-optimized.onrender.com"))

        submitted = st.form_submit_button("💾 Сохранить и применить")
        
        if submitted:
            new_config = {
                "use_openvino": use_ov,
                "use_sahi": use_sh,
                "threads": threads,
                "api_url": api_url
            }
            with open(config_path, "w") as f:
                json.dump(new_config, f)
            
            st.success("✅ Настройки сохранены! Для применения некоторых параметров может потребоваться перезапуск.")

if __name__ == "__main__":
    main()