import streamlit as st
from streamlit_elements import elements, mui

def main():
    with elements("dashboard"):

        # You can create a draggable and resizable dashboard using
        # any element available in Streamlit Elements.

        from streamlit_elements import dashboard

        # First, build a default layout for every element you want to include in your dashboard

        layout = [
            # Parameters: element_identifier, x_pos, y_pos, width, height, [item properties...]
            dashboard.Item("first_item", 0, 0, 2, 2, isDraggable=True),
            dashboard.Item("second_item", 2, 0, 2, 2, isDraggable=True),
            dashboard.Item("third_item", 0, 2, 1, 1, isDraggable=True),
        ]

        # Next, create a dashboard layout using the 'with' syntax. It takes the layout
        # as first parameter, plus additional properties you can find in the GitHub links below.

        with dashboard.Grid(layout):
            mui.Paper("First item", key="first_item")
            mui.Paper("Second item (cannot drag)", key="second_item")
            with mui.Card(sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, key='third_item', elevation=1):
                mui.CardHeader(
                    title="Илья сошел с ума",
                    subheader="остановите его",
                    avatar=mui.Avatar("KEKW", sx={"bgcolor": "red"}),
                    action=mui.IconButton(mui.icon.MoreVert),
                    # className=self._draggable_class,
                )

                with mui.CardContent(sx={"flex": 1}):
                    mui.Typography('abobus')

                with mui.CardActions(disableSpacing=True):
                    mui.IconButton(mui.icon.Favorite)
                    mui.IconButton(mui.icon.Share)

if __name__ == "__main__":
    st.set_page_config(page_title="Илья псих", page_icon="🎈", layout="wide")
    main()