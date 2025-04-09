from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_list, name='class_list'),  # Đây là trang mặc định khi vào /class_admin/
    path('add/', views.add_class, name='add_class'),
    path('<int:class_id>/', views.class_detail, name='class_detail'),
]
