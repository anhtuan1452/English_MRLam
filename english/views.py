from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy



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

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)  # Thực hiện đăng xuất thủ công
        messages.success(request, 'Đăng xuất thành công!')
        return HttpResponseRedirect(self.next_page)  # Chuyển hướng đến trang đăng nhập