# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from .forms import UserProfileForm, PasswordChangeCustomForm, EmailUpdateForm
from english.models import USER_CLASS
import random
from django.core.mail import send_mail
from django.conf import settings
from django import forms



@login_required
def profile_view(request):
    user = request.user
    user_profile = user.profile
    active_tab = request.GET.get('active_tab', 'personal-info')

    profile_form = UserProfileForm(instance=user_profile)
    password_form = PasswordChangeCustomForm(user)
    email_form = EmailUpdateForm(initial={'email': user.email})

    if request.method == 'POST':
        if 'personal-info-submit' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            if profile_form.is_valid():
                user.save()
                profile_form.save()
                messages.success(request, "Đã cập nhật thông tin cá nhân.")
            else:
                messages.error(request, "Lỗi khi cập nhật thông tin.")
            active_tab = 'personal-info'

        elif 'password-submit' in request.POST:
            password_form = PasswordChangeCustomForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Đổi mật khẩu thành công.")
            else:
                print("Password form errors:", password_form.errors)  # 👈 DEBUG
                messages.error(request, "Lỗi khi đổi mật khẩu.")
            active_tab = 'password'


        elif 'email-submit' in request.POST:
            email_form = EmailUpdateForm(request.POST)
            session_key = 'email_verification_data'
            if email_form.is_valid():
                new_email = email_form.cleaned_data['email']
                verification_code = str(random.randint(100000, 999999))
                # Gửi mã xác nhận
                send_mail(
                    subject='Mã xác nhận thay đổi email',
                    message=f'Mã xác nhận của bạn là: {verification_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[new_email],
                )

                request.session[session_key] = {
                    'email': new_email,
                    'code': verification_code
                }
                messages.success(request, f'Mã xác nhận đã được gửi tới {new_email}.')
            else:
                messages.error(request, 'Email không hợp lệ.')
            active_tab = 'email'

        elif 'verify-email-submit' in request.POST:
            email_form = EmailUpdateForm(request.POST)
            session_key = 'email_verification_data'
            if email_form.is_valid():
                user_code = email_form.cleaned_data.get('verification_code')
                session_data = request.session.get(session_key)
                if session_data and user_code == session_data.get('code'):
                    request.user.email = session_data.get('email')
                    request.user.save()
                    del request.session[session_key]
                    messages.success(request, 'Email đã được cập nhật thành công.')
                else:
                    messages.error(request, 'Mã xác nhận không đúng.')
            active_tab = 'email'
    enrolled_classes = USER_CLASS.objects.filter(user=user).select_related('classes')

    return render(request, 'profile.html', {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
        'email_form': email_form,
        'enrolled_classes': [uc.classes for uc in enrolled_classes],
        'active_tab': active_tab,
    })




