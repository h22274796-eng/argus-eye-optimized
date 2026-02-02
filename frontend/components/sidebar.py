import streamlit as st
import requests

def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/eye.png", width=100)
        st.title("Argus Eye")
        st.subheader("CPU Optimized v2.0")
        
        st.divider()
        
        # Статус API
        try:
            # ЗАМЕНЯЕМ localhost на 127.0.0.1 для стабильности
            res = requests.get("https://argus-eye-optimized.onrender.com/api/v1/health", timeout=5)
            if res.status_code == 200:
                st.success("● API: Connected")
            else:
                st.error("○ API: Error")
        except:
            st.warning("○ API: Offline")
            
        st.divider()
        
        st.info("💡 Совет: Для мелких объектов с дронов всегда включайте режим SAHI.")
        
        if st.button("🧹 Очистить кэш"):
            st.cache_data.clear()
            st.rerun()