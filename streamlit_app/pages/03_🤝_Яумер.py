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
        pie=Pie(board, 6, 0, 6, 8, minW=3, minH=4),
        card=Card(board, 0, 0, 3, 8, minW=2, minH=4, isResizable=False)
    )
    with elements("kek"):
        DEFAULT_DATA = [
            { "id": "Илюха", "label": "Илюха", "value": 465, "color": "hsl(128, 70%, 50%)" },
            { "id": "Миша", "label": "Миша", "value": 140, "color": "hsl(178, 70%, 50%)" },
            { "id": "Иванов", "label": "Иванов", "value": 40, "color": "hsl(322, 70%, 50%)" },
            { "id": "Тот парень", "label": "Он самый", "value": 439, "color": "hsl(117, 70%, 50%)" },
            { "id": "Не Илья", "label": "не Илья", "value": 366, "color": "hsl(286, 70%, 50%)" }
        ]
        with w.dashboard(rowHeight=57):
            w.pie(DEFAULT_DATA)
            w.card("Илья умер в попытках познать Material UI. Его спас добрый самаритянин, который интегрировал его со стримлитом и разместил на гитхабе примеры.")

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()