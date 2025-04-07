from django.urls import path
from Login import views

urlpatterns = [
    path('SignUp/', views.SignUp, name='SignUp'),
    path('SignIn/', views.SignIn, name='SignIn'),
    path('ForgetPassword/', views.ForgetPassword, name='ForgetPassword'),
    path('RePassWord/', views.RePassWord, name='RePassWord'),
]