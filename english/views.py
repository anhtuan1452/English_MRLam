from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def materials(request):
    return render(request, 'materials.html')

def tests(request):
    return render(request, 'tests.html')

def classes(request):
    return render(request, 'classes.html')

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


