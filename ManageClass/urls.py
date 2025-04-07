# ManageClass/urls.py
from django.urls import path
from . import views

app_name = 'ManageClass'

urlpatterns = [
    path('', views.DanhSachLopHocView.as_view(), name='danh_sach_lop'),
    path('them/', views.them_lop_hoc_view, name='them_lop_hoc'),
    path('chi-tiet/<int:lop_id>/', views.chi_tiet_lop_hoc, name='chi_tiet_lop_hoc'),
    path('cap-nhat/<int:pk>/', views.CapNhatLopHocView.as_view(), name='cap_nhat_lop_hoc'),
    path('xoa/<int:lop_id>/', views.xoa_lop_hoc, name='xoa_lop_hoc'),
    path('xoa-ajax/<int:lop_id>/', views.xoa_lop_hoc_ajax, name='xoa_lop_hoc_ajax'),
]