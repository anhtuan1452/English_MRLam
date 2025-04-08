# MaterialsFree/urls.py
from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.materials_list, name='list'),
    path('<int:doc_id>/', views.material_detail, name='detail'),
]