from django.contrib import admin
from django.urls import path
from english import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('materials/', views.materials, name='materials'),
    path('tests/', views.tests, name='tests'), # Thêm URL này
]
