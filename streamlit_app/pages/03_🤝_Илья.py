import streamlit as st
from streamlit_elements import elements, mui, html
from types import SimpleNamespace
import streamlit_setup as setup

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from elems import Dashboard, Pie, Card, Metric

def main():
    st.title('Илюхины гигачад метрики')
    board = Dashboard()
    w = SimpleNamespace(
        dashboard=board,
        # Parameters: element_identifier, x_pos, y_pos, width, height, static, isDraggable, isResizable, resizeHandles
        pie=Pie(board, 6, 5, 9, 8, minW=3, minH=4),
        card=Card(board, 0, 5, 3, 8, minW=2, minH=4, isResizable=False),
        metric_1=Metric(board, 0, 0, 3, 2, minW=2, minH=2),
        metric_2=Metric(board, 3, 0, 3, 2, minW=2, minH=2, isResizable=False),
        metric_3=Metric(board, 6, 0, 3, 2, minW=2, minH=2, resizeHandles=['s']),
        metric_4=Metric(board, 9, 0, 3, 2, minW=2, minH=2, isDraggable=False)
    )
    with elements("kek"):
        with w.dashboard(cols={'lg': 12, 'md': 10, 'sm': 6, 'xs': 4, 'xxs': 2}, containerPadding=[0,0], rowHeight=60):
            w.pie('')
            w.card("Илья умер в попытках познать Material UI. Его спас добрый самаритянин, который интегрировал его со стримлитом и разместил на гитхабе примеры.")
            w.metric_1("228k", "+18%", postfix='от вчерашнего', label='Можно ресайзить')
            w.metric_2(1337, "-18%", postfix='от вчерашнего', label='Нельзя ресайзить')
            w.metric_3("AVON", "Новый", postfix='клиент', label='Можно только вниз')
            w.metric_4(-666, "+18%", postfix='от прошлого месяца', label='Двигать нельзя')
    st.title('Стримлитовские метрики')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Тест', 228,'-5%')
    col2.metric('Тест', 228,'-5%')
    col3.metric('Тест', 228,'-5%')
    col4.metric('Тест', 228,'-5%')
    
if __name__ == "__main__":
    setup.page_config(layout='wide', title='FESSBoard')
    setup.remove_footer()
    main()