# DocumentManagement/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('add/', views.add_document, name='add_document'),
    path('documents/<int:lesson_id>/', views.document_detail_edit, name='document_detail_edit'),

]