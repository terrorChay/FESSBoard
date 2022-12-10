import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
import pandas as pd
import numpy as np
import plotly.express as px
from connectdb import mysql_conn


@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

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
def load_students():
    query   =   """
                SELECT
                    T01.project_id AS 'ID',
                    T0.group_id AS 'Группа',
                    T3.student_id AS 'ID студента',
                    CONCAT_WS(
                        ' ',
                        T3.student_surname,
                        T3.student_name,
                        T3.student_midname) AS 'Студент'
                FROM    (SELECT projects.project_id, projects.project_company_id FROM projects) AS T01
                LEFT JOIN   (
                                (SELECT groups_in_projects.project_id, groups_in_projects.group_id FROM groups_in_projects) AS T0
                                    LEFT JOIN
                                        (SELECT groups.group_id FROM groups) AS T1
                                            LEFT JOIN
                                                (SELECT students_in_groups.student_id, students_in_groups.group_id FROM students_in_groups) AS T2
                                                    LEFT JOIN
                                                        (SELECT students.student_id, students.student_surname, students.student_name, students.student_midname FROM students) AS T3
                                                    ON T2.student_id = T3.student_id
                                            ON T1.group_id = T2.group_id
                                    ON T0.group_id = T1.group_id
                )
                ON T01.project_id = T0.project_id;
                """
    students_df = query_data(query)
    students_df.dropna(axis=0, subset=['Группа'], inplace=True)
    students_df.set_index('ID', drop=True, inplace=True)

    return students_df

def main():
    logo_col, _col = st.columns([1, 6])
    logo_col.image('streamlit_app/img/logo_light.png', use_column_width=True)
    projects_df = load_projects()
    students_df = load_students()
    # metrics
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Всего проектов',   projects_df.shape[0])
        col2.metric('Всего студентов',  students_df.shape[0])
        col3.metric('Уникальных направлений', projects_df['Направление'].nunique())
        col4.metric('Уникальных партнеров', projects_df['Заказчик'].nunique())
    # first row
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader('Темп прироста проектов')
        with col2:
            st.subheader('Всего проектов')
        with col3:
            st.subheader('Что-то еще')

    # second row
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.subheader('Какой-то кружок')

        with col2:
            st.subheader('Распределение студентов')
            st.dataframe(students_df)
        with col3:
            st.subheader('Какой-то график')


if __name__ == "__main__":
    # page setup
    setup.page_config(layout='wide', title='FESSBoard')
    # styles
    setup.remove_footer()
    setup.load_local_css('styles.css')
    # main func
    main()