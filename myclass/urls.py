# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('class/<int:course_id>', views.myclass, name='class'),
]
