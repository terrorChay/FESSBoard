import streamlit as st
from streamlit import session_state as session
from st_init import init

# Подключение к БД
def run():
    if 'test_123' in session:
        st.write(session.test_123)
    else:
        st.write('Ничего нет')
                
if __name__ == '__main__':
    init()
    run()