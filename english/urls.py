from django.contrib import admin
from django.urls import path
from english import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('materials/', views.materials, name='materials'),
    path('tests/', views.tests, name='tests'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('admin_ql_baitest/', views.admin_ql_baitest, name='admin_ql_baitest'),
    path('admin_ql_lophoc/', views.admin_ql_lophoc, name='admin_ql_lophoc'),
    path('admin_ql_nguoidung/', views.admin_ql_nguoidung, name='admin_ql_nguoidung'),
    path('admin_ql_tailieu/', views.admin_ql_tailieu, name='admin_ql_tailieu'),
    path('admin_ql_thanhtoan/', views.admin_ql_thanhtoan, name='admin_ql_thanhtoan'),
    path('admin_ql_khoahoc/', views.admin_ql_khoahoc, name='admin_ql_khoahoc'),


]
