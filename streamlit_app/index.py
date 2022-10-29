import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from gsheetsdb import connect

# Подключение к БД
conn = connect()
@st.experimental_memo
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    df = pd.DataFrame(rows)
    return df

# Настройка
def init():
    # Настройки страницы
    st.set_page_config(layout='wide', page_title='FESSBoard')

    # Импорт градиентов
    global colorscales
    colorscales = px.colors.named_colorscales()

    # Импорт CSS стилей
    try: # Local launch
        with open('/app/fessboard/streamlit_app/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open('styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Парсинг датафрейма из гугл таблиц
    global df
    global list_of_headers
    sheet_url = 'https://docs.google.com/spreadsheets/d/1W_mPyvhZHNZeSo00g0ewu5F1YLjXCtdhNFQqfzBS1I0/edit?usp=sharing'
    query = f'SELECT * FROM "{sheet_url}"'
    df = run_query(query)
    list_of_headers = df.columns.values.tolist()

# Донат пай чарт
def myDonut(values, names, title=None, hovertemplate='<b>%{label}<br>Процент: %{percent}</b>', textinfo='value', font_size=20, center_text='', center_text_size=26, bLegend=False, theme=px.colors.sequential.RdBu):
    fig = px.pie(
                    values = values,
                    names = names,
                    title = title,
                    color_discrete_sequence = theme,
                    hole = 0.6)
    fig.update_traces(   
                        hovertemplate = hovertemplate,
                        textinfo = textinfo,
                        textfont_size = font_size)
    fig.update_layout(  
                        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=center_text_size, showarrow=False)],
                        margin = dict(l=10, r=10),
                        showlegend = bLegend)
    st.plotly_chart(fig, use_container_width = True)

# Запуск приложения
def run():
    # Запускаем настройки
    init()

    # Обработка датафрейма 
    ## Общее
    df_unique_count = df.nunique()
    ## Расчеты для проектов
    total_count = df_unique_count['ID']
    active_projects = df[df['Дата_окончания'].isna()]
    active_count = active_projects.shape[0]
    inactive_count = total_count - active_count
    ## Расчеты для сфер
    sph_df = pd.pivot_table(df, values = 'ID', columns ='Сфера_проекта', aggfunc ='count')
    sph_names = sph_df.columns.to_list()
    sph_count = df_unique_count['Сфера_проекта']
    sph_values = sph_df.values[0]
    ## Расчеты для партнеров
    partners_df = pd.pivot_table(df, values = 'ID', columns ='Компания', aggfunc ='count')
    partners_names = partners_df.columns.to_list()
    partners_count = df_unique_count['Компания']
    partners_values = partners_df.values[0]

    tab1, tab2, tab3 = st.tabs(["Проекты", "Сферы", "Партнеры"])
    # Контейнер проектов
    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            myDonut(
                        values          = [active_count, inactive_count], 
                        names           = ['Активные', 'Завершенные'],
                        hovertemplate   = "<b>%{label} проекты</b><br>Процент: %{percent}",
                        center_text     = f'<b>{inactive_count/total_count}%<br>завершено</b>')
            st.metric("Всего проектов", total_count)
        
        with col2:
            pass

    # Контейнер направлений
    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            myDonut(
                        values          = sph_values, 
                        names           = sph_names,
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{len(sph_names)}<br>сфер</b>')
            st.metric("Всего направлений", sph_count)
        
        with col2:
            st.dataframe(sph_df)
        
    with tab3:
        col1, col2 = st.columns([1, 3])
        with col1:
            myDonut(
                        values          = partners_values, 
                        names           = partners_names,
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{len(partners_names)}<br>сфер</b>')
            st.metric("Всего партнеров", partners_count)    

        with col2:
            st.dataframe(partners_df)  
    
    # Контейнер с таблицей
    with st.container():
        st.dataframe(df)
                
if __name__ == '__main__':
    run()