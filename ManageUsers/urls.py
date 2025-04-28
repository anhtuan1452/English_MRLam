from django.urls import path
from ManageUsers import views

urlpatterns = [
    path('user_list/', views.user_list, name='user_list'),
    path('user_edit/<int:id>/', views.user_edit, name='user_edit'),
    path('user_detail/<int:id>/', views.user_detail, name='user_detail'),
    path('user_create/', views.user_create, name='user_create'),
    path('user_delete/<int:id>/', views.user_delete, name='user_delete'),
]