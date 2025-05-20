import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.forms import modelformset_factory
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)
from course_admin.forms import LessonDetailForm as CourseLessonDetailForm, \
    LessonDetailFormSet as CourseLessonDetailFormSet

# Create a formset for LessonDetailForm (for class_detail view, editing dates only)
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=0
)


def class_list(request):
    query = request.GET.get("q")
    classes = CLASS.objects.all()

    if query:
        classes = classes.filter(class_name__icontains=query)

    classes = classes.annotate(student_count=Count('user_class'))

    return render(request, 'class_list.html', {
        'classes': classes,
        'now': now().date(),
    })


def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    lessons = LESSON.objects.filter(course=class_instance.course).order_by('session_number')
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')
    lesson_detail_dict = {ld.lesson_id: ld for ld in lesson_details}

    for lesson in lessons:
        if lesson.lesson_id not in lesson_detail_dict:
            LESSON_DETAIL.objects.create(
                lesson=lesson,
                classes=class_instance,
                date=None
            )

    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by(
        'lesson__session_number')
    class_form = ClassUpdateForm(instance=class_instance)
    lesson_detail_formset = LessonDetailFormSet(queryset=lesson_details)
    zipped_form_details = zip(lesson_detail_formset.forms, lesson_details)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_class':
            class_form = ClassUpdateForm(request.POST, instance=class_instance)
            if class_form.is_valid():
                class_form.save()
                messages.success(request, "Cập nhật lớp học thành công!")
                return redirect('class_detail', class_id=class_id)
            else:
                messages.error(request, "Có lỗi khi cập nhật lớp học.")
        elif action == 'update_lesson_dates':
            lesson_detail_formset = LessonDetailFormSet(request.POST, queryset=lesson_details)
            if lesson_detail_formset.is_valid():
                lesson_detail_formset.save()
                messages.success(request, "Cập nhật ngày học thành công!")
                return redirect('class_detail', class_id=class_id)
            else:
                messages.error(request, "Có lỗi khi cập nhật ngày học.")
        elif action == 'delete_class':
            try:
                class_instance.delete()
                messages.success(request, "Xóa lớp học thành công!")
                return redirect('class_list')
            except ProtectedError:
                messages.error(request, "Không thể xóa lớp học do có dữ liệu liên quan.")

    return render(request, 'class_detail.html', {
        'class_instance': class_instance,
        'lesson_details': lesson_details,
        'lessons': lessons,
        'class_form': class_form,
        'lesson_detail_formset': lesson_detail_formset,
        'zipped_form_details': zipped_form_details,
    })


def class_exercise(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    students = USER_CLASS.objects.filter(classes=class_instance).select_related('user')
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by(
        'lesson__session_number')

    # Tổng số học viên trong lớp
    total_students = students.count()

    lesson_data = []
    for lesson_detail in lesson_details:
        exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
        student_submissions = []

        # Thống kê cho buổi học này
        submission_stats = {
            'submitted_count': 0,  # Số bài đã nộp
            'not_submitted_count': total_students,  # Số bài chưa nộp (mặc định bằng tổng số học viên)
            'checked_count': 0,  # Số bài đã chấm
            'unchecked_count': 0,  # Số bài chưa chấm
        }

        if exercise:
            # Lấy tất cả bài nộp cho bài tập này
            submissions = SUBMISSION.objects.filter(exercise=exercise)

            # Số bài đã nộp
            submitted_count = submissions.count()
            submission_stats['submitted_count'] = submitted_count

            # Số bài chưa nộp
            submission_stats['not_submitted_count'] = total_students - submitted_count

            # Số bài đã chấm (status='done')
            checked_count = submissions.filter(status='Done').count()
            submission_stats['checked_count'] = checked_count

            # Số bài chưa chấm (status='check')
            unchecked_count = submissions.filter(status='Checking').count() + submissions.filter(status='Check').count()
            submission_stats['unchecked_count'] = unchecked_count

        for student in students:
            submission = None
            if exercise:
                submission = SUBMISSION.objects.filter(
                    userclass=student,
                    exercise=exercise
                ).select_related('userclass__user').first()

            student_submissions.append({
                'student': student,
                'submission': submission,
            })

        lesson_data.append({
            'lesson_detail': lesson_detail,
            'exercise': exercise,
            'student_submissions': student_submissions,
            'submission_stats': submission_stats,  # Thêm thống kê
        })

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'lesson_data': lesson_data,
    })


