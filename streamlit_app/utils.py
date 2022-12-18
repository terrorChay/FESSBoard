import streamlit as st

# set page layout
def page_config(title, layout='wide'):
    try:
        st.set_page_config(layout=layout, page_title=title)
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            return
        raise e

# load css with local source
def load_local_css(file_name):
    try: # Local launch
        with open(f'/app/fessboard/streamlit_app/{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open(f'{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# remove streamlit logo footer
def remove_footer():
    st.markdown('''
                <style>
                footer {
                    visibility: hidden;
                }
                </style>
                ''', unsafe_allow_html=True)

# set logo
def set_logo(dark=False):
    if dark:
        logo_url = 'https://github.com/terrorChay/FESSBoard/blob/master/streamlit_app/img/logo_dark.png?raw=true'
    else:
        logo_url = 'https://github.com/terrorChay/FESSBoard/blob/master/streamlit_app/img/logo_light.png?raw=true'

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({logo_url});
                background-size: 200px;
                background-repeat: no-repeat;
                background-position: 20px 50px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# load css with external source
def load_remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

# set material ui icon
def set_MU_icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)