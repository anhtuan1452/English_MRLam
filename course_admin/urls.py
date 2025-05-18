from django.urls import path
from course_admin import views

urlpatterns = [
    path('ql_khoahoc/', views.admin_ql_khoahoc, name='admin_ql_khoahoc'),
    path('ql_khoahoc/<int:course_id>/', views.admin_xemkhoahoc, name='admin_xemkhoahoc'),
    path('ql_khoahoc/<int:course_id>/lesson/new/', views.add_lesson, name='add_lesson'),
    path('ql_khoahoc/them_khoahoc/', views.admin_themkhoahoc, name='admin_themkhoahoc'),
    path('ql_khoahoc/<int:course_id>/lesson/<int:lesson_id>/',views.view_lesson,name='view_lesson'),

]