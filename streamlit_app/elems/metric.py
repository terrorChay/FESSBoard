from streamlit_elements import mui
from .dashboard import Dashboard


class Metric(Dashboard.Item):

    DEFAULT_LABEL       = ('Моя метрика')
    DEFAULT_VALUE       = ('1337')

    def __call__(self, value, delta='', postfix='', label=DEFAULT_LABEL):
        with mui.Paper(key=self._key, sx={
                                    "font-family":"Roboto, Helvetica, Arial, sans-serif",
                                    "display": "flex",
                                    "flexDirection":"column", 
                                    "justify-content":"space-between",
                                    "borderRadius": 3, 
                                    "padding": "16px", 
                                    "overflow": "hidden"}, elevation=1, className=self._draggable_class):

            mui.Typography(label, sx={"letter-spacing":"-0.04px"})
            mui.Typography(value, sx={"fontSize":34, "fontWeight":600})
            with mui.Box(sx={"display":"flex", "align-items":"center"}):
                if "-" in list(delta):
                    delta_color = 'error.dark'
                else:
                    delta_color = 'success.dark'
                mui.Typography(delta, sx={"fontSize":11, "letter-spacing":"0.33px", "color":delta_color, "fontWeight":600, "margin-right":"4px"})
                mui.Typography(postfix, sx={"fontSize":11, "letter-spacing":"0.33px", "fontWeight":400, "opacity":"0.8"})