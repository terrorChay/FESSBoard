import streamlit as st
from streamlit import session_state as session
import pandas as pd
import plotly.express as px

def init():
    # Настройки страницы
    st.set_page_config(layout='wide', page_title='FESSBoard')
    # Импорт CSS стилей
    try: # Local launch
        with open('/app/fessboard/streamlit_app/styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open('styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # Настройка страницы
    st.set_page_config(
        page_title="Главная Страница",
        page_icon="✋🏻" 
    )
    from connectdb import conn

    st.title("Главная Страница")
    st.sidebar.success("Выберете страницу 📖")

    # Подгрузка бибилотеки цветных градиентов
    global colorscales
    colorscales = px.colors.named_colorscales()

    frame = pd.read_sql('select * from projects', conn)
    st.dataframe(pd.DataFrame(frame))

    df = frame

    fig = px.pie(df.loc[df['project_company'] > 5], values = 'project_company', names = 'project_name')
    st.write (fig)

    fig_1 = px.pie(df, values = 'project_id', names = 'project_field', hole =.2)
    st.write (fig_1)

    st.bar_chart(df, x = 'project_end_date', y = 'project_id')




# Подключение к БД
def run():
    test = st.text_input('Переменная на странице дашборд')
    btn = st.button('Сохранить')
    if btn:
        session['test_123'] = test

if __name__ == '__main__':
    init()
    run()
    main()