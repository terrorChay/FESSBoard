import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
import pandas as pd
import plotly.express as px
from connectdb import mysql_conn

# Запрос к базе данных, делается заново только если новые данные или прошло 10 минут, иначе - из кэша
@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

#  Загрузка и первичная обработка датасета, делается заново только если используются новые данные (если старые - то из кэша)
@st.experimental_memo
def load_data():
    df = query_data('select * from projects')
    return df

def main():

    st.title("Главная Страница")
    st.sidebar.success("Выберете страницу 📖")

    # Достаем датафрейм
    df = load_data()

    fig = px.pie(df.loc[df['project_company'] > 5], values = 'project_company', names = 'project_name')
    st.write(fig)

    fig_1 = px.pie(df, values = 'project_id', names = 'project_field', hole =.2)
    st.write(fig_1)

    st.bar_chart(df, x = 'project_end_date', y = 'project_id')


if __name__ == "__main__":
    # page setup
    setup.page_config(layout='wide', title='FESSBoard')
    # styles
    setup.remove_footer()
    setup.load_local_css('styles.css')
    # main func
    main()