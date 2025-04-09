from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.qr_payment, name='qr_payment'),
    path('', views.payment_list, name='payment_list'),
    # path('test/<int:id>/', views.test_view, name='test_view')
]
