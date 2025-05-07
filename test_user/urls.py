from django.urls import path
from test_user.views import test_page, home_test

urlpatterns = [
    path('home_test/<int:test_id>/', home_test, name='home_test'),
    path('test_page/<int:test_id>/', test_page, name='test_page'),
]