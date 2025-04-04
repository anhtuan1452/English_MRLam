from django.contrib import admin
from django.urls import path
from english import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.courses, name='home'),
    path('courses/', views.courses, name='courses'),
    path('materials/', views.materials, name='materials'),
    path('tests/', views.tests, name='tests'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
]
