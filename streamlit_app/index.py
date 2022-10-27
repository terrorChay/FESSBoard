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
    # На локалке нужно поменять путь к файлу на 'styles.css'
    with open('/app/fessboard/streamlit_app/styles.css', 'r') as f:
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
    ## Расчеты для проектов
    total_count = df.shape[0]
    active_projects = df[df['Дата_окончания'].isna()]
    active_count = active_projects.shape[0]
    inactive_count = total_count - active_count
    ## Расчеты для сфер
    sph_df = pd.pivot_table(df, values = 'ID', columns ='Сфера_проекта', aggfunc ='count')
    sph_names = sph_df.columns.to_list()
    sph_values = sph_df.values[0]

    # Контейнер с метриками и логотипом
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.image('https://fesn.ranepa.ru/img/fesn-logo.png')
        col2.metric("Проекты", total_count, "10")
        col3.metric("Партнеры", "45", "-15%")
        col4.metric("Участники", "хз", "1337%")

    # Контейнер с пай чартами
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            myDonut(
                        values          = [active_count, inactive_count], 
                        names           = ['Активные', 'Завершенные'],
                        hovertemplate   = "<b>%{label} проекты</b><br>Процент: %{percent}",
                        center_text     = f'<b>{total_count}<br>проектов</b>')
        with col2:
            myDonut(
                        values          = sph_values, 
                        names           = sph_names,
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{len(sph_names)}<br>сфер</b>')
    
    # Контейнер с таблицей
    with st.container():
        st.dataframe(df)
                
if __name__ == '__main__':
    run()