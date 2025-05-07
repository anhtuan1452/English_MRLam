# MaterialsFree/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('', views.materials_list, name='materials_list'),
    path('<int:doc_id>/', views.materials_detail, name='materials_detail'),
]
