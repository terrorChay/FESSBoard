import mysql.connector
import streamlit as st


#Connecting to MySql
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])
global conn
conn = init_connection()