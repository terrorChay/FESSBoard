import mysql.connector
import streamlit as st
from contextlib import contextmanager

#Connecting to MySql
@contextmanager
def init_connection():
    connection = mysql.connector.connect(**st.secrets["mysql"])
    try:
       yield connection
    finally:
        connection.close()