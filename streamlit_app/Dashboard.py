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
    query = ("""
            SELECT
                projects.project_id 'ID проекта',
                projects.project_name 'Имя проекта',
                projects.project_description 'Описание проекта',
                projects.project_result 'Результат проекта',
                projects.project_start_date 'Старт проекта',
                projects.project_end_date 'Окончание проекта',
                companies.company_name 'Название компании',
                companies.company_id 'ID компании'
            FROM projects
            INNER JOIN companies 
                ON projects.project_company = companies.company_id;
            """)
    project_df = query_data(query)
    session['projects_staroe'] = project_df
    return project_df

def main():

    st.title("Главная Страница")
    st.sidebar.success("Выберете страницу 📖")
    project_df = load_data()

    companies_df = pd.pivot_table (project_df, values='ID проекта', columns='Название компании', aggfunc='count')
    companies_name = companies_df.columns.tolist()
    companies_values = companies_df.values[0]

    fig = px.pie(project_df, values = companies_values, names = companies_name)
    st.write(fig)

    # fig = px.pie(df.loc[df['project_company'] > 5], values = 'project_company', names = 'project_name')
    # st.write(fig)

    # fig_1 = px.pie(df, values = 'project_id', names = 'project_field', hole =.2)
    # st.write(fig_1)

    # st.bar_chart(df, x = 'project_end_date', y = 'project_id')


if __name__ == "__main__":
    # page setup
    setup.page_config(layout='wide', title='FESSBoard')
    # styles
    setup.remove_footer()
    setup.load_local_css('styles.css')
    # main func
    main()