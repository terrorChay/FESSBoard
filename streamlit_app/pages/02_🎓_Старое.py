import streamlit as st
from streamlit import session_state as session
import plotly.express as px
import pandas as pd
import streamlit_setup as setup
from connectdb import mysql_conn
from datetime import date

# Кэшированная 
@st.experimental_singleton
def load_data():
    with mysql_conn() as conn:
        query = """
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
        projects_df = pd.read_sql(query, conn)
        projects_df['Дата окончания']   = pd.to_datetime(projects_df['Дата окончания'], format='%Y-%m-%d')
        projects_df['Дата начала']      = pd.to_datetime(projects_df['Дата начала'], format='%Y-%m-%d')
    session.projects_staroe = projects_df
    return True

# Донат пай чарт
def myDonut(values=None, names=None, data=None, title=None, hovertemplate='<b>%{label}<br>Процент: %{percent}</b>', textinfo='value', font_size=20, center_text='', center_text_size=26, bLegend=False, theme=px.colors.sequential.RdBu):
    fig = px.pie(   
                    values      = values,
                    names       = names,
                    data_frame  = data,
                    title       = title,
                    color_discrete_sequence = theme,
                    hole        = 0.6)
    fig.update_traces(   
                        hovertemplate = hovertemplate,
                        textinfo = textinfo,
                        textfont_size = font_size)
    fig.update_layout(  
                        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=center_text_size, showarrow=False)],
                        margin = dict(l=10, r=10),
                        showlegend = bLegend)
    return fig

# Запуск приложения
def run():
    if 'projects_staroe' not in st.session_state:
        load_data()
    today = date.today().strftime('%Y-%m-%d')
    projects_df = session.projects_staroe
    ## Расчеты для проектов
    total_projects  = projects_df.shape[0]
    total_active    = projects_df.loc[(projects_df['Дата окончания'] < today)].shape[0]
    total_inactive  = total_projects - total_active
    active_ratio    = round(100*(total_inactive/total_projects))

    ## Расчеты для сфер
    total_spheres   = projects_df['Направление'].nunique()
    spheres_count   = projects_df.groupby(['Направление'])['Направление'].count().sort_values(ascending=False).to_frame(name='Кол-во проектов').reset_index(drop=False)

    ## Расчеты для партнеров
    total_companies         = projects_df['Заказчик'].nunique()
    companies_count         = projects_df.groupby(['Заказчик'])['Заказчик'].count().sort_values(ascending=False)
    companies_types_count   = projects_df.groupby(['Тип компании'])['Тип компании'].count().sort_values(ascending=False).to_frame(name='Кол-во проектов').reset_index(drop=False)

    tab1, tab2, tab3 = st.tabs(["Проекты", "Сферы", "Партнеры"])
    # Контейнер проектов
    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
                st.metric("Всего проектов", total_projects)
                fig = myDonut(
                            values          = [total_active, total_inactive], 
                            names           = ['Активные', 'Завершенные'],
                            hovertemplate   = "<b>%{label} проекты</b><br>Процент: %{percent}",
                            center_text     = f'<b>{active_ratio}%<br>завершено</b>')
                st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(projects_df)

    # Контейнер направлений
    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего направлений", total_spheres)
            fig = myDonut(
                        data            = spheres_count,
                        values          = 'Кол-во проектов',
                        names           = 'Направление',
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{total_spheres}<br>всего</b>')
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(spheres_count, use_container_width=True)
        
    with tab3:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего партнеров", total_companies)

        with col2:
            fig = px.bar(   companies_types_count, 
                            x = 'Тип компании',
                            y = 'Кол-во проектов',
                            color='Тип компании',
                            color_discrete_sequence=px.colors.sequential.RdBu)  
            st.plotly_chart(fig, use_container_width=True) 
    
    with st.container():
        st.dataframe(session.projects_staroe, use_container_width=True)

if __name__ == "__main__":
    setup.page_config(layout='wide', title='FESSBoard')
    setup.load_local_css('styles.css')
    run()