
from django import forms
# from english.models import ACCOUNT
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nhập mật khẩu', 'id': 'password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lại mật khẩu', 'id': 'password_confirm'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']  # Đảm bảo đã bao gồm tất cả các trường
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên đăng nhập', 'id': 'username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email của bạn', 'id': 'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Họ', 'id': 'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên', 'id': 'last_name'}),
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp.")
        return password_confirm

from django import forms

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="Tên đăng nhập hoặc Email", max_length=100,widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tên đăng nhập hoặc Email', 'id': 'username_or_email'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        # Kiểm tra xem người dùng nhập thông tin đúng
        if not username_or_email or not password:
            raise forms.ValidationError("Vui lòng nhập đầy đủ thông tin.")

        return cleaned_data
