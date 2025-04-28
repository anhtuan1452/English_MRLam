from django.contrib import admin
from django.urls import path
from . import views
from english.views import home
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),  # Thêm URL cho đăng nhập
    path('forget-password/', views.forget_password_view, name='forget_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
]


