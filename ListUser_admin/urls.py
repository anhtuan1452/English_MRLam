from django.urls import path
from ListUser_admin import views

urlpatterns = [
    path('user_list/', views.user_list, name='user_list'),
    path('user_edit/', views.user_edit, name='user_edit'),
    path('user_detail/', views.user_detail, name='user_detail'),
    path('user_create/', views.user_create, name='user_create'),
]