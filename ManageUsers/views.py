from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect

from english.models import USER_PROFILE, USER_CLASS
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


def user_detail(request, user_id):
    # Lấy thông tin chi tiết của người dùng
    user = get_object_or_404(User, id=user_id)

    # Lấy danh sách lớp học của người dùng
    user_classes = USER_CLASS.objects.filter(user=user)

    context = {
        'user': user,
        'user_classes': user_classes,
        'now': timezone.now()
    }
    return render(request, 'user_detail.html', context)


def user_create(request):
    if request.method == 'POST':
        # Xử lý dữ liệu form khi submit
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')

        # Tạo tài khoản mới
        account = User.objects.create(
            username=username,
            password=password,  # Trong thực tế, bạn nên mã hóa mật khẩu
            role=role
        )

        # Tạo hồ sơ người dùng
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            sex=sex,
            account=account
        )

        return redirect('user_detail', user_id=user.id)

    return render(request, 'user_create.html')



def user_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # Cập nhật USER_PROFILE
        profile = user.profile
        profile.dob = request.POST.get('dob')
        profile.sex = request.POST.get('sex')
        profile.role = request.POST.get('role')
        profile.save()

        # Cập nhật username
        new_username = request.POST.get('username')
        if new_username != user.username:
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                messages.error(request, 'Tên tài khoản đã tồn tại.')
                return render(request, 'user_edit.html', {'user': user})
            user.username = new_username

        # Cập nhật mật khẩu nếu có
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        user.save()

        messages.success(request, 'Thông tin người dùng đã được cập nhật.')
        return redirect('listuser_admin:user_detail', id=user.id)

    context = {
        'user': user
    }
    return render(request, 'user_edit.html', context)


def user_delete(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    if request.method == 'POST':
        # Xóa tài khoản sẽ tự động xóa hồ sơ người dùng do có khóa ngoại
        user.account.delete()
        return redirect('user_list')

    return redirect('user_detail', id=user_id)

