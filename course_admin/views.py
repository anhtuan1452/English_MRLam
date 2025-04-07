from django.shortcuts import render

# Create your views here.
def admin_ql_khoahoc(request):
    return render(request, 'course_admin_home.html')
def admin_xemkhoahoc(request):
    return render(request, 'course_detail.html')
def add_lesson_detail(request):
    return render(request, 'lesson_admin_detail.html')