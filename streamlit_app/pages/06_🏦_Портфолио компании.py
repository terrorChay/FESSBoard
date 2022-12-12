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
    is_float_dtype,
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
    query_i =   """
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
                    CASE
                        WHEN
                            projects.is_frozen = 1
                        THEN 'Заморожен'
                        WHEN
                            projects.is_frozen != 1 AND DAYNAME(projects.project_end_date) IS NULL
                        THEN 'Активен'
                        ELSE 'Завершен'
                    END AS 'Статус'
                FROM projects 
                LEFT JOIN project_grades
                    ON projects.project_grade_id   = project_grades.grade_id
                LEFT JOIN project_fields
                    ON projects.project_field_id   = project_fields.field_id
                LEFT JOIN   (
                                (SELECT companies.company_id, companies.company_name, companies.company_type_id, companies.company_sphere_id FROM companies) AS T1
                                    LEFT JOIN 
                                        (SELECT company_types.company_type_id, company_types.company_type FROM company_types) AS T2
                                        ON T1.company_type_id = T2.company_type_id
                                    LEFT JOIN
                                        (SELECT company_spheres.company_sphere_id, company_spheres.company_sphere FROM company_spheres) AS T3
                                        ON T1.company_sphere_id = T3.company_sphere_id
                            )
                    ON projects.project_company_id = T1.company_id;
                """
    query_j =   """
                SELECT
                    projects.project_id AS 'ID',
                    CONCAT_WS(
                        ' ',
                        T5.student_surname,
                        T5.student_name,
                        T5.student_midname) AS 'Менеджер проекта'
                FROM projects 
                LEFT JOIN   (
                                (SELECT managers_in_projects.project_id, managers_in_projects.student_id FROM managers_in_projects) AS T4
                                    LEFT JOIN
                                        (SELECT students.student_id, students.student_surname, students.student_name, students.student_midname FROM students) AS T5
                                        ON T4.student_id = T5.student_id
                            )
                    ON projects.project_id = T4.project_id;
                """
    query_k =   """
                SELECT
                    projects.project_id AS 'ID',
                    CONCAT_WS(
                        ' ',
                        T7.teacher_surname,
                        T7.teacher_name,
                        T7.teacher_midname) AS 'Курирующий преподаватель'
                FROM projects 
                LEFT JOIN   (
                                (SELECT teachers_in_projects.project_id, teachers_in_projects.teacher_id FROM teachers_in_projects) AS T6
                                    LEFT JOIN
                                        (SELECT teachers.teacher_id, teachers.teacher_surname, teachers.teacher_name, teachers.teacher_midname FROM teachers) AS T7
                                        ON T6.teacher_id = T7.teacher_id
                            )
                    ON projects.project_id = T6.project_id;
                """
    # Projects dataframe (no many-to-many relations)
    projects_df = query_data(query_i)

    # Managers dataframe (many-to-many relations)
    managers_df = query_data(query_j)
    managers_df.replace('', np.nan, inplace=True)
    managers_df.dropna(inplace=True)
    managers_df = managers_df.groupby(['ID'])['Менеджер проекта'].apply(list).reset_index()

    # Teachers dataframe (many-to-many relations)
    teachers_df = query_data(query_k)
    teachers_df.replace('', np.nan, inplace=True)
    teachers_df.dropna(inplace=True)
    teachers_df = teachers_df.groupby(['ID'])['Курирующий преподаватель'].apply(list).reset_index()

    # Left join dataframes
    projects_df = projects_df.merge(managers_df, on='ID', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID', how='left')

    # Set project ID as dataframe index
    projects_df.set_index('ID', drop=True, inplace=True)
    return projects_df

@st.experimental_memo
def load_company_data(company: str):
    query   =   f"""
                SELECT
                    T1.company_name AS 'Заказчик',
                    T2.company_type AS 'Тип компании',
                    T3.company_sphere AS 'Отрасль',
                    T1.company_website AS 'Веб-сайт',
                    T1.company_logo_url AS 'Логотип'
                FROM    (
                            (SELECT companies.company_id, companies.company_name, companies.company_type_id, companies.company_sphere_id, companies.company_website, companies.company_logo_url FROM companies) AS T1
                                LEFT JOIN 
                                    (SELECT company_types.company_type_id, company_types.company_type FROM company_types) AS T2
                                    ON T1.company_type_id = T2.company_type_id
                                LEFT JOIN
                                    (SELECT company_spheres.company_sphere_id, company_spheres.company_sphere FROM company_spheres) AS T3
                                    ON T1.company_sphere_id = T3.company_sphere_id
                        )
                WHERE
                    company_name = '{company}'
                """
    company_data_df = query_data(query)
    return company_data_df

@st.experimental_memo
def load_students_in_projects(project_ids):
    query   =   """
                SELECT
                    T01.project_id AS 'ID',
                    T0.group_id AS 'Группа',
                    T3.student_id AS 'ID студента',
                    CONCAT_WS(
                        ' ',
                        T3.student_surname,
                        T3.student_name,
                        T3.student_midname) AS 'Студент',
                    bach_name AS 'Бакалавриат',
                    bach_reg_name AS 'Бак. регион',
                    T3.bachelors_start_year AS 'Бак. год',
                    mast_name AS 'Магистратура',
                    mast_reg_name as 'Маг. регион',
                    T3.masters_start_year AS 'Маг. год',
                    student_statuses.student_status AS 'Статус'
                FROM    (SELECT projects.project_id, projects.project_company_id FROM projects) AS T01
                LEFT JOIN   (
                                (SELECT groups_in_projects.project_id, groups_in_projects.group_id FROM groups_in_projects) AS T0

                                        LEFT JOIN (SELECT groups.group_id FROM groups) AS T1
                                                
                                                LEFT JOIN (SELECT students_in_groups.student_id, students_in_groups.group_id FROM students_in_groups) AS T2

                                                        LEFT JOIN (SELECT students.student_id, students.student_surname, students.student_name, students.student_midname, students.student_status_id, students.bachelors_university_id, students.bachelors_start_year, students.masters_university_id, students.masters_start_year FROM students) AS T3
                                                                
                                                                LEFT JOIN student_statuses
                                                                ON T3.student_status_id = student_statuses.student_status_id

                                                                LEFT JOIN universities
                                                                ON T3.bachelors_university_id = universities.university_id

                                                                LEFT JOIN   (
                                                                                (SELECT universities.university_id AS 'bach_id', universities.university_name AS 'bach_name', universities.university_region_id AS 'bach_reg_id' FROM universities) AS T4
                                                                                    LEFT JOIN
                                                                                        (SELECT regions.region_id, regions.region 'bach_reg_name', regions.is_foreign FROM regions) AS T5
                                                                                        ON bach_reg_id = T5.region_id
                                                                            )
                                                                ON bach_id = T3.bachelors_university_id

                                                                LEFT JOIN   (
                                                                                (SELECT universities.university_id AS 'mast_id', universities.university_name AS 'mast_name', universities.university_region_id AS 'mast_reg_id' FROM universities) AS T6
                                                                                    LEFT JOIN
                                                                                        (SELECT regions.region_id, regions.region AS 'mast_reg_name', regions.is_foreign FROM regions) AS T7
                                                                                        ON mast_reg_id = T7.region_id
                                                                            )
                                                                ON mast_id = T3.masters_university_id

                                                        ON T2.student_id = T3.student_id

                                                ON T1.group_id = T2.group_id

                                        ON T0.group_id = T1.group_id
                            )
                ON T01.project_id = T0.project_id;
                """
    # get students in groups in projects
    students_df = query_data(query)
    students_df.set_index('ID', drop=True, inplace=True)

    students_with_company   = project_ids.merge(students_df, how='left', left_index=True, right_index=True)
    students_with_company.dropna(axis=0, subset=['Группа', 'Студент'], inplace=True)

    return students_with_company

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

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame, label='Поиск') -> pd.DataFrame:

    df = df.copy()

    user_text_input = st.text_input(label, placeholder='Введите текст', help='Укажите текст, который могут содержать интересующие Вас проекты')

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
            if 'Менеджер' in df[column].name or 'Курирующий' in df[column].name:
                options = pd.Series([x for _list in df[column][df[column].notna()] for x in _list]).unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options,
                )
                if user_cat_input:
                    df = df[df[column].astype(str).str.contains('|'.join(user_cat_input))]
            elif is_numeric_dtype(df[column]):
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
            elif (is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255) and ('Название' not in df[column].name):
                options = df[column].unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options,
                )
                if user_cat_input:
                    _cat_input = user_cat_input
                    df = df[df[column].isin(_cat_input)]
            else:
                user_text_input = right.text_input(
                    f"{column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, na=False, flags=re.IGNORECASE)]

    # Try to convert datetimes into displayable date formats
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d-%m-%Y')

    return df

# Apply filters and return company name
def company_selection(df: pd.DataFrame):

    df = df[['Заказчик', 'Тип компании', 'Отрасль']].copy()
    company = False

    modification_container = st.container()

    with modification_container:
        left, right = st.columns(2)
        # Filters for household name selection input
        ## df.columns[1:] so that the company name is not used (its the first col)
        for idx, column in enumerate(df.columns[1:]):
            options = df[column].unique()
            ### preselection tweak to preserve selected filter values in case related filters get adjusted
            cached_value_key = column+'-input'
            preselection = []
            if cached_value_key in session:
                for i in session[cached_value_key]:
                    try:
                        if i in options:
                            preselection.append(i)
                    except:
                        pass
            ### display every other input field on the right column, all the rest - on the left column
            col = left if idx % 2 == 0 else right
            user_cat_input = col.multiselect(
                f"{column}",
                options,
                default=preselection,
                key=cached_value_key,
            )
            if user_cat_input:
                df = df[df[column].isin(user_cat_input)]
        options = np.insert(df['Заказчик'].unique(), 0, 'Не выбрано', axis=0)

        # Household name selection
        ## preselection tweak once again to preserve selected company in case related filters get adjusted
        preselection = 0
        if 'company_selectbox' in session:
            try:
                preselection = int(np.where(options == session['company_selectbox'])[0][0])
            except:
                pass

        user_cat_input = st.selectbox(
            "Заказчик",
            options,
            index=preselection,
            key='company_selectbox',
        )
        if user_cat_input and user_cat_input != 'Не выбрано':
            company = user_cat_input

    return company

# App launch
def run():
    # Feedback btn
    st.sidebar.button(label='Сообщить об ошибке')
    # Load dataframe
    projects_df = load_projects()
    st.title('Портфолио компании')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранной компании!
            ''')
    # Draw company search filters and return chosen company
    company = company_selection(projects_df)
    if company:
        tab1, tab2, tab3 = st.tabs(['О компании', 'Проекты', 'Студенты'])
        # load info about company as a dictionary
        company_data            = load_company_data(company).to_dict()
        # load only projects with selected company
        projects_with_company   = projects_df.loc[projects_df['Заказчик'] == company]
        # load only students who had projects with selected company
        students_with_company   = load_students_in_projects(projects_with_company[['Название']])

        # О компании
        with tab1:
            col1, col2 = st.columns([3, 1])
            for key, value in company_data.items():
                key = key.casefold()
                value = value[0]
                if 'сайт' in key:
                    col1.markdown(f'[{value}]({value})')
                elif 'логотип' in key:
                    if len(value) > 5:
                        try:
                            col2.image(value, use_column_width=True)
                        except:
                            col2.write('Логотип уехал в отпуск')
                    else:
                        col2.image('https://i.pinimg.com/originals/18/3e/9b/183e9bd688fe158b9141aa162c853382.jpg', use_column_width=True)
                elif 'заказчик' in key:
                    col1.subheader(value)
                else:
                    # col1.text_input(label=key, value=value, disabled=True)
                    col1.caption(value)
        # Проекты        
        with tab2:
            ## Draw search filters and return filtered df
            df_search_applied   = search_dataframe(projects_with_company, label='Поиск по проектам')
            ## if search has results draw dataframe and download buttons
            if df_search_applied.shape[0]:
                st.dataframe(df_search_applied, use_container_width=True)
                col1, col2, _col3, _col4, _col5, _col6 = st.columns([0.8, 1, 1, 1, 1, 1])
                col1.download_button('💾 CSV', data=convert_df(df_search_applied), file_name=f"{company}_slice.csv", mime='text/csv')
                col2.download_button('💾 Excel', data=convert_df(df_search_applied, True), file_name=f"{company}_slice.xlsx")
            else:
                st.warning('Проекты не найдены')
            # Project groups
            st.markdown('#### Просмотр проектных команд')
            unique_projects_idx = students_with_company.index.unique()
            if len(unique_projects_idx) >= 1:
                for project_idx in unique_projects_idx:
                    project_name = projects_with_company['Название'].loc[project_idx]
                    with st.expander(f'Проект "{project_name}"'):

                        students_in_project     = students_with_company[['Группа', 'Студент', 'Бакалавриат', 'Магистратура']].loc[[project_idx]]
                        unique_groups_idx       = students_in_project['Группа'].unique()
                        group_counter = 0
                        for group_idx in unique_groups_idx:
                            st.caption(f'Группа {group_counter+1}')
                            students_in_group   = students_in_project[students_in_project['Группа'] == group_idx].reset_index()
                            st.dataframe(students_in_group[['Студент', 'Бакалавриат', 'Магистратура']], use_container_width=True)    
                            
                            group_counter += 1
            else:
                st.warning('Проектные команды не найдены')

        # Студенты
        with tab3:
            # Draw search filters and return filtered df
            _students_with_company = students_with_company.dropna(subset='Студент', inplace=False)
            _students_with_company = students_with_company.groupby(['Студент'])['Студент'].count().sort_values(ascending=False).to_frame(name='Проектов с компанией').reset_index(drop=False)
            df_search_applied   = search_dataframe(_students_with_company, label='Поиск по студентам')
            # if search has results draw dataframe and download buttons
            if df_search_applied.shape[0]:
                st.dataframe(df_search_applied, use_container_width=True)
                st.download_button('Скачать CSV', data=convert_df(df_search_applied), file_name="fessboard_slice.csv", mime='text/csv')
                st.download_button('Скачать XLSX', data=convert_df(df_search_applied, True), file_name="fessboard_slice.xlsx")
            else:
                st.warning('Студенты не найдены')

    else:
        st.warning('Выберите компанию-заказчика')
    
if __name__ == "__main__":
    setup.page_config(layout='centered', title='Портфолио компании')
    setup.remove_footer()
    run()