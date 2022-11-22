import streamlit as st
from streamlit import session_state as session
import plotly.express as px
import pandas as pd
import streamlit_setup as setup
from connectdb import mysql_conn
from datetime import date
 
 # Database Query
@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

# Load projects dataset
@st.experimental_memo
def load_projects():
    query   =   """
                SELECT
                    projects.project_id 'ID',
                    companies.company_name 'Заказчик',
                    company_types.company_type 'Тип компании',
                    projects.project_name 'Название',
                    projects.project_description 'Описание',
                    projects.project_result 'Результат',
                    projects.project_start_date 'Дата начала',
                    projects.project_end_date 'Дата окончания',
                    project_grades.grade 'Грейд',
                    project_fields.field 'Направление',
                    projects.is_frozen 'Заморожен'
                FROM projects 
                LEFT JOIN project_grades
                    ON projects.project_grade   = project_grades.grade_id
                LEFT JOIN project_fields
                    ON projects.project_field   = project_fields.field_id
                LEFT JOIN (companies
                            LEFT JOIN company_types
                                ON companies.company_type = company_types.company_type_id)
                    ON projects.project_company = companies.company_id;
                """
    projects_df = query_data(query)
    projects_df['Дата окончания']   = pd.to_datetime(projects_df['Дата окончания'], format='%Y-%m-%d')
    projects_df['Дата начала']      = pd.to_datetime(projects_df['Дата начала'], format='%Y-%m-%d')
    session['projectss'] = projects_df
    return projects_df

@st.experimental_memo
def get_controls_vals(df):
    vals = {
        'Заказчики'         :   sorted(df['Заказчик'].unique()),
        'Типы компаний'     :   sorted(df['Тип компании'].unique()),
        'Направления'       :   sorted(df['Направление'].unique()),
        'Грейды'            :   sorted(df['Грейд'].unique())
    }
    return vals
# Apply filters and return filtered dataset
@st.experimental_memo
def filter_dataframe(dataframe, filters):
    pass

@st.experimental_memo
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Запуск приложения
def run():
    # Проверяем есть ли в кэше датафрейм с проектами, если да, то берем его от туда, если нет - то загружаем его заново
    if 'projectss' not in st.session_state:
        projects_df = load_projects()
    else:
        projects_df = session.projectss

    # Controls vals
    controls_vals = get_controls_vals(projects_df)
    # Controls
    selected_companies          = st.sidebar.multiselect(label='Выберите компании', options=controls_vals['Заказчики'])
    selected_company_types      = st.sidebar.multiselect(label='Выберите типы компаний', options=controls_vals['Типы компаний'])
    selected_spheres            = st.sidebar.multiselect(label='Выберите направления', options=controls_vals['Направления'])
    selected_grades             = st.sidebar.multiselect(label='Выберите грейды', options=controls_vals['Грейды'])
    selected_years              = st.sidebar.multiselect(label='Выберите годы', options=range(2015, 2022, 1))
    show_active                 = st.sidebar.checkbox('Показывать активные', True)
    show_inactive               = st.sidebar.checkbox('Показывать завершенные', True)
    st.title('Поиск проектов')
    st.write('''
            На данной странице можно составить выборку проектов при заданных настройках.  
            Настройки расположены в левой боковой панели приложения.  
            Вы можете скачать составленную выборку в формате .CSV (совместимо с Microsoft Excel).
            ''')
    tab1, tab2 = st.tabs(["Данные", "Аналитика"])
    with tab1:
        st.dataframe(projects_df, use_container_width=True)
        csv = convert_df(projects_df)
        st.download_button('Скачать таблицу', data=csv, file_name="fessboard_slice.csv", mime='text/csv', )
    with tab2:
        st.write('какая-то аналитика')

if __name__ == "__main__":
    setup.page_config(layout='centered', title='Поиск проектов')
    setup.load_local_css('styles.css')
    run()