from django.contrib import admin
from django.urls import path
from english import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('materials/', views.materials, name='materials'),
    path('tests/', views.tests, name='tests'), # Thêm URL này
    path('course_user/courses/search/', views.search_courses, name='search_courses'),
    path('materials/search/', views.search_materials, name='search_materials'),
    path('admin/', admin.site.urls)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
