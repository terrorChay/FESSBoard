from django.urls import path
from .views import *


urlpatterns = [
    path('', homepage),
    path('company-form/', index, name='company-form'),
    path('event-form/', Render_EventsForm, name='event-form'),
    path('uni-form/', Render_UniForm, name='uni-form'),
    path('project-form/', Render_ComplexProject, name='project-form'),
    path('xproject-form/', MultipleRender, name='xproject-form'),
    path('teacher-form/', Render_TeachersInProjectForm, name='teacher-form'),

]
