import streamlit as st
import utils as utils
from my_query import query_dict
import pandas as pd
from connectdb import mysql_conn
 
 # Database Query
@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

# App launch
def run():
    for key, query in query_dict.items():
        st.header(f'query_dict[{key}]')
        with st.expander('Запрос'):
            st.code(query)
        with mysql_conn() as conn:
            df = pd.read_sql(query, conn)
        st.dataframe(df)

if __name__ == "__main__":
    utils.page_config(layout='wide', title='Поиск проектов')
    utils.load_local_css('css/project.css')
    utils.remove_footer()
    utils.set_logo()
    run()