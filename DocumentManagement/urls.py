from django.urls import path
from . import views
urlpatterns = [
    # Danh sách tài liệu
    path('', views.document_list, name='document_list'),

    # Chi tiết tài liệu
    path('chi-tiet/<int:document_id>/', views.document_detail, name='document_detail'),

    # Thêm tài liệu mới
    path('them/', views.add_document, name='add_document'),

    # Sửa tài liệu
    path('sua/<int:document_id>/', views.edit_document, name='edit_document'),

    # Xóa tài liệu
    path('xoa/<int:document_id>/', views.delete_document, name='delete_document'),
]

