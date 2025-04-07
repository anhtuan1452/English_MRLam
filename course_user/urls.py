from django.urls import path
from course_user import views

urlpatterns = [
    path('courses/', views.course, name='course'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
]