import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
from my_query import query_dict
import pandas as pd
import numpy as np
import plotly.express as px
from connectdb import mysql_conn


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
def load_students():
    students_df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    students_df.dropna(axis=0, subset=['ID группы'], inplace=True)
    students_df.set_index('ID проекта', drop=True, inplace=True)
    return students_df

def main():
    try:
        st.image('streamlit_app/img/logo_light.png', width=200)
    except:
        st.image('img/logo_light.png', width=200)

    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df = load_projects()
    with st.spinner('Происходит аджайл...'):
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
            st.subheader('Распределение студентов')
            st.dataframe(students_df)

    with col3:
        with st.container():
            st.subheader('Какой-то график')


if __name__ == "__main__":
    # page setup
    setup.page_config(layout='wide', title='FESSBoard')
    # styles
    setup.remove_footer()
    setup.load_local_css('styles.css')
    # main func
    main()