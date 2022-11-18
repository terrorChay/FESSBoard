from django.urls import path
from .views import *


urlpatterns = [
    path('', homepage),
    path('company-form/', index, name='company-form'),
    path('event-form/', Render_EventsForm, name='event-form'),
    path('uni-form/', Render_UniForm, name='uni-form'),
]
