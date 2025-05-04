from django.urls import path
from . import views

urlpatterns = [
    path('qr_payment/<int:payment_id>/', views.payment_detail, name='payment_detail'),  # URL cho trang chi tiết thanh toán
    path('', views.payment_list, name='payment_list'),
    path('qr_payment/add/', views.add_payment, name='add_payment'),
]
