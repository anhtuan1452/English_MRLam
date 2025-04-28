"""
URL configuration for English_MRLam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('english/', include('english.urls')),
    path('', include('Login.urls')),
    path('Profile/', include('Profile_User.urls')),
    path('exercise_admin/', include('exercise_admin.urls')),
    path('course_user/', include('course_user.urls')),
    path('test_admin/',include('test_admin.urls')),
    path('listuser_admin/',include('ManageUsers.urls')),
    path('test_user/',include('test_user.urls')),
    path('MyClass/',include('MyClass.urls')),
    path('course_admin/',include('course_admin.urls')),
    path('registercourse/',include('registerCourse.urls')),
    path('class_admin/',include('ManageClass.urls')),
    path('materials/',include('MaterialsFree.urls')),
    path('manage_class/',include('ManageClass.urls')),
    path('document_management/',include('DocumentManagement.urls')),
    path('qr_payment/',include('qrPayment.urls')),
    path('course_admin/',include('course_admin.urls')),
]
