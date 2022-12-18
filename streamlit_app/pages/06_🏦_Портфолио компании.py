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
    is_float_dtype,
)
import plotly.express as px
from connectdb import mysql_conn
 
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
    projects_df.set_index('ID проекта', drop=True, inplace=True)
    projects_df.rename(columns={'ФИО студента':'Менеджеры', 'ФИО преподавателя':'Преподаватели'}, inplace=True)
    return projects_df

@st.experimental_memo
def load_companies():
    companies_df = query_data(query_dict['companies'])
    return companies_df

@st.experimental_memo
def load_students_in_projects(project_ids):
    # Load data from database
    students_df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    students_df.set_index('ID проекта', drop=True, inplace=True)

    students_with_company   = project_ids.merge(students_df, how='left', left_index=True, right_index=True)
    students_with_company.dropna(axis=0, subset=['ID группы', 'ID студента'], inplace=True)

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
            elif (is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255) and ('Название проекта' not in df[column].name):
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
    df = df[['ID компании', 'Название компании', 'Тип компании', 'Отрасль']].copy()
    df.insert(0, 'Составной ключ', df['ID компании'].astype('str') + ' - ' + df['Название компании'])
    company = False

    modification_container = st.container()
    with modification_container:
        left, right = st.columns(2)
        # Filters for household name selection input
        ## df.columns[1:] so that the company name is not used (its the first col)
        for idx, column in enumerate(df.columns[2:]):
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
        if 'company_selectbox' in session:
            try:
                preselection = int(np.where(options == session['company_selectbox'])[0][0])
            except:
                pass

        user_cat_input = st.selectbox(
            "Название компании",
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
    with st.spinner('Изучаем SCRUM...'):
        projects_df = load_projects()
    st.title('Портфолио компании')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранной компании!
            ''')
    # Draw company search filters and return chosen company
    company = company_selection(projects_df)
    if company:
        company_id = int(company[:5].split(' - ')[0])
        tab1, tab2, tab3 = st.tabs(['О компании', 'Проекты', 'Студенты'])
        # load info about company as a dictionary
        with st.spinner('Делаем однотумбовые столы...'):
            company_data_df            = load_companies()
        company_data_df            = company_data_df.loc[company_data_df['ID компании'] == company_id].to_dict()
        # load only projects with selected company
        projects_with_company   = projects_df.loc[projects_df['ID компании'] == company_id]
        # load only students who had projects with selected company
        with st.spinner('Захватываем мир...'):
            students_with_company   = load_students_in_projects(projects_with_company[['Название проекта']])

        # О компании
        with tab1:
            try:
                col1, col2 = st.columns([3, 1])
                for key, value in company_data_df.items():
                    key = key.casefold()
                    value = list(value.values())[0]
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
                    elif 'название компании' in key:
                        col1.subheader(value)
                    elif 'id компании' in key:
                        pass
                    else:
                        # col1.text_input(label=key, value=value, disabled=True)
                        col1.caption(value)
            except:
                st.error('Ошибка 1')
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
                    project_name = projects_with_company['Название проекта'].loc[project_idx]
                    with st.expander(f'Проект "{project_name}"'):

                        students_in_project     = students_with_company[['ID группы', 'ФИО студента', 'Бакалавриат', 'Магистратура']].loc[[project_idx]]
                        unique_groups_idx       = students_in_project['ID группы'].unique()
                        group_counter = 0
                        for group_idx in unique_groups_idx:
                            st.caption(f'Группа {group_counter+1}')
                            students_in_group   = students_in_project[students_in_project['ID группы'] == group_idx].reset_index()
                            st.dataframe(students_in_group[['ФИО студента', 'Бакалавриат', 'Магистратура']], use_container_width=True)    
                            
                            group_counter += 1
            else:
                st.warning('Проектные команды не найдены')

        # Студенты
        with tab3:
            # Draw search filters and return filtered df
            _students_with_company  = students_with_company[['ID студента', 'ФИО студента']].dropna(subset='ID студента', inplace=False)
            _projects_count         = students_with_company.groupby(['ID студента'])['ID студента'].count().sort_values(ascending=False).to_frame(name='Проектов с компанией').reset_index(drop=False)
            projects_count          = _projects_count.merge(_students_with_company, how='left', on='ID студента').drop_duplicates()
            df_search_applied   = search_dataframe(projects_count[['ФИО студента', 'Проектов с компанией']], label='Поиск по студентам')
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