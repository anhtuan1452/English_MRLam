from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_list, name='admin_test_list'),
    # path('test/<int:id>/', views.test_view, name='test_view'),
    path('add/', views.test_create, name='admin_test_add'),
    path('results/', views.list_result_view, name='results'),
    path('test/<int:test_id>',views.test_detail,name='admin_test_details'),
    path('result_delete/<int:result_id>/', views.result_delete, name='result_delete'),
    path('test_delete/<int:test_id>/', views.test_delete, name='test_delete'),
    path('test_edit/<int:test_id>/', views.test_edit, name='test_edit'),
]
