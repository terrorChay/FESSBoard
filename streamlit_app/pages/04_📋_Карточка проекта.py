import streamlit as st
from streamlit import session_state as session
import streamlit_setup as setup
from my_query import query_dict
import pandas as pd
import numpy as np
import re
from io import BytesIO
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
    # Load data from database
    projects_df = query_data(query_dict['projects'])
    managers_df = query_data(query_dict['managers_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    teachers_df = query_data(query_dict['teachers_in_projects']).merge(query_data(query_dict['teachers']), on='ID преподавателя', how='left')

    # Join multiple managers and teachers into list values
    managers_df = managers_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index()
    teachers_df = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index()

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(managers_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')

    # Set project ID as dataframe index
    # projects_df.set_index('ID проекта', drop=True, inplace=True)
    projects_df.rename(columns={'ФИО студента':'Менеджеры', 'ФИО преподавателя':'Преподаватели'}, inplace=True)
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
            elif is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255:
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

# Apply filters and return company name
def project_selection(df: pd.DataFrame):
    df = df[['ID проекта', 'Название проекта', 'Название компании', 'Грейд', 'Направление', 'Статус']].copy()
    df.insert(0, 'Составной ключ', df['ID проекта'].astype('str') + ' - ' + df['Название проекта'])
    selected_project = False

    modification_container = st.container()
    with modification_container:
        left, right = st.columns(2)
        # Filters for project selection
        ## df.columns[3:] so that the composite key, project id and project name are ignored
        for idx, column in enumerate(df.columns[3:]):
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
        options = np.insert(df['Составной ключ'].unique(), 0, 'Не выбрано', axis=0)

        # Household name selection
        ## preselection tweak once again to preserve selected company in case related filters get adjusted
        preselection = 0
        if 'project_selectbox' in session:
            try:
                preselection = int(np.where(options == session['project_selectbox'])[0][0])
            except:
                pass

        user_cat_input = st.selectbox(
            "Выбранный проект",
            options,
            index=preselection,
            key='project_selectbox',
        )
        if user_cat_input and user_cat_input != 'Не выбрано':
            selected_project = user_cat_input

    return selected_project

# App launch
def run():
    # Load dataframe
    projects_df = load_projects()
    st.title('Карточка проекта')
    st.write('''
            #### На данной странице можно ознакомиться со всей информацией по выбранному проекту!
            ''')
    selected_project = project_selection(projects_df)
    # Draw search filters and return filtered df
    if selected_project:
        project_id = int(selected_project[:5].split(' - ')[0])
        output = projects_df.loc[projects_df['ID проекта'] == project_id]
        st.table(output.T)

if __name__ == "__main__":
    setup.page_config(layout='wide', title='Поиск проектов')
    setup.remove_footer()
    run()