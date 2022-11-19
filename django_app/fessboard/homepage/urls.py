from django.urls import path
from .views import *
urlpatterns = [
    path('', homepage),
    path('company-form/', company_view, name='company-form'),
    path('student-form/', student_view, name='student-form'),
    path('universities-form/', student_view, name='universities-form'),
    path('teachers-form/', student_view, name='teachers-form'),
    path('events-form/', student_view, name='events-form'),
    path('projects-form/', student_view, name='projects-form'),

    #path('to-form/',)
]