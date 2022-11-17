import streamlit as st
# Настройка
def init():
    # Настройки страницы
    st.set_page_config(layout='wide', page_title='FESSBoard')
    # Импорт CSS стилей
    try: # Local launch
        with open('/app/fessboard/streamlit_app/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open('styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)