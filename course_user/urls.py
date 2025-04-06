from django.urls import path
from course_user import views

urlpatterns = [
    path('courses/', views.courses, name='courses'),
]