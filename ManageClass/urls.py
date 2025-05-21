from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('add/', views.add_class, name='add_class'),
    #path('update_rollcall/', views.update_rollcall, name='update_rollcall'),
    path('<int:class_id>/', views.class_detail, name='class_detail'),
    path('manage_class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('<int:class_id>/exercises/', views.class_exercise, name='class_exercise'),
    path('<int:class_id>/rollcall/', views.class_rollcall, name='class_rollcall'),
    path('<int:class_id>/exercise/submission/<int:submission_id>/', views.exercise_detail_view, name='exercise_detail')
]