def class_rollcall(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    lesson_details = LESSON_DETAIL.objects.filter(
        lesson__course=class_instance.course
    ).select_related('lesson')

    rollcall_data = []
    for lesson_detail in lesson_details:
        rollcall_users = []
        rollcall = getattr(lesson_detail, 'rollcall', None)
        if rollcall:
            rollcall_users = ROLLCALL_USER.objects.filter(
                rollcall=rollcall
            ).select_related('userclass__user')

        rollcall_data.append({
            'lesson_detail': lesson_detail,
            'rollcall_users': rollcall_users,
            'has_rollcall': rollcall is not None,
        })

    return render(request, 'class_rollcall.html', {
        'class_instance': class_instance,
        'rollcall_data': rollcall_data,
    })


def add_student_to_class(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        USER_CLASS.objects.get_or_create(user=user, classes=class_instance)
        messages.success(request, "Thêm học viên thành công!")
        return redirect('class_detail', class_id=class_id)

    users_not_in_class = User.objects.exclude(
        id__in=USER_CLASS.objects.filter(classes=class_instance).values_list('user_id', flat=True)
    )
    return render(request, 'add_student_to_class.html', {
        'class_instance': class_instance,
        'users': users_not_in_class
    })


def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm lớp học thành công!")
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})


def update_rollcall(request):
    if request.method == 'POST':
        rollcall_data = request.POST.get('rollcall_data')
        if rollcall_data:
            try:
                rollcall_data = json.loads(rollcall_data)
                for user_id, data in rollcall_data.items():
                    lesson_detail_id = data.get('lesson_detail_id')
                    status = data.get('status')
                    if not lesson_detail_id or not str(lesson_detail_id).isdigit():
                        continue
                    try:
                        lesson_detail = LESSON_DETAIL.objects.get(pk=lesson_detail_id)
                    except LESSON_DETAIL.DoesNotExist:
                        continue
                    try:
                        user = ROLLCALL_USER.objects.get(
                            userclass__user__id=user_id,
                            rollcall__lessondetail=lesson_detail
                        )
                        user.status = status
                        user.save()
                    except ROLLCALL_USER.DoesNotExist:
                        continue
                return JsonResponse({'message': 'Cập nhật trạng thái thành công!'})
            except Exception as e:
                return JsonResponse({'message': f'Lỗi xử lý dữ liệu: {str(e)}'}, status=400)
        return JsonResponse({'message': 'Dữ liệu gửi lên không hợp lệ'}, status=400)
    return JsonResponse({'message': 'Chỉ chấp nhận phương thức POST'}, status=405)


def exercise_detail_view(request, class_id, submission_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    submission = get_object_or_404(SUBMISSION, pk=submission_id, userclass__classes=class_instance)

    if request.method == 'POST':
        review = request.POST.get('review')
        action = request.POST.get('action')

        if not review:
            messages.error(request, "Vui lòng cung cấp nhận xét.")
            return redirect('exercise_detail', class_id=class_id, submission_id=submission_id)

        submission.review = review
        if action == 'redo':
            submission.status = 'Check'
            subject = f'Yêu cầu làm lại bài tập: {submission.exercise.lessondetail.lesson.lesson_name}'
            message = f"""
Kính gửi {submission.userclass.user.get_full_name},

Bài tập "{submission.exercise.lessondetail.lesson.lesson_name}" của bạn cần được làm lại. Dưới đây là nhận xét từ giáo viên:

{review}

Vui lòng nộp lại bài tập qua hệ thống trước hạn chót.

Trân trọng,
Hệ thống quản lý lớp học
"""
            messages.success(request, "Yêu cầu làm lại bài tập đã được gửi tới học viên!")
        else:  # action == 'done'
            submission.status = 'Done'
            subject = f'Nhận xét bài tập: {submission.exercise.lessondetail.lesson.lesson_name}'
            message = f"""
Kính gửi {submission.userclass.user.get_full_name},

Bài tập "{submission.exercise.lessondetail.lesson.lesson_name}" của bạn đã được chấm. Dưới đây là nhận xét từ giáo viên:

{review}

Trân trọng,
Hệ thống quản lý lớp học
"""
            messages.success(request, "Nhận xét bài tập đã được gửi tới học viên!")

        submission.save()

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[submission.userclass.user.email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Lỗi khi gửi email: {str(e)}")
            return redirect('exercise_detail', class_id=class_id, submission_id=submission_id)

        return redirect('class_exercise', class_id=class_id)

    return render(request, 'exercise_detail.html', {
        'class_instance': class_instance,
        'submission': submission,
    })