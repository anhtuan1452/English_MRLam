# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('class/<int:course_id>', views.MyClass, name='class'),
    path('class/', views.student_class, name='student_class'),
    path('class/<int:class_id>/', views.student_homework, name='student_homework'),
    path('submission/<int:class_id>/<int:lesson_id>/', views.student_submission, name='student_submission'),
    path('submission/download/<int:submission_id>/', views.download_submission, name='download_submission')
]