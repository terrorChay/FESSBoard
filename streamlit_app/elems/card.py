from streamlit_elements import mui
from .dashboard import Dashboard


class Card(Dashboard.Item):

    DEFAULT_CONTENT = (
        "Илья умер в попытках познать Material UI "
        "Его спас добрый самаритянин, который интегрировал его со стримлитом "
        "и разместил на гитхабе примеры."
    )

    def __call__(self, content):
        with mui.Card(key=self._key, sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, elevation=1):
            mui.CardHeader(
                title='ПЦР тесты "Просто Будущее"',
                subheader="September 14, 2016",
                avatar=mui.Avatar("R", sx={"bgcolor": "red"}),
                action=mui.IconButton(mui.icon.MoreVert),
                className=self._draggable_class,
            )
            mui.CardMedia(
                component="img",
                height=194,
                image="https://www.stomed.ru/storage/offers/photos/8/729/pcr-test-na-koronavirus-7635.jpg",
                alt="Paella dish",
            )
            
            with mui.CardContent(sx={"flex": 1}):
                mui.Typography(content)

            with mui.CardActions(disableSpacing=True):
                mui.IconButton(mui.icon.Favorite)
                mui.IconButton(mui.icon.Share)