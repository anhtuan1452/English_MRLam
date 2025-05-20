from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_list, name='admin_test_list'),
    path('add/', views.test_add_view, name='admin_test_add'),
    path('results/', views.list_result_view, name='results'),
    path('test/<int:test_id>',views.test_detail_view,name='admin_test_details'),
    path('result_delete/<int:result_id>/', views.result_delete, name='result_delete'),
    path('test_delete/<int:test_id>/', views.test_delete, name='test_delete'),
    path('test_edit/<int:test_id>/', views.test_edit_view, name='test_edit'),
]
