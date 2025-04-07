from django.urls import path
from course_admin import views

urlpatterns = [
    path('ql_khoahoc/', views.admin_ql_khoahoc, name='admin_ql_khoahoc'),
    path('ql_khoahoc/khoa1/', views.admin_xemkhoahoc, name='admin_xemkhoahoc'),
    path('ql_khoahoc/khoa1/add_lesson_detail', views.add_lesson_detail, name='add_lesson_detail'),
]