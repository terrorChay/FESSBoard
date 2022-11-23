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
    session['projects_staroe'] = projects_df
    return projects_df

# Perform heavy calculations on the dataset
@st.experimental_memo
def projects_calc(projects_df):
    ## Расчеты для проектов
    today = date.today().strftime('%Y-%m-%d')
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

    result = {
        'total_projects'        :   total_projects,
        'total_active'          :   total_active,
        'total_inactive'        :   total_inactive,
        'active_ratio'          :   active_ratio,
        'total_spheres'         :   total_spheres,
        'spheres_count'         :   spheres_count,
        'total_companies'       :   total_companies,
        'companies_count'       :   companies_count,
        'companies_types_count' :   companies_types_count
    }
    return result

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
    # Проверяем есть ли в кэше датафрейм с проектами, если да, то берем его от туда, если нет - то загружаем его заново
    if 'projects_staroe' not in st.session_state:
        projects_df = load_projects()
    else:
        projects_df = session.projects_staroe

    # Тяжеловесные подсчеты
    projects_info = projects_calc(projects_df)

    # Горизонтальный блок с табами
    tab1, tab2, tab3 = st.tabs(["Проекты", "Сферы", "Партнеры"])
    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
                st.metric("Всего проектов", projects_info['total_projects'])
                fig = myDonut(
                            values          = [projects_info['total_active'], projects_info['total_inactive']], 
                            names           = ['Активные', 'Завершенные'],
                            hovertemplate   = "<b>%{label} проекты</b><br>Процент: %{percent}",
                            center_text     = f"<b>{projects_info['active_ratio']}%<br>завершено</b>")
                st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(projects_df)

    with tab2:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего направлений", projects_info['total_spheres'])
            fig = myDonut(
                        data            = projects_info['spheres_count'],
                        values          = 'Кол-во проектов',
                        names           = 'Направление',
                        hovertemplate   = "<b>%{label}</b><br>Процент: %{percent}",
                        center_text     = f'<b>{projects_info["total_spheres"]}<br>всего</b>')
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.dataframe(projects_info['spheres_count'], use_container_width=True)
        
    with tab3:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Всего партнеров", projects_info['total_companies'])

        with col2:
            fig = px.bar(   projects_info['companies_types_count'], 
                            x = 'Тип компании',
                            y = 'Кол-во проектов',
                            color='Тип компании',
                            color_discrete_sequence=px.colors.sequential.RdBu)  
            st.plotly_chart(fig, use_container_width=True) 
    
    with st.container():
        st.dataframe(projects_df, use_container_width=True)

if __name__ == "__main__":
    setup.page_config(layout='wide', title='FESSBoard')
    setup.load_local_css('styles.css')
    setup.remove_footer()
    run()