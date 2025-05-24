
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
import logging, datetime

from .forms import UserProfileForm, PasswordChangeCustomForm, EmailUpdateForm
from english.models import USER_CLASS, LESSON_DETAIL, EXERCISE, SUBMISSION
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


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

            # An toàn hơn khi lấy tên
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)

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
                logger.warning("Password form errors: %s", password_form.errors)
                messages.error(request, "Lỗi khi đổi mật khẩu.")
            active_tab = 'password'

        elif 'email-submit' in request.POST:
            email_form = EmailUpdateForm(request.POST)
            session_key = 'email_verification_data'
            if email_form.is_valid():
                new_email = email_form.cleaned_data['email']
                # Kiểm tra trùng email
                if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                    messages.error(request, "Email này đã được sử dụng.")
                else:
                    verification_code = str(random.randint(100000, 999999))
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
                    user.email = session_data.get('email')
                    user.save()
                    del request.session[session_key]
                    messages.success(request, 'Email đã được cập nhật thành công.')
                else:
                    messages.error(request, 'Mã xác nhận không đúng.')
            active_tab = 'email'

    # Lấy danh sách lớp và bài tập đã nộp
    enrolled_classes = USER_CLASS.objects.filter(user=user).select_related('classes')
    class_exercises = []

    for uc in enrolled_classes:
        lessons = LESSON_DETAIL.objects.filter(classes=uc.classes).select_related('lesson')
        lesson_info = []
        for lesson in lessons:
            try:
                exercise = EXERCISE.objects.get(lessondetail=lesson)
                submission = SUBMISSION.objects.filter(userclass=uc, exercise=exercise).first()
                lesson_date = lesson.date
                lesson_file_exists = bool(lesson.lesson.exercise_file)

                if not lesson_file_exists:
                    status = "Chưa có file bài tập"
                else:
                    if submission and submission.submission_file_content:
                        if lesson_date and submission.submit_date.date() <= lesson_date:
                            status = "Đã nộp"
                        elif lesson_date:
                            status = "Nộp trễ"
                        else:
                            status = "Đã nộp"
                    else:
                        if lesson_date and lesson_date < datetime.date.today():
                            status = "Quá hạn"
                        else:
                            status = "Chưa nộp"

                lesson_info.append({
                    'lesson_name': lesson.lesson.lesson_name,
                    'date': lesson.date,
                    'exercise': exercise,
                    'status': status
                })

            except EXERCISE.DoesNotExist:
                # Nếu không có bài tập liên kết
                lesson_info.append({
                    'lesson_name': lesson.lesson.lesson_name,
                    'date': lesson.date,
                    'exercise': None,
                    'status': "Chưa có bài tập"
                })

        # for lesson in lessons:
        #     try:
        #         exercise = EXERCISE.objects.get(lessondetail=lesson)
        #         submission = SUBMISSION.objects.filter(userclass=uc, exercise=exercise).first()
        #         lesson_date = lesson.date
        #
        #         if submission and submission.submission_file_content:
        #             if lesson_date and submission.submit_date.date() <= lesson_date:
        #                 status = "Đã nộp"
        #             elif lesson_date:
        #                 status = "Nộp trễ"
        #             else:
        #                 status = "Đã nộp"
        #         else:
        #             if lesson_date and lesson_date < datetime.date.today():
        #                 status = "Quá hạn"
        #             else:
        #                 status = "Chưa nộp"
        #
        #         lesson_info.append({
        #             'lesson_name': lesson.lesson.lesson_name,
        #             'date': lesson.date,
        #             'exercise': exercise,
        #             'status': status
        #         })
        #     except EXERCISE.DoesNotExist:
        #         continue

        class_exercises.append({
            'class': uc.classes,
            'lessons': lesson_info
        })

    return render(request, 'profile.html', {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
        'email_form': email_form,
        'enrolled_classes': [uc.classes for uc in enrolled_classes],
        'class_exercises': class_exercises,
        'active_tab': active_tab,
    })




