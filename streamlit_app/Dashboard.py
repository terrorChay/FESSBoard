import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
import pandas as pd
import plotly.express as px
from connectdb import conn

@st.experimental_memo(ttl=600)
def load_data():
    # Достаем данные из бд
    frame = pd.read_sql('select * from projects', conn)
    st.dataframe(pd.DataFrame(frame))
    df = frame
    # Пихаем датафрейм в сессионную переменную
    session.projects = df
    return True

def main():

    st.title("Главная Страница")
    st.sidebar.success("Выберете страницу 📖")

    # Достаем датафрейм из сессионной переменной
    load_data()
    df = session.projects

    fig = px.pie(df.loc[df['project_company'] > 5], values = 'project_company', names = 'project_name')
    st.write(fig)

    fig_1 = px.pie(df, values = 'project_id', names = 'project_field', hole =.2)
    st.write(fig_1)

    st.bar_chart(df, x = 'project_end_date', y = 'project_id')


if __name__ == "__main__":
    # page setup
    setup.page_config(layout='wide', title='FESSBoard')

    # init session vars
    if 'projects' not in st.session_state:
        st.session_state['projects'] = 'not stated'

    # styles
    setup.load_local_css('styles.css')

    # main func
    main()