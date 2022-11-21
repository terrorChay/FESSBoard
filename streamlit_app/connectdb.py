import mysql.connector
import streamlit as st
from contextlib import contextmanager

#Connecting to MySql
@contextmanager
def mysql_conn():
    connection = mysql.connector.connect(**st.secrets["mysql"])
    try:
       yield connection
    finally:
        connection.close()