import streamlit as st
from streamlit_elements import elements, mui, html
from types import SimpleNamespace

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from elems import Dashboard, Pie, Card

def main():
    st.title('P I Z D A')
    board = Dashboard()
    w = SimpleNamespace(
        dashboard=board,
        # Parameters: element_identifier, x_pos, y_pos, width, height, static, isDraggable, isResizable, resizeHandles
        pie=Pie(board, 6, 0, 7, 8, minW=3, minH=4),
        card=Card(board, 0, 0, 3, 8, minW=2, minH=4, isResizable=False)
    )
    with elements("kek"):
        with w.dashboard(cols={'lg': 10, 'md': 10, 'sm': 6, 'xs': 4, 'xxs': 2}, rowHeight=57):
            w.pie('')
            w.card("Илья умер в попытках познать Material UI. Его спас добрый самаритянин, который интегрировал его со стримлитом и разместил на гитхабе примеры.")
    st.title('lol kek cheburek')
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()