import streamlit as st
from streamlit import session_state as session
from st_init import init
import pandas as pd
import plotly.express as px
from connectdb import conn

def main():

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


if __name__ == '__main__':
    init()
    main()