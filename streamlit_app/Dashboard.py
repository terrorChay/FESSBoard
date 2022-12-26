import streamlit as st
from streamlit import session_state as session
import utils as utils
from my_query import query_dict
import pandas as pd
import numpy as np
import plotly.express as px
from connectdb import mysql_conn
from datetime import datetime


@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

@st.experimental_memo
def load_projects():
    # Load data from database
    projects_df = query_data(query_dict['projects'])
    managers_df = query_data(query_dict['managers_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    teachers_df = query_data(query_dict['teachers_in_projects']).merge(query_data(query_dict['teachers']), on='ID преподавателя', how='left')

    # Join multiple managers and teachers into list values
    managers_df = managers_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index()
    teachers_df = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index()

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(managers_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')

    # Set project ID as dataframe index
    projects_df.set_index('ID проекта', drop=True, inplace=True)
    projects_df.rename(columns={'ФИО студента':'Менеджеры', 'ФИО преподавателя':'Преподаватели'}, inplace=True)
    return projects_df

@st.experimental_memo
def load_students_in_projects():
    students_df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    students_df.dropna(axis=0, subset=['ID группы'], inplace=True)
    students_df.set_index('ID проекта', drop=True, inplace=True)
    return students_df

@st.experimental_memo
def load_students():
    return query_data(query_dict['students'])

def main():
    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df = load_projects()
    with st.spinner('Происходит аджайл...'):
        students_in_projects_df = load_students_in_projects()
    with st.spinner('Hamdulilah'):
        students_df = load_students()
    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Всего проектов',   projects_df.shape[0])
    col2.metric('Всего студентов',  students_df.shape[0])
    col3.metric('Уникальных направлений', projects_df['Направление'].nunique())
    col4.metric('Уникальных партнеров', projects_df['Название компании'].nunique())
    # first row
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        with st.container():
            st.subheader('Темп прироста проектов')
            
    with col2:
        with st.container():
            st.subheader('Всего проектов')

    with col3:
        with st.container():
            st.subheader('Что-то еще')

    # second row
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        with st.container():
            st.subheader('Какой-то кружок')

    with col2:
        with st.container():
            # st.subheader('Вовлеченность потока')
            options = sorted(students_df.loc[(students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['Бак. год'].unique(), reverse=True)
            options = list(map(lambda x: f'{x} - {x+4}', options))
            year = st.selectbox(label='Динамика вовлеченности потока', options=options, index=0)
            year = int(year[:4])
            if year:
                m = students_df.loc[(students_df['Бак. год'] == year) & (students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['ID студента'].nunique()
                l = []
                for i in range(0, 4):
                    e = students_in_projects_df.loc[
                            (students_in_projects_df['Бак. год'] == year)
                        &   (students_in_projects_df['Бакалавриат'] == 'ФЭСН РАНХиГС')
                        &   (students_in_projects_df['Дата окончания'].between(datetime.strptime(f'{year+i}-09-01', '%Y-%m-%d').date(), datetime.strptime(f'{year+i+1}-09-01', '%Y-%m-%d').date()))
                        ]['ID студента'].nunique()
                    # e - Кол-во уникальных студентов с потока N, приниваших участие в проектах за 1 курс
                    l.append(e/m)
                data = pd.Series(l, (f'1 курс ({year}-{year+1})',f'2 курс ({year+1}-{year+2})',f'3 курс ({year+2}-{year+3})',f'4 курс ({year+3}-{year+4})'))
                fig = px.bar(data)
                fig.update_yaxes(range = [0,1])
                fig.update_layout(yaxis_tickformat=".0%")
                st.plotly_chart(fig, use_container_width=True)

    with col3:
        with st.container():
            st.subheader('Какой-то график')


if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()