import re
import uuid
from datetime import timedelta


from django.contrib.auth import authenticate, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

from English_MRLam import settings
from english.models import USER_PROFILE
from django.db import transaction
from django.contrib.auth import authenticate, login  # Import login

def register_view(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Kiểm tra dữ liệu
        if password != password_confirm:
            messages.error(request, 'Mật khẩu và xác nhận mật khẩu không khớp.')
            return render(request, 'resgister_content.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'resgister_content.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng.')
            return render(request, 'resgister_content.html')

        try:
            # Sử dụng transaction để đảm bảo tính toàn vẹn dữ liệu
            with transaction.atomic():
                # Tạo người dùng mới
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Tạo hồ sơ người dùng (để trống các trường tùy chọn)
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
            return render(request, 'resgister_content.html')

    return render(request, 'resgister_content.html')

def login_view(request):
    if request.user.is_authenticated:
        # Nếu đã đăng nhập, chuyển hướng dựa trên vai trò
        if request.user.is_superuser:
            return redirect('user_list')  # Trang cho admin
        elif request.user.is_staff:
            return redirect('teacher_dashboard')  # Trang cho giáo viên
        else:
            return redirect('home')  # Trang khóa học cho học viên

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        login_input = request.POST.get('username')  # Trường nhập có thể là email hoặc username
        password = request.POST.get('password')

        # Kiểm tra xem login_input có phải là email hay không
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_pattern, login_input):
            # Nếu là email, tìm người dùng dựa trên email
            try:
                user = User.objects.get(email=login_input)
                username = user.username  # Lấy username để xác thực
            except User.DoesNotExist:
                messages.error(request, 'Email không tồn tại.')
                return render(request, 'login_content.html')
        else:
            # Nếu không phải email, coi login_input là username
            username = login_input

        # Xác thực người dùng với username và password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            # Chuyển hướng dựa trên vai trò
            if user.is_superuser:
                return redirect('user_list')  # Trang cho admin
            elif user.is_staff:
                return redirect('teacher_dashboard')  # Trang cho giáo viên
            else:
                return redirect('course')  # Trang khóa học cho học viên
        else:
            messages.error(request, 'Tên đăng nhập/email hoặc mật khẩu không đúng.')
    return render(request, 'login_content.html')

def forget_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Vui lòng nhập email.')
            return render(request, 'forgetpass.html')

        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())
            user.user_profile.reset_password_token = token
            user.user_profile.reset_password_expiry = timezone.now() + timedelta(hours=1)
            user.user_profile.save()

            reset_link = request.build_absolute_uri(f"/Login/reset-password/?token={token}")
            subject = "Đặt lại mật khẩu - MR. LAM"
            message = f"Chào {user.username},\n\nNhấn vào liên kết sau để đặt lại mật khẩu của bạn:\n{reset_link}\n\nLiên kết này có hiệu lực trong 1 giờ.\n\nTrân trọng,\nMR. LAM"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.')
            return redirect('forget_password')
        except User.DoesNotExist:
            messages.error(request, 'Email không tồn tại.')
            return render(request, 'forgetpass.html')
        except Exception as e:
            messages.error(request, f'Đã có lỗi xảy ra: {str(e)}')
            return render(request, 'forgetpass.html')
    return render(request, 'forgetpass.html')

def reset_password_view(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Liên kết không hợp lệ.')
        return redirect('forget_password')

    try:
        user_profile = USER_PROFILE.objects.get(
            reset_password_token=token,
            reset_password_expiry__gt=timezone.now()
        )
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            if password != password_confirm:
                messages.error(request, 'Mật khẩu và xác nhận mật khẩu không khớp.')
                return render(request, 're-password.html', {'token': token})

            if len(password) < 8:
                messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự.')
                return render(request, 're-password.html', {'token': token})

            user = user_profile.userprofile
            user.set_password(password)
            user.save()
            user_profile.reset_password_token = None
            user_profile.reset_password_expiry = None
            user_profile.save()
            messages.success(request, 'Mật khẩu đã được đặt lại thành công. Vui lòng đăng nhập.')
            return redirect('login')

        return render(request, 're-password.html', {'token': token})
    except USER_PROFILE.DoesNotExist:
        messages.error(request, 'Liên kết không hợp lệ hoặc đã hết hạn.')
        return redirect('re-password')

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')