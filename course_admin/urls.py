from django.urls import path
from course_admin import views

urlpatterns = [
    path('ql_khoahoc/', views.admin_ql_khoahoc, name='admin_ql_khoahoc'),
    path('ql_khoahoc/<int:course_id>/', views.admin_xemkhoahoc, name='admin_xemkhoahoc'),
    path('ql_khoahoc/<int:course_id>/lesson/new/', views.add_lesson_detail, name='add_lesson_detail'),
    path('ql_khoahoc/them_khoahoc/', views.admin_themkhoahoc, name='admin_themkhoahoc'),
    path('ql_khoahoc/<int:course_id>/lesson/<int:lesson_detail_id>/',views.view_lesson_detail,name='view_lesson_detail'),

]