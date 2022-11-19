import streamlit as st

# page settings
def load_page_setup(title, layout='wide'):
    st.set_page_config(layout=layout, page_title=title)
    
# load css with local source
def load_local_css(file_name):
    try: # Local launch
        with open(f'/app/fessboard/streamlit_app/{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open(f'{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# load css with external source
def load_remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

# set material ui icon
def set_MU_icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)