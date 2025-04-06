from django.urls import path
from exercise_admin import views

urlpatterns = [
    path('ql_baitap/', views.admin_ql_baitap, name='admin_ql_baitap'),
    path('ql_baitap/thembt/', views.them_baitap, name='them_baitap'),
]