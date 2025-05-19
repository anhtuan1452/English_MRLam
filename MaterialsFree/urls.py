# MaterialsFree/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('', views.materials_list, name='materials_list'),
]
