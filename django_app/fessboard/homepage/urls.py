from django.urls import path
from .views import index
from .views import homepage

urlpatterns = [
    path('', homepage),
    path('company-form/', index, name='company-form'),
    #path('to-form/',)
]