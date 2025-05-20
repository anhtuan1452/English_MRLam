from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from english.models import USER_PROFILE


class CustomLoginView(LoginView):
    template_name = 'login_content.html'
    redirect_authenticated_user = True  # Tự động chuyển hướng nếu đã đăng nhập

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('user_list')  # Trang cho admin
        elif user.is_staff:
            return reverse_lazy('teacher_dashboard')  # Trang cho giáo viên
        else:
            return reverse_lazy('course')  # Trang cho học viên

    def form_invalid(self, form):
        messages.error(self.request, 'Tên đăng nhập/email hoặc mật khẩu không đúng.')
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Đăng nhập thành công!')
        return super().form_valid(form)
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'Email đã được sử dụng.')
                return render(request, 'resgister_content.html', {'form': form})

            try:
                with transaction.atomic():
                    user = form.save()  # Form tùy chỉnh đã xử lý email, first_name, last_name
                    USER_PROFILE.objects.create(
                        userprofile=user,
                        dob=None,
                        sex=None,
                        description=None,
                        image=None
                    )
                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Đã có lỗi xảy ra: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        form = CustomUserCreationForm()
    return render(request, 'resgister_content.html', {'form': form})
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView

class CustomPasswordResetView(PasswordResetView):
    template_name = 'forgetpass.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    extra_email_context = {'site_name': 'MR. LAM'}

    def form_valid(self, form):
        messages.success(self.request, 'Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Vui lòng nhập email hợp lệ.')
        return super().form_invalid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'forgetpass.html'  # Có thể tạo template riêng nếu muốn

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 're-password.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, 'Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Mật khẩu và xác nhận mật khẩu không khớp hoặc không hợp lệ.')
        return super().form_invalid(form)

from django.contrib.auth.forms import AuthenticationForm  # Thêm import này

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'login_content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AuthenticationForm(self.request)  # Thêm form đăng nhập
        return context
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Tên")
    last_name = forms.CharField(max_length=30, required=True, label="Họ")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)  # Thực hiện đăng xuất thủ công
        messages.success(request, 'Đăng xuất thành công!')
        return HttpResponseRedirect(self.next_page)  # Chuyển hướng đến trang đăng nhập