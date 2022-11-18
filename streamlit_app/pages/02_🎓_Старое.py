import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from gsheetsdb import connect
import streamlit_setup as setup

# Подключение к БД
conn = connect()
@st.experimental_memo
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    df = pd.DataFrame(rows)
    return df

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
    return fig

# Запуск приложения
def run():
    # Запускаем настройки

    # Тянем данные
    sheet_url = 'https://docs.google.com/spreadsheets/d/1W_mPyvhZHNZeSo00g0ewu5F1YLjXCtdhNFQqfzBS1I0/edit?usp=sharing'
    query = f'SELECT * FROM "{sheet_url}"'
    df = run_query(query)
    list_of_headers = df.columns.values.tolist()

    # Обрабатываем данные 
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
                st.metric("Всего проектов", total_count)
                fig = myDonut(
                            values          = [active_count, inactive_count], 
                            names           = ['Активные', 'Завершенные'],
                            hovertemplate   = "<b>%{label} проекты</b><br>Процент: %{percent}",
                            center_text     = f'<b>{round(100*(inactive_count/total_count))}%<br>завершено</b>')
                st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(df)

    # Контейнер направлений
    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего направлений", sph_count)
            fig = myDonut(
                        values          = sph_values, 
                        names           = sph_names,
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{len(sph_names)}<br>сфер</b>')
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(sph_df, use_container_width=True)
        
    with tab3:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего партнеров", partners_count)

        with col2:
            fig = px.bar(partners_df.T, orientation='h', )  
            st.plotly_chart(fig, use_container_width=True) 
    
    with st.container():
        st.text('interesting content')
        st.text('in a potentially ')
        st.text('very stylish container')

    col1, col2, col3 = st.columns(3)
    col1.write('cool column box 1')
    col2.write('cool column box 2')
    col3.write('cool column box 3')


if __name__ == "__main__":
    st.set_page_config(layout='centered', page_title='DEPRICATED')
    setup.load_local_css('styles.css')
    run()