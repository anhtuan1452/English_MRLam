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

from ManageClass.forms import ClassUpdateForm, LessonDetailForm, ClassForm #,, LessonForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)
from course_admin.forms import LessonDetailForm as CourseLessonDetailForm, LessonDetailFormSet as CourseLessonDetailFormSet

# Create a formset for LessonDetailForm (for class_detail view, editing dates only)
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,  # From ManageClass.forms
    fields=['date'],
    extra=0  # No extra forms, only edit existing lesson details
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

    # Lấy tất cả các buổi học của khóa học
    lessons = LESSON.objects.filter(course=class_instance.course).order_by('session_number')

    # Lấy hoặc tạo LESSON_DETAIL cho mỗi LESSON
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')
    lesson_detail_dict = {ld.lesson_id: ld for ld in lesson_details}

    # Tự động tạo LESSON_DETAIL cho các LESSON chưa có
    for lesson in lessons:
        if lesson.lesson_id not in lesson_detail_dict:
            LESSON_DETAIL.objects.create(
                lesson=lesson,
                classes=class_instance,
                date=None  # Ngày học để trống, người dùng sẽ nhập
            )

    # Lấy lại lesson_details sau khi tạo mới
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson').order_by('lesson__session_number')

    # Khởi tạo các form
    class_form = ClassUpdateForm(instance=class_instance)
    lesson_detail_formset = LessonDetailFormSet(queryset=lesson_details)

    # Zip formset với lesson_details để hiển thị
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
    submissions = SUBMISSION.objects.filter(
        userclass__classes=class_instance
    ).select_related('userclass__user', 'exercise__lessondetail__lesson')

    if not submissions:
        submissions = None

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'submissions': submissions
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

# Placeholder ClassForm (needs proper implementation)


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

def exercise_detail_view(request, class_id, exercise_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    exercise = get_object_or_404(EXERCISE, pk=exercise_id)
    submissions = SUBMISSION.objects.filter(
        exercise=exercise,
        userclass__classes=class_instance
    ).select_related('userclass__user')
    return render(request, 'exercise_detail.html', {
        'class_instance': class_instance,
        'exercise': exercise,
        'submissions': submissions,
    })

