from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from english.models import COURSE, DOCUMENT

def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=''
    )(view_func)
def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=''
    )(view_func)
def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()
def is_student(user):
    return user.groups.filter(name='Student').exists()
def is_admin(user):
    return user.groups.filter(name='Admin').exists()
def is_staff(user):
    return user.groups.filter(name__in=['Admin', 'Teacher']).exists()


# Create your views here.
def home(request):
    return render(request, 'home.html')

def materials(request):
    return render(request, 'materials.html')

def tests(request):
    return render(request, 'tests.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def admin_ql_baitest(request):
    return render(request, 'ql_baitest.html')

def admin_ql_lophoc(request):
    return render(request, 'ql_lophoc.html')

def admin_ql_nguoidung(request):
    return render(request, 'ql_nguoidung.html')

def admin_ql_tailieu(request):
    return render(request, 'ql_tailieu.html')

def admin_ql_thanhtoan(request):
    return render(request, 'ql_thanhtoan.html')

def admin_ql_khoahoc(request):
    return render(request, 'ql_khoahoc.html')

def search_courses(request):
    query = request.GET.get('q', '')
    courses = []

    if query:
        # Ví dụ tìm kiếm tên trong Course hoặc Material
        courses = COURSE.objects.filter(course_name__icontains=query)

    context = {
        'query': query,
        'courses': courses,
    }
    return render(request, 'search_courses.html', context)


def search_materials(request):
    query = request.GET.get('q', '')
    materials = []

    if query:
        materials = DOCUMENT.objects.filter(doc_name__icontains=query)

    context = {
        'query': query,
        'materials': materials,
    }
    return render(request, 'search_materials.html', context)

def page_not_found(request, exception):
    return render(request, '404.html', {
        'message': 'Trang bạn tìm kiếm không tồn tại. Vui lòng kiểm tra lại URL hoặc quay lại trang chính.'
    }, status=404)