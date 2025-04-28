from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from english.models import USER_PROFILE, USER_CLASS,CLASS
from django.contrib.auth.models import User

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q


def user_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        # Tìm kiếm theo first_name hoặc last_name
        users = User.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    else:
        # Lấy tất cả người dùng
        users = User.objects.all()

    context = {
        'users': users,
        'search_query': search_query
    }
    return render(request, 'user_list.html', context)

def user_detail(request, id):
    # Lấy thông tin chi tiết của người dùng
    user = get_object_or_404(User, id=id)
    user_profile = get_object_or_404(USER_PROFILE, userprofile_id=user)
    # Lấy danh sách lớp học của người dùng
    user_classes = USER_CLASS.objects.filter(user_id=user.id)
    context = {
        'user': user,
        'user_classes': user_classes,
        'now': timezone.now(),
        'user_profile' : user_profile,
    }
    return render(request, 'user_detail.html', context)


from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render


def user_create(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            # Username already exists, add error message
            messages.error(request, f"Tên đăng nhập '{username}' đã tồn tại. Vui lòng chọn tên đăng nhập khác.")
            # Return to the form with the submitted data (except password)
            context = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                # Include any other fields you want to preserve
            }
            return render(request, 'user_create.html', context)

        # Create the user with Django's User model
        try:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=make_password(password)
            )

            # Set user permissions based on role
            if role == 'admin':
                user.is_superuser = True
                user.is_staff = True
            elif role == 'teacher':
                user.is_staff = True

            user.save()

            # If you have additional user profile info (dob, sex)
            if hasattr(user, 'USER_PROFILE'):
                profile = user.USER_PROFILE
            else:
                # Create a new profile if it doesn't exist
                profile = USER_PROFILE(user=user)

            # Update profile fields
            profile.dob = request.POST.get('dob')
            profile.sex = request.POST.get('sex')
            profile.save()

            # Add success message
            messages.success(request, f"Tài khoản '{username}' đã được tạo thành công!")

            # Redirect to user detail view
            return redirect('user_detail', user_id=user.id)

        except Exception as e:
            # Handle other potential errors
            messages.error(request, f"Lỗi khi tạo tài khoản: {str(e)}")
            return render(request, 'user_create.html')

    # For GET requests, just show the empty form
    return render(request, 'user_create.html')
def user_edit(request, id):
    # Lấy đối tượng từ auth_user
    user = get_object_or_404(User, id=id)
    # Lấy đối tượng từ USER_PROFILE (liên kết với user qua trường account)
    user_profile = get_object_or_404(USER_PROFILE, userprofile_id=user)

    if request.method == 'POST':
        # Cập nhật thông tin cho auth_user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # Cập nhật thông tin cho USER_PROFILE
        user_profile.dob = request.POST.get('dob')
        user_profile.sex = request.POST.get('sex')
        user_profile.save()

        # Cập nhật thông tin tài khoản (username, password, role)
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)  # Mã hóa mật khẩu
        user.username = request.POST.get('username')

        # Cập nhật role (nếu role là trường tùy chỉnh trong USER_PROFILE)
        user_profile.role = request.POST.get('role')
        user_profile.save()

        return redirect('user_detail', id=user.id)

    context = {
        'user': user,
        'user_profile': user_profile,  # Truyền cả user_profile vào template
    }
    return render(request, 'user_edit.html', context)

def user_delete(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return redirect('user_detail', user_id=user.id)

