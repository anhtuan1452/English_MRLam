# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('class/<int:course_id>', views.MyClass, name='class'),
    path('homework/', views.student_homework, name='student_homework'),
    path('submission/<int:lesson_id>/', views.student_submission, name='student_submission'),
]
