import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
import pandas as pd
import numpy as np
import re
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import xlsxwriter
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import plotly.express as px
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
    query = """
            SELECT
                projects.project_id AS 'ID',
                T1.company_name AS 'Заказчик',
                T2.company_type AS 'Тип компании',
                T3.company_sphere AS 'Отрасль',
                projects.project_name AS 'Название',
                projects.project_description AS 'Описание',
                projects.project_result AS 'Результат',
                projects.project_start_date AS 'Дата начала',
                projects.project_end_date AS 'Дата окончания',
                project_grades.grade AS 'Грейд',
                project_fields.field AS 'Направление',
                CONCAT_WS(
                    ' ',
                    T5.student_surname,
                    T5.student_name,
                    T5.student_midname) AS 'Менеджер проекта',
                CONCAT_WS(
                    ' ',
                    T7.teacher_surname,
                    T7.teacher_name,
                    T7.teacher_midname) AS 'Курирующий преподаватель',
                projects.is_frozen AS 'Заморожен'
            FROM projects 
            LEFT JOIN project_grades
                ON projects.project_grade   = project_grades.grade_id
            LEFT JOIN project_fields
                ON projects.project_field   = project_fields.field_id
            LEFT JOIN   (
                            (SELECT companies.company_id, companies.company_name, companies.company_type, companies.company_sphere FROM companies) AS T1
                                LEFT JOIN 
                                    (SELECT company_types.company_type_id, company_types.company_type FROM company_types) AS T2
                                    ON T1.company_type = T2.company_type_id
                                LEFT JOIN
                                    (SELECT company_spheres.company_sphere_id, company_spheres.company_sphere FROM company_spheres) AS T3
                                    ON T1.company_sphere = T3.company_sphere_id
                        )
                ON projects.project_company = T1.company_id
            LEFT JOIN   (
                            (SELECT managers_in_projects.project_id, managers_in_projects.student_id FROM managers_in_projects) AS T4
                                LEFT JOIN
                                    (SELECT students.student_id, students.student_surname, students.student_name, students.student_midname FROM students) AS T5
                                    ON T4.student_id = T5.student_id
                        )
                ON projects.project_id = T4.project_id
            LEFT JOIN   (
                            (SELECT teachers_in_projects.project_id, teachers_in_projects.teacher_id FROM teachers_in_projects) AS T6
                                LEFT JOIN
                                    (SELECT teachers.teacher_id, teachers.teacher_surname, teachers.teacher_name, teachers.teacher_midname FROM teachers) AS T7
                                    ON T6.teacher_id = T7.teacher_id
                        )
                ON projects.project_id = T6.project_id;
            """
    projects_df = query_data(query)
    projects_df.set_index('ID', drop=True, inplace=True)
    return projects_df

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    user_text_input = st.text_input(f"Поиск по проектам", help='Укажите текст, который могут содержать интересующие Вас проекты')

    if user_text_input:
        _user_text_input = "".join([char for char in user_text_input if char.isalnum()])
        mask = df.apply(lambda x: x.astype(str).str.contains(_user_text_input, na=False, flags=re.IGNORECASE))
        df = df.loc[mask.any(axis=1)]

    return df

# Apply filters and return filtered dataset
def filter_dataframe(df: pd.DataFrame, cols_to_ignore: list) -> pd.DataFrame:

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)
    
    modification_container = st.container()

    with modification_container:
        cols = [col for col in df.columns if col not in cols_to_ignore]
        to_filter_columns = st.multiselect("Параметры фильтрации", cols)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("└")
            if is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f" {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f" {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            # use selectbox for instances where there are < 10 unique vals or where max len option is < 255
            elif (is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255) and ('азвание' not in df[column].name):
                options = df[column].unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options
                )
                if user_cat_input == []:
                    _cat_input = df[column].unique()
                else:
                    _cat_input = user_cat_input
                df = df[df[column].isin(_cat_input)]
            else:
                user_text_input = right.text_input(
                    f"{column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    # Try to convert datetimes into displayable date formats
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d-%m-%Y')

    return df

@st.experimental_memo
def convert_df(df: pd.DataFrame, to_excel=False):
    if to_excel:
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='FESSBoard')
        workbook = writer.book
        worksheet = writer.sheets['FESSBoard']
        format1 = workbook.add_format({'num_format': '0.00'}) 
        worksheet.set_column('A:A', None, format1)  
        workbook.close()
        processed_data = output.getvalue()
    else:
        processed_data = df.to_csv().encode('utf-8')
    return processed_data

# App launch
def run():
    # Load dataframe
    projects_df = load_projects()
    st.title('Поиск проектов')
    st.write('''
            #### На данной странице можно составить выборку проектов по заданным параметрам!
            :mag: __Поиск по проектам__ выводит проекты, в которых фигурирует введенный текст.  
            :art: __Параметры фильтрации__ выводят проекты, которые удовлетворяют заданным параметрам.\n
            :sunglasses: Поиск и фильтры можно использовать вместе!  
            :floppy_disk: Вы также можете скачать составленную выборку в формате Microsoft Excel.
            ''')
    # Draw search filters and return filtered df
    df_search_applied   = search_dataframe(projects_df)
    # if search has results -> draw criteria filters and return filtered df
    if df_search_applied.shape[0]:
        df_filters_applied  = filter_dataframe(df_search_applied, ['Заморожен'])
        # if filters have results -> draw DF, download btn and analytics
        if df_filters_applied.shape[0]:
            tab1, tab2 = st.tabs(["Данные", "Аналитика"])
            with tab1:
                st.dataframe(df_filters_applied)
                st.download_button('Скачать CSV', data=convert_df(df_filters_applied), file_name="fessboard_slice.csv", mime='text/csv')
                st.download_button('Скачать XLSX', data=convert_df(df_filters_applied, True), file_name="fessboard_slice.xlsx")
            with tab2:
                st.write('какая-то аналитика')
            # Feedback btn
            st.sidebar.button(label='Сообщить об ошибке')
        else:
            # Technically only possible with long string criteria filters cuz they allow for any string input
            st.warning('Проекты не найдены')
    else:
        st.warning('Проекты не найдены')

if __name__ == "__main__":
    setup.page_config(layout='wide', title='Поиск проектов')
    setup.remove_footer()
    run()