from django.urls import path
from . import views

urlpatterns = [
    path('payment/start/<int:course_id>/', views.start_payment, name='start_payment'),
    path('payment/qr/<int:paymentinfo_id>/', views.qr_code_view, name='qr_code_view'),
    path('payment/success/<int:paymentinfo_id>/', views.payment_success, name='payment_success'),
]
