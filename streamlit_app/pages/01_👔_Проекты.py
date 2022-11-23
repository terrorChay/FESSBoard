import streamlit as st
import streamlit_setup as setup



if __name__ == "__main__":
    setup.page_config(layout='wide', title='Карточка проекта')
    setup.load_local_css('styles.css')
    setup.remove_footer()
    st.markdown("""
    # Карточка проекта
    """)