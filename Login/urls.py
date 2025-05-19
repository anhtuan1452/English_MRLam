from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.CustomLoginView.as_view(), name='login'),
    path('forget-password/', views.CustomPasswordResetView.as_view(), name='forget_password'),
    path('reset-password/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='reset_password'),
    path('reset-password/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]