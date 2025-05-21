from django.urls import path
from test_user.views import test_page, home_test, result_page, submit_test

urlpatterns = [
    path('home_test/<int:test_id>/', home_test, name='home_test'),
    path('test_page/<int:test_id>/', test_page, name='test_page'),
    path('result_page/<int:result_id>/', result_page, name='result_page'),
    path('test/<int:test_id>/submit/', submit_test, name='submit_test'),
]