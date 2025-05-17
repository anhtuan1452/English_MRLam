# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from .forms import UserProfileForm, PasswordChangeCustomForm, EmailUpdateForm
from english.models import USER_CLASS

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
            if email_form.is_valid():
                user.email = email_form.cleaned_data['email']
                user.save()
                messages.success(request, "Cập nhật email thành công.")
            else:
                print("Email form errors:", email_form.errors)  # 👈 DEBUG
                messages.error(request, "Email không hợp lệ.")
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

# @login_required
# def profile_view(request):
#     active_tab = request.GET.get('tab', 'personal-info')
#
#     # Truy vấn thủ công user profile từ model
#     user_profile = USER_PROFILE.objects.get(userprofile=request.user)
#
#     # Form thông tin cá nhân
#     profile_form = ProfileForm(instance=user_profile)
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
#                 instance=user_profile
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
#             # TODO: Xử lý logic đổi email
#
#     context = {
#         'active_tab': active_tab,
#         'profile_form': profile_form,
#         'password_form': password_form,
#         'email_form': email_form,
#         'user': request.user,
#     }
#     return render(request, 'profile.html', context)
