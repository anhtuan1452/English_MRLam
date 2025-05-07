from django.urls import path
from Profile_User import views

urlpatterns = [
    # path('', views.Profile_User, name='Profile_User'),
    path('', views.profile_view, name='Profile_User'),
]