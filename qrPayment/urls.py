from django.urls import path
from . import views

urlpatterns = [
    path('', views.qr_payment, name='qr_payment'),
    # path('test/<int:id>/', views.test_view, name='test_view')
]
