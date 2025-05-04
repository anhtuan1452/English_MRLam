from django.urls import path
from exercise_admin import views

urlpatterns = [
    path('ql_baitap/', views.admin_ql_baitap, name='admin_ql_baitap'),
    path('ql_baitap/thembt/', views.them_baitap, name='them_baitap'),
    path('ql_baitap/xembt/<int:lesson_id>/', views.xem_baitap, name='xem_baitap'),
    path('ql_baitap/xembt/<int:lesson_id>/edit/', views.sua_baitap, name='sua_baitap'),
    path('ql_baitap/xoa_baitap/<int:lesson_id>/', views.xoa_baitap, name='xoa_baitap'),
    path('ql_baitap/xembt/<int:lesson_id>/sua/', views.sua_baitap_xem, name='sua_baitap_xem'),
]