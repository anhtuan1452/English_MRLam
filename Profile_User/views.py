from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm, CustomPasswordChangeForm, EmailChangeForm
from django.contrib.auth import update_session_auth_hash

from english.models import USER_PROFILE
#
#
# @login_required
# def profile_view(request):
#     # Xử lý tab active
#     active_tab = request.GET.get('tab', 'personal-info')
#
#     user_profile = USER_PROFILE.objects.get(userprofile=request.user)
#     # Form thông tin cá nhân
#     profile_form = ProfileForm(instance=request.user.userprofile)
#
#     # Form đổi mật khẩu
#     password_form = CustomPasswordChangeForm(request.user)
#
#     # Form đổi email
#     email_form = EmailChangeForm()
#
#     if request.method == 'POST':
#         if 'personal-info-submit' in request.POST:
#             profile_form = ProfileForm(
#                 request.POST,
#                 request.FILES,
#                 instance=request.user.userprofile
#             )
#             if profile_form.is_valid():
#                 profile_form.save()
#                 messages.success(request, 'Thông tin cá nhân đã được cập nhật!')
#                 return redirect('profile')
#
#         elif 'password-submit' in request.POST:
#             password_form = CustomPasswordChangeForm(request.user, request.POST)
#             if password_form.is_valid():
#                 user = password_form.save()
#                 update_session_auth_hash(request, user)
#                 messages.success(request, 'Mật khẩu đã được thay đổi thành công!')
#                 return redirect('profile?tab=password')
#
#         elif 'email-submit' in request.POST:
#             email_form = EmailChangeForm(request.POST)
#             # Xử lý logic đổi email ở đây
#
#     context = {
#         'active_tab': active_tab,
#         'profile_form': profile_form,
#         'password_form': password_form,
#         'email_form': email_form,
#         'user': request.user,
#     }
#     return render(request, 'profile.html', context)
# # from django.shortcuts import render
# # def Profile_User(request):
# #     return render(request, 'backup.html')

# from .models import USER_PROFILE

@login_required
def profile_view(request):
    active_tab = request.GET.get('tab', 'personal-info')

    # Truy vấn thủ công user profile từ model
    user_profile = USER_PROFILE.objects.get(userprofile=request.user)

    # Form thông tin cá nhân
    profile_form = ProfileForm(instance=user_profile)

    # Form đổi mật khẩu
    password_form = CustomPasswordChangeForm(request.user)

    # Form đổi email
    email_form = EmailChangeForm()

    if request.method == 'POST':
        if 'personal-info-submit' in request.POST:
            profile_form = ProfileForm(
                request.POST,
                request.FILES,
                instance=user_profile
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Thông tin cá nhân đã được cập nhật!')
                return redirect('profile')

        elif 'password-submit' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Mật khẩu đã được thay đổi thành công!')
                return redirect('profile?tab=password')

        elif 'email-submit' in request.POST:
            email_form = EmailChangeForm(request.POST)
            # TODO: Xử lý logic đổi email

    context = {
        'active_tab': active_tab,
        'profile_form': profile_form,
        'password_form': password_form,
        'email_form': email_form,
        'user': request.user,
    }
    return render(request, 'profile.html', context)
