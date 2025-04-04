from django.contrib import admin
from django.urls import path
from english import views

urlpatterns = [
    path('quantri/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.courses, name='home'),
    path('courses/', views.courses, name='courses'),
    path('materials/', views.materials, name='materials'),
    path('tests/', views.tests, name='tests'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ql_baitest/', views.admin_ql_baitest, name='admin_ql_baitest'),
    path('ql_baitap/', views.admin_ql_baitap, name='admin_ql_baitap'),
    path('ql_lophoc/', views.admin_ql_lophoc, name='admin_ql_lophoc'),
    path('ql_nguoidung/', views.admin_ql_nguoidung, name='admin_ql_nguoidung'),
    path('ql_tailieu/', views.admin_ql_tailieu, name='admin_ql_tailieu'),
    path('ql_thanhtoan/', views.admin_ql_thanhtoan, name='admin_ql_thanhtoan'),
    path('ql_khoahoc/', views.admin_ql_khoahoc, name='admin_ql_khoahoc'),

]
