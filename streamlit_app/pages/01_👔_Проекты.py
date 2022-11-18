import streamlit as st
import streamlit_setup as setup



if __name__ == '__main__':
    st.set_page_config(layout='wide', page_title='FESSBoard')
    setup.load_local_css('styles.css')
    st.markdown("""
    # Карточка проекта
    """)