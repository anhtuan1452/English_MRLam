from django.urls import path
from . import views

urlpatterns = [
    path('', views.materials_list, name='materials_list'),
    path('<slug:slug>/', views.materials_detail, name='materials_detail'),
]